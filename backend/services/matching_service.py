import asyncio
from typing import Optional

from services.kalshi_service import KalshiService
from services.video_analysis_service import VideoAnalysisService


class MatchingService:
    def __init__(self):
        self.kalshi = KalshiService()
        self.video_analysis = VideoAnalysisService()

    async def match_video_to_market(self, video_id: str) -> Optional[dict]:
        analysis = await self.video_analysis.analyze_video(video_id)
        keywords = analysis.get("keywords", [])

        if not keywords:
            return None

        matches = await self.kalshi.search_markets_by_keywords(keywords)

        if not matches:
            return None

        best_match = matches[0]
        return {
            "youtube": {
                "video_id": video_id,
                "title": analysis["metadata"]["title"],
                "thumbnail": analysis["metadata"]["thumbnail"],
                "channel": analysis["metadata"]["channel"],
            },
            "kalshi": best_match,
            "keywords": keywords,
        }

    async def match_videos_batch(self, video_ids: list[str]) -> list[dict]:
        tasks = [self.match_video_to_market(vid) for vid in video_ids]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
