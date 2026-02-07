import asyncio
import base64
import json
import time
from typing import Optional

import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from openai import AsyncOpenAI

from utils.env import settings

KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"


class FeedService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.youtube_api_key = settings.YOUTUBE_API_KEY
        self.kalshi_api_key = settings.KALSHI_API_KEY
        self.kalshi_private_key = self._load_private_key()

    def _load_private_key(self):
        with open(settings.KALSHI_PRIVATE_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    def _sign_kalshi_request(self, method: str, path: str, timestamp_ms: int) -> str:
        message = f"{timestamp_ms}{method}{path}"
        signature = self.kalshi_private_key.sign(
            message.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def _get_kalshi_headers(self, method: str, path: str) -> dict:
        timestamp_ms = int(time.time() * 1000)
        signature = self._sign_kalshi_request(method, path, timestamp_ms)
        return {
            "KALSHI-ACCESS-KEY": self.kalshi_api_key,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": str(timestamp_ms),
            "Content-Type": "application/json",
        }

    async def _get_markets(self, status: str = "open", limit: int = 100) -> list[dict]:
        path = "/trade-api/v2/markets"
        params = {"status": status, "limit": limit}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{KALSHI_BASE_URL}/markets",
                params=params,
                headers=self._get_kalshi_headers("GET", path),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("markets", [])

    async def _get_event(self, event_ticker: str) -> dict:
        path = f"/trade-api/v2/events/{event_ticker}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{KALSHI_BASE_URL}/events/{event_ticker}",
                headers=self._get_kalshi_headers("GET", path),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("event", {})

    async def get_video_metadata(self, video_id: str) -> dict:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {"part": "snippet", "id": video_id, "key": self.youtube_api_key}
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
            "thumbnail": (
                snippet.get("thumbnails", {}).get("maxres", {}).get("url")
                or snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            ),
        }

    async def _extract_keywords(self, title: str, description: str) -> list[str]:
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

    async def _match_keywords_to_markets(
        self, keywords: list[str], markets: list[dict]
    ) -> list[int]:
        market_titles = [
            f"{i}: {m.get('yes_sub_title', m.get('title', 'Unknown'))}"
            for i, m in enumerate(markets)
        ]
        market_list = "\n".join(market_titles)
        keywords_str = ", ".join(keywords)

        prompt = f"""You match video keywords to prediction market bets.

Keywords from video: {keywords_str}

Available markets:
{market_list}

Return a JSON array of indices (0-based) of the most relevant markets, ranked by relevance.
Return up to 10 indices. Only return markets that are genuinely related to the keywords.
If no markets are relevant, return an empty array [].

Return ONLY the JSON array, no explanation."""

        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        try:
            return json.loads(response.choices[0].message.content.strip())
        except json.JSONDecodeError:
            return []

    async def _format_market_display(
        self, market: dict, event: dict, keywords: list[str]
    ) -> dict:
        event_title = event.get("title", "")
        yes_sub_title = market.get("yes_sub_title", "")
        rules = market.get("rules_primary", "")
        keywords_str = ", ".join(keywords)

        prompt = f"""Format this Kalshi prediction market for display.

Event: {event_title}
Outcome text: {yes_sub_title}
Rules: {rules}
Video keywords: {keywords_str}

Create a clean, user-friendly bet display:
1. "question": A clear, concise yes/no question about this bet (e.g., "Will Arsenal win today?")
2. "outcome": The single most relevant team/item/subject from the outcome text based on the video keywords (e.g., "Arsenal"). Just the name, no "yes" prefix.

Return JSON only: {{"question": "...", "outcome": "..."}}"""

        try:
            response = await self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception:
            return {
                "question": event_title or yes_sub_title,
                "outcome": yes_sub_title.split(",")[0].replace("yes ", "") if yes_sub_title else "",
            }

    async def match_video(self, video_id: str) -> Optional[dict]:
        metadata = await self.get_video_metadata(video_id)
        keywords = await self._extract_keywords(metadata["title"], metadata["description"])

        if not keywords:
            return None

        markets = await self._get_markets(status="open", limit=100)
        if not markets:
            return None

        indices = await self._match_keywords_to_markets(keywords, markets)
        if not indices:
            return None

        best_market = markets[indices[0]]
        event_ticker = best_market.get("event_ticker", "")
        event = {}
        if event_ticker:
            try:
                event = await self._get_event(event_ticker)
            except Exception:
                pass

        formatted = await self._format_market_display(best_market, event, keywords)

        return {
            "youtube": {
                "video_id": video_id,
                "title": metadata["title"],
                "thumbnail": metadata["thumbnail"],
                "channel": metadata["channel"],
            },
            "kalshi": {
                "ticker": best_market.get("ticker"),
                "question": formatted.get("question", ""),
                "outcome": formatted.get("outcome", ""),
                "yes_price": best_market.get("yes_bid", 0),
                "no_price": best_market.get("no_bid", 0),
                "volume": best_market.get("volume", 0),
            },
            "keywords": keywords,
        }

    async def get_feed(self, video_ids: list[str]) -> list[dict]:
        tasks = [self.match_video(vid) for vid in video_ids]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
