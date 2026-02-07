# Worker endpoint for Cloud Tasks
from blacksheep import json, Response
from blacksheep.server.controllers import APIController, post
from services.job_service import JobService

class Worker(APIController):
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    @post("/process")
    async def process_job(self, data: dict) -> Response:
        job_id = data.get("job_id")
        if not job_id:
            return json({"error": "job_id required"}, status=400)

        # Process the job
        await self.job_service.process_video_job(job_id, data)

        return json({"status": "processing", "job_id": job_id})
