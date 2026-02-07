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
        ct = request.headers.get("content-type") or ""
        if "application/json" in ct:
            body = await request.json()
        else:
            form = await request.form()
            body = {k: form.get(k) for k in form}
            if isinstance(body.get("bet"), str):
                raw_bet = body.get("bet", "").strip()
                if raw_bet.startswith("{") and raw_bet.endswith("}"):
                    try:
                        parsed = json_lib.loads(raw_bet)
                        if isinstance(parsed, dict):
                            body["bet"] = parsed.get("link") or raw_bet
                    except Exception:
                        pass

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
