from typing import Literal

ShortsStyle = Literal["action_commentary", "vibe_music_edit", "fantasy_ai_gen"]

DEFAULT_SHORTS_STYLE: ShortsStyle = "action_commentary"

_SHORTS_STYLE_ALIASES: dict[str, ShortsStyle] = {
    "action": "action_commentary",
    "action_commentary": "action_commentary",
    "action-commentary": "action_commentary",
    "vibe_music_edit": "vibe_music_edit",
    "vibe-music-edit": "vibe_music_edit",
    "music_edit": "vibe_music_edit",
    "music": "vibe_music_edit",
    "edit": "vibe_music_edit",
    "fantasy_ai_gen": "fantasy_ai_gen",
    "fantasy-ai-gen": "fantasy_ai_gen",
    "fantasy": "fantasy_ai_gen",
    "aigen": "fantasy_ai_gen",
    "ai_gen": "fantasy_ai_gen",
}


def normalize_shorts_style(style: str | None) -> ShortsStyle:
    normalized = (style or "").strip().lower()
    return _SHORTS_STYLE_ALIASES.get(normalized, DEFAULT_SHORTS_STYLE)
