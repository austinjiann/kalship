# Job controller for video generation pipeline
from blacksheep import json, Response
from blacksheep.server.controllers import APIController, post, get
from services.job_service import JobService
from models.job import VideoJobRequest


class Jobs(APIController):
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    @post("/create")
    async def create_job(self, request: VideoJobRequest) -> Response:
        job_id = await self.job_service.create_video_job(request)
        return json({"job_id": job_id})

    @get("/status/{job_id}")
    async def get_status(self, job_id: str) -> Response:
        status = await self.job_service.get_job_status(job_id)

        if status is None:
            return json({"error": "Job not found"}, status=404)

        return json({
            "status": status.status,
            "video_url": status.video_url,
            "error": status.error,
            "metadata": status.metadata
        })
