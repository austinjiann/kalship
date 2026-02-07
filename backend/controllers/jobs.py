# Job controller for video generation pipeline
import json as json_lib

from blacksheep import json, Response
from blacksheep.server.controllers import APIController, post, get
from services.job_service import JobService
from models.job import VideoJobRequest


class Jobs(APIController):
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def _coerce_payload(self, payload: dict) -> dict:
        return {
            "title": payload.get("title"),
            "caption": payload.get("caption"),
            "original_bet_link": (
                payload.get("original_bet_link")
                or payload.get("originalBetLink")
                or payload.get("originla_bet_link")
                or payload.get("bet_link")
                or payload.get("bet")
            ),
            "duration_seconds": payload.get("duration_seconds", 6),
        }

    @post("/create")
    async def create_job(self, request):
        body = None
        try:
            body = await request.json()
        except Exception:
            form = await request.form()
            normalized = {}
            for k, v in form.items():
                if isinstance(k, bytes):
                    key = k.decode()
                else:
                    key = str(k)

                val = v
                if isinstance(val, (list, tuple)):
                    val = val[0] if val else ""
                if isinstance(val, bytes):
                    try:
                        val = val.decode()
                    except Exception:
                        val = str(val)
                normalized[key] = val
            body = normalized

        payload = self._coerce_payload(body)
        title = (payload.get("title") or "").strip()
        caption = (payload.get("caption") or "").strip()
        original_bet_link = (payload.get("original_bet_link") or "").strip()

        if not title or not caption or not original_bet_link:
            return json(
                {
                    "error": (
                        "title, caption, and original_bet_link are required"
                    )
                },
                status=400,
            )

        try:
            duration_seconds = int(payload.get("duration_seconds", 6))
        except Exception:
            duration_seconds = 6

        job_request = VideoJobRequest(
            title=title,
            caption=caption,
            original_bet_link=original_bet_link,
            duration_seconds=max(2, min(duration_seconds, 10)),
        )

        job_id = await self.job_service.create_video_job(job_request)
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
            "original_bet_link": status.original_bet_link,
        })
