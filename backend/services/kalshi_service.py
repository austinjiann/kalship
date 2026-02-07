import base64
import time
from typing import Optional
import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from openai import AsyncOpenAI

from utils.env import settings

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"


class KalshiService:
    def __init__(self):
        self.api_key = settings.KALSHI_API_KEY
        self.private_key = self._load_private_key()
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _load_private_key(self):
        with open(settings.KALSHI_PRIVATE_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    def _sign_request(self, method: str, path: str, timestamp_ms: int) -> str:
        message = f"{timestamp_ms}{method}{path}"
        signature = self.private_key.sign(
            message.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def _get_headers(self, method: str, path: str) -> dict:
        timestamp_ms = int(time.time() * 1000)
        signature = self._sign_request(method, path, timestamp_ms)
        return {
            "KALSHI-ACCESS-KEY": self.api_key,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": str(timestamp_ms),
            "Content-Type": "application/json",
        }

    async def get_markets(
        self,
        status: str = "open",
        limit: int = 100,
        cursor: Optional[str] = None,
        series_ticker: Optional[str] = None,
    ) -> dict:
        path = "/trade-api/v2/markets"
        params = {"status": status, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        if series_ticker:
            params["series_ticker"] = series_ticker

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/markets",
                params=params,
                headers=self._get_headers("GET", path),
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def get_market(self, ticker: str) -> dict:
        path = f"/trade-api/v2/markets/{ticker}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/markets/{ticker}",
                headers=self._get_headers("GET", path),
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def get_event(self, event_ticker: str) -> dict:
        path = f"/trade-api/v2/events/{event_ticker}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/events/{event_ticker}",
                headers=self._get_headers("GET", path),
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def format_market_display(
        self, market: dict, event: dict, keywords: list[str]
    ) -> dict:
        import json
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

    async def search_markets_by_keywords(self, keywords: list[str]) -> list[dict]:
        markets_response = await self.get_markets(status="open", limit=100)
        markets = markets_response.get("markets", [])

        if not markets:
            return []

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
            import json
            indices = json.loads(response.choices[0].message.content.strip())
            result = []
            event_cache = {}
            for i in indices:
                if 0 <= i < len(markets):
                    m = markets[i]
                    event_ticker = m.get("event_ticker", "")
                    if event_ticker and event_ticker not in event_cache:
                        try:
                            event_data = await self.get_event(event_ticker)
                            event_cache[event_ticker] = event_data.get("event", {})
                        except Exception:
                            event_cache[event_ticker] = {}
                    event = event_cache.get(event_ticker, {})
                    formatted = await self.format_market_display(m, event, keywords)
                    result.append({
                        "ticker": m.get("ticker"),
                        "question": formatted.get("question", ""),
                        "outcome": formatted.get("outcome", ""),
                        "yes_price": m.get("yes_bid", 0),
                        "no_price": m.get("no_bid", 0),
                        "volume": m.get("volume", 0),
                    })
            return result
        except (json.JSONDecodeError, TypeError):
            return []
