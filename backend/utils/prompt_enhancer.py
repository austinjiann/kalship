from openai import AsyncOpenAI
from utils.env import settings

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You lightly clarify trading market titles for a video AI. Given a trade title, outcome, and link, return ONE short sentence that makes the outcome obvious.

Rules:
1. Stay very close to the original title. Only add small clarifying details.
2. For competitions, name the winner AND the loser (e.g. "Seahawks beat the Eagles to win the Super Bowl").
3. One sentence max.
4. No statistics, odds, or numbers. No cinematic language. No camera directions.
5. Just state what happened as a simple headline."""

SANITIZE_PROMPT = """You are rewriting a video generation prompt to comply with content policies.

The original prompt was rejected by an AI video generator for mentioning real people, brands, or sensitive topics.

Rewrite BOTH the title and outcome so they:
1. Remove ALL real person names — replace with generic descriptions (e.g. "Beyonce" → "a famous pop singer", "Trump" → "a political leader")
2. Remove trademarked brand names where possible (e.g. "NFL" → "professional football league")
3. Keep the core meaning/scenario intact — the video should still depict the same general situation
4. Keep it concise — one line each

Return JSON only: {"title": "...", "outcome": "..."}"""


async def enhance_prompt(title: str, outcome: str, original_trade_link: str) -> str:
    user_message = f"""Trade title: {title}
Selected outcome: {outcome}
Trade link: {original_trade_link}

Write a vivid cinematic scene description for this outcome."""

    response = await _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()


async def sanitize_for_content_policy(title: str, outcome: str) -> tuple[str, str]:
    """Rewrite title/outcome to avoid Vertex AI content policy violations.

    Returns (sanitized_title, sanitized_outcome).
    """
    import json

    user_message = f"""Original title: {title}
Original outcome: {outcome}

Rewrite these to remove real names, brands, and sensitive terms."""

    try:
        response = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SANITIZE_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=200,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)
        return parsed.get("title", title), parsed.get("outcome", outcome)
    except Exception as e:
        print(f"[sanitize] Failed to sanitize prompt: {e}")
        return title, outcome
