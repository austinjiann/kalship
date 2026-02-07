# Worker endpoint for Cloud Tasks
from blacksheep import json, Response
from blacksheep.server.controllers import APIController, post
from services.job_service import JobService

class Worker(APIController):
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    @post("/process")
    async def process_job(self, data: dict) -> Response:
        required = ("job_id", "title", "caption", "original_bet_link")
        missing = [key for key in required if not data.get(key)]
        if missing:
            return json(
                {"error": f"Missing required fields: {', '.join(missing)}"},
                status=400,
            )

        job_id = data["job_id"]

        # Process the job
        await self.job_service.process_video_job(job_id, data)

        return json({"status": "processing", "job_id": job_id})
