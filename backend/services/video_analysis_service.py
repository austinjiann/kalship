import aiohttp
from openai import AsyncOpenAI

from utils.env import settings


class VideoAnalysisService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.youtube_api_key = settings.YOUTUBE_API_KEY

    async def get_video_metadata(self, video_id: str) -> dict:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "id": video_id,
            "key": self.youtube_api_key,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

        if not data.get("items"):
            return {"title": "", "description": "", "channel": "", "thumbnail": ""}

        snippet = data["items"][0]["snippet"]
        return {
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:500],
            "channel": snippet.get("channelTitle", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("maxres", {}).get("url")
            or snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        }

    async def extract_keywords(self, title: str, description: str) -> list[str]:
        prompt = f"""Extract 3-5 keywords from this YouTube video that could match prediction market bets.
Focus on: sports teams/players, political figures, companies, events, weather phenomena, cryptocurrency.
Return ONLY comma-separated keywords, no explanation.

Title: {title}
Description: {description[:500]}"""

        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        keywords_str = response.choices[0].message.content.strip()
        return [k.strip() for k in keywords_str.split(",") if k.strip()]

    async def analyze_video(self, video_id: str) -> dict:
        metadata = await self.get_video_metadata(video_id)
        keywords = await self.extract_keywords(metadata["title"], metadata["description"])
        return {
            "video_id": video_id,
            "metadata": metadata,
            "keywords": keywords,
        }
