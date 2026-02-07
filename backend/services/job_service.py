from datetime import datetime
from typing import Optional
from models.job import JobStatus, VideoJobRequest
from services.vertex_service import VertexService
from utils.env import settings
import uuid
import asyncio
import traceback


class JobService:
    def __init__(self, vertex_service: VertexService):
        self.vertex_service = vertex_service
        # In-memory job storage
        self.jobs: dict[str, dict] = {}

        # Cloud Tasks client (only init if in production mode)
        self.cloud_tasks = None
        if settings.WORKER_SERVICE_URL:
            from services.cloud_tasks_service import CloudTasksService
            self.cloud_tasks = CloudTasksService()

    async def create_video_job(self, request: VideoJobRequest) -> str:
        """Create a video job - uses Cloud Tasks in prod, asyncio locally"""
        job_id = str(uuid.uuid4())

        # Store pending job
        self.jobs[job_id] = {
            "status": "pending",
            "job_start_time": datetime.now().isoformat(),
        }

        job_data = {
            "title": request.title,
            "caption": request.caption,
            "duration_seconds": request.duration_seconds
        }

        if self.cloud_tasks:
            # Production: enqueue to Cloud Tasks
            self.cloud_tasks.enqueue_video_job(job_id, job_data)
        else:
            # Local: use asyncio background task
            asyncio.create_task(self.process_video_job(job_id, job_data))

        return job_id

    async def process_video_job(self, job_id: str, job_data: dict):
        """Process video generation - called by worker or asyncio"""
        try:
            title = job_data["title"]
            caption = job_data["caption"]
            duration = job_data.get("duration_seconds", 6)

            # Step 1: Generate start frame from title + caption
            start_frame = await self.vertex_service.generate_image_content(
                title=title,
                caption=caption
            )

            # Step 2: Generate video from start frame
            prompt = f"{title}\n{caption}"
            operation = await self.vertex_service.generate_video_content(
                prompt=prompt,
                image_data=start_frame,
                duration_seconds=duration
            )

            # Store operation name for polling
            self.jobs[job_id] = {
                "status": "processing",
                "operation_name": operation.name,
                "job_start_time": datetime.now().isoformat(),
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
                )

            return JobStatus(
                status="waiting",
                job_start_time=job_start_time,
            )

        return None

    def update_job(self, job_id: str, data: dict):
        """Update job data (used by worker)"""
        if job_id in self.jobs:
            self.jobs[job_id].update(data)
        else:
            self.jobs[job_id] = data
