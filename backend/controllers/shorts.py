from blacksheep import json
from blacksheep.server.controllers import APIController, get

from services.feed_service import FeedService

HARDCODED_VIDEO_IDS = [
    "vHaPgrSMlI0",
    "HZOkwNsYFdo",
    "w1rbnM6A4AA",
    "_qW6a1A9gb0",
    "3fQhDJlRJYg",
    "LQ8uCvKYu3Y",
]


class Shorts(APIController):
    def __init__(self, feed_service: FeedService):
        self.feed_service = feed_service

    @classmethod
    def route(cls):
        return "/shorts"

    @get("/health")
    async def health_check(self):
        return json({"status": "ok"})

    @get("/match")
    async def match_video(self, video_id: str = ""):
        if not video_id:
            return json({"error": "video_id required"}, status=400)
        result = await self.feed_service.match_video(video_id)
        if not result:
            return json({"error": "No matching market found"}, status=404)
        return json(result)

    @get("/feed")
    async def get_feed(self, limit: int = 20):
        video_ids = HARDCODED_VIDEO_IDS[:limit]
        results = await self.feed_service.get_feed(video_ids)
        feed = []
        for i, item in enumerate(results):
            feed.append({
                "id": str(i + 1),
                "youtube": item["youtube"],
                "kalshi": item["kalshi"],
            })
        return json(feed)
