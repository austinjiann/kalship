import asyncio
import json
import traceback
import uuid
from datetime import datetime
from typing import Optional

from google.cloud import storage

from models.job import JobStatus, VideoJobRequest
from services.vertex_service import VertexService
from utils.env import settings
from utils.gemini_prompt_builder import (
    create_first_image_prompt,
    create_second_image_prompt,
)
from utils.veo_prompt_builder import create_video_prompt


class JobService:
    def __init__(self, vertex_service: VertexService):
        self.vertex_service = vertex_service
        self.jobs: dict[str, dict] = {}

        self.local_queue: asyncio.Queue[dict] = asyncio.Queue()
        self.local_worker_task: asyncio.Task | None = None

        self.cloud_tasks = None
        if settings.WORKER_SERVICE_URL:
            from services.cloud_tasks_service import CloudTasksService

            self.cloud_tasks = CloudTasksService()

        self.storage_client: storage.Client | None = None
        self.bucket = None
        if settings.GOOGLE_CLOUD_BUCKET_NAME:
            try:
                self.storage_client = storage.Client(
                    project=settings.GOOGLE_CLOUD_PROJECT or None
                )
                self.bucket = self.storage_client.bucket(settings.GOOGLE_CLOUD_BUCKET_NAME)
            except Exception as exc:
                print(f"Failed to initialize GCS job persistence: {exc}")

    def _job_blob_path(self, job_id: str) -> str:
        return f"jobs/{job_id}.json"

    def _parse_timestamp(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    def _to_public_url(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        if value.startswith("gs://"):
            return f"https://storage.googleapis.com/{value[len('gs://'):]}"
        return value

    def _download_job_sync(self, job_id: str) -> Optional[dict]:
        if not self.bucket or not self.storage_client:
            return None

        blob = self.bucket.blob(self._job_blob_path(job_id))
        if not blob.exists(client=self.storage_client):
            return None

        raw = blob.download_as_text()
        data = json.loads(raw)
        return data if isinstance(data, dict) else None

    def _upload_job_sync(self, job_id: str, data: dict):
        if not self.bucket:
            return
        blob = self.bucket.blob(self._job_blob_path(job_id))
        blob.upload_from_string(
            json.dumps(data, separators=(",", ":"), sort_keys=True),
            content_type="application/json",
        )

    async def _save_job(self, job_id: str, data: dict):
        self.jobs[job_id] = data
        if self.bucket:
            try:
                await asyncio.to_thread(self._upload_job_sync, job_id, data)
            except Exception as exc:
                print(f"Failed to persist job {job_id} to bucket: {exc}")

    async def _load_job(self, job_id: str, prefer_remote: bool = False) -> Optional[dict]:
        job = self.jobs.get(job_id)
        if job and not prefer_remote:
            return job

        if self.bucket:
            try:
                remote_job = await asyncio.to_thread(self._download_job_sync, job_id)
            except Exception as exc:
                print(f"Failed to read job {job_id} from bucket: {exc}")
                return job

            if remote_job:
                self.jobs[job_id] = remote_job
                return remote_job

        return job

    async def _ensure_local_worker(self):
        if self.cloud_tasks:
            return

        if self.local_worker_task and not self.local_worker_task.done():
            return

        self.local_worker_task = asyncio.create_task(self._local_worker_loop())

    async def _local_worker_loop(self):
        while True:
            item = await self.local_queue.get()
            try:
                await self.process_video_job(item["job_id"], item)
            except Exception as exc:
                print(f"Local worker failed for {item.get('job_id')}: {exc}")
                traceback.print_exc()
            finally:
                self.local_queue.task_done()

    async def create_video_job(self, request: VideoJobRequest) -> str:
        """
        Create a video job:
        - prod: enqueue to Cloud Tasks
        - local: enqueue to in-process async queue
        """
        job_id = str(uuid.uuid4())
        start_time = datetime.now().isoformat()

        await self._save_job(
            job_id,
            {
                "status": "pending",
                "job_start_time": start_time,
                "title": request.title,
                "caption": request.caption,
                "original_bet_link": request.original_bet_link,
                "duration_seconds": request.duration_seconds,
            },
        )

        job_data = {
            "title": request.title,
            "caption": request.caption,
            "original_bet_link": request.original_bet_link,
            "duration_seconds": request.duration_seconds,
        }

        if self.cloud_tasks:
            self.cloud_tasks.enqueue_video_job(job_id, job_data)
        else:
            await self._ensure_local_worker()
            await self.local_queue.put({"job_id": job_id, **job_data})

        return job_id

    async def process_video_job(self, job_id: str, job_data: dict):
        """
        Process the pipeline:
        1) Gemini prompt -> image 1
        2) Gemini prompt + image 1 -> image 2
        3) Veo prompt + image 1 + image 2 -> video operation
        """
        start_time = datetime.now().isoformat()
        existing_job = await self._load_job(job_id)

        try:
            title = job_data["title"]
            caption = job_data["caption"]
            original_bet_link = job_data["original_bet_link"]
            duration = int(job_data.get("duration_seconds", 6))

            first_prompt = create_first_image_prompt(
                title=title,
                caption=caption,
                original_bet_link=original_bet_link,
            )
            first_image = await self.vertex_service.generate_image_from_prompt(
                prompt=first_prompt
            )

            second_prompt = create_second_image_prompt(
                title=title,
                caption=caption,
                original_bet_link=original_bet_link,
            )
            second_image = await self.vertex_service.generate_image_from_prompt(
                prompt=second_prompt,
                image=first_image,
            )

            veo_prompt = create_video_prompt(
                title=title,
                caption=caption,
                original_bet_link=original_bet_link,
            )
            operation = await self.vertex_service.generate_video_content(
                prompt=veo_prompt,
                image_data=first_image,
                ending_image_data=second_image,
                duration_seconds=duration,
            )

            await self._save_job(
                job_id,
                {
                    "status": "processing",
                    "operation_name": operation.name,
                    "job_start_time": (
                        existing_job.get("job_start_time")
                        if existing_job and existing_job.get("job_start_time")
                        else start_time
                    ),
                    "title": title,
                    "caption": caption,
                    "original_bet_link": original_bet_link,
                    "duration_seconds": duration,
                },
            )
        except Exception as exc:
            print(f"Error processing video job {job_id}: {exc}")
            traceback.print_exc()
            await self._save_job(
                job_id,
                {
                    "status": "error",
                    "error": str(exc),
                    "job_start_time": (
                        existing_job.get("job_start_time")
                        if existing_job and existing_job.get("job_start_time")
                        else start_time
                    ),
                    "title": job_data.get("title"),
                    "caption": job_data.get("caption"),
                    "original_bet_link": job_data.get("original_bet_link"),
                    "duration_seconds": int(job_data.get("duration_seconds", 6)),
                },
            )

    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """
        Poll job status.
        For processing jobs, poll Vertex operation and cache final output URL.
        """
        job = await self._load_job(job_id, prefer_remote=bool(self.bucket))
        if job is None:
            return None

        status = job.get("status")
        job_start_time = self._parse_timestamp(job.get("job_start_time"))
        job_end_time = self._parse_timestamp(job.get("job_end_time"))
        original_bet_link = job.get("original_bet_link")

        if status in ("pending", "queued"):
            return JobStatus(
                status="waiting",
                job_start_time=job_start_time,
                original_bet_link=original_bet_link,
            )

        if status == "error":
            return JobStatus(
                status="error",
                job_start_time=job_start_time,
                job_end_time=job_end_time,
                error=job.get("error"),
                original_bet_link=original_bet_link,
            )

        if status == "done":
            return JobStatus(
                status="done",
                job_start_time=job_start_time,
                job_end_time=job_end_time,
                video_url=job.get("video_url"),
                original_bet_link=original_bet_link,
            )

        if status == "processing" and job.get("operation_name"):
            result = await self.vertex_service.get_video_status_by_name(
                job["operation_name"]
            )
            if result.status == "done":
                video_url = self._to_public_url(result.video_url)
                job["status"] = "done"
                job["video_url"] = video_url
                job["job_end_time"] = datetime.now().isoformat()
                await self._save_job(job_id, job)
                return JobStatus(
                    status="done",
                    job_start_time=job_start_time,
                    job_end_time=self._parse_timestamp(job["job_end_time"]),
                    video_url=video_url,
                    original_bet_link=original_bet_link,
                )
            return JobStatus(
                status="waiting",
                job_start_time=job_start_time,
                original_bet_link=original_bet_link,
            )

        return JobStatus(
            status="waiting",
            job_start_time=job_start_time,
            original_bet_link=original_bet_link,
        )

    async def update_job(self, job_id: str, data: dict):
        existing = await self._load_job(job_id) or {}
        existing.update(data)
        await self._save_job(job_id, existing)
