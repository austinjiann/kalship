from datetime import datetime
from typing import Optional
from models.job import JobStatus, VideoJobRequest
from services.vertex_service import VertexService
from utils.veo_prompt_builder import create_video_prompt
import uuid
import asyncio
import traceback


class JobService:
    def __init__(self, vertex_service: VertexService):
        self.vertex_service = vertex_service
        # In-memory job storage
        self.jobs: dict[str, dict] = {}
        self.current_image: bytes | None = None

    async def create_video_job(self, request: VideoJobRequest) -> str:
        job_id = str(uuid.uuid4())

        # Store pending job before starting background task
        self.jobs[job_id] = {
            "status": "pending",
            "job_start_time": datetime.now().isoformat()
        }

        # Start background task
        asyncio.create_task(self._process_video_job(job_id, request))

        return job_id

    async def _process_video_job(self, job_id: str, request: VideoJobRequest):
        """Background task that processes the video generation"""
        try:
            # Parallel tasks
            tasks = [
                self.vertex_service.analyze_image_content(
                    prompt="Describe any animation annotations you see. Use this description to inform a video director. Be descriptive about location and purpose of the annotations.",
                    image_data=request.starting_image
                ),
                self.vertex_service.generate_image_content(
                    title="Remove all text, captions, subtitles, annotations from this image.",
                    caption="Generate a clean version of the image with no text. Keep everything else the exact same.",
                    image=request.starting_image
                )
            ]

            if request.ending_image:
                tasks.append(
                    self.vertex_service.generate_image_content(
                        title="Remove all text, captions, subtitles, annotations from this image.",
                        caption="Generate a clean version of the image with no text. Keep the art/image style the exact same.",
                        image=request.ending_image
                    )
                )

            results = await asyncio.gather(*tasks)
            annotation_description = results[0]
            starting_frame = results[1]
            ending_frame = results[2] if len(results) > 2 else None

            operation = await self.vertex_service.generate_video_content(
                create_video_prompt(request.custom_prompt, request.global_context, annotation_description),
                starting_frame,
                ending_frame,
                request.duration_seconds
            )

            # Store operation name for polling
            self.jobs[job_id] = {
                "status": "processing",
                "operation_name": operation.name,
                "job_start_time": datetime.now().isoformat(),
                "metadata": {"annotation_description": annotation_description}
            }

        except Exception as e:
            print(f"Error processing video job {job_id}: {e}")
            traceback.print_exc()
            self.jobs[job_id] = {
                "status": "error",
                "error": str(e),
                "job_start_time": datetime.now().isoformat()
            }

    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Poll job status - checks Vertex AI if processing"""
        job = self.jobs.get(job_id)

        if job is None:
            return None

        status = job.get("status")
        job_start_time = datetime.fromisoformat(job["job_start_time"]) if job.get("job_start_time") else None

        # Pending - still setting up
        if status == "pending":
            return JobStatus(status="waiting", job_start_time=job_start_time)

        # Error
        if status == "error":
            return JobStatus(
                status="error",
                job_start_time=job_start_time,
                error=job.get("error")
            )

        # Done - return cached result
        if status == "done":
            return JobStatus(
                status="done",
                job_start_time=job_start_time,
                video_url=job.get("video_url"),
                metadata=job.get("metadata")
            )

        # Processing - poll Vertex AI
        if status == "processing" and job.get("operation_name"):
            result = await self.vertex_service.get_video_status_by_name(job["operation_name"])

            if result.status == "done":
                video_url = result.video_url.replace("gs://", "https://storage.googleapis.com/") if result.video_url else None
                # Cache the result
                self.jobs[job_id]["status"] = "done"
                self.jobs[job_id]["video_url"] = video_url

                return JobStatus(
                    status="done",
                    job_start_time=job_start_time,
                    video_url=video_url,
                    metadata=job.get("metadata")
                )

            return JobStatus(
                status="waiting",
                job_start_time=job_start_time,
                metadata=job.get("metadata")
            )

        return None

    # Image generation helpers
    async def generate_image(
        self,
        title: str,
        caption: str,
        additional: str | None = None
    ) -> bytes:
        """Generate image, using previous image if available (image-to-image)"""
        result = await self.vertex_service.generate_image_content(
            title=title,
            caption=caption,
            additional=additional,
            image=self.current_image
        )
        self.current_image = result
        return result

    def reset_image_state(self):
        self.current_image = None

    def has_image(self) -> bool:
        return self.current_image is not None
