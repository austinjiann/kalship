from utils.shorts_style import normalize_shorts_style


def create_first_image_prompt(
    title: str,
    outcome: str,
    original_bet_link: str,
    shorts_style: str | None = None,
) -> str:
    """
    Build the first-frame prompt for Gemini image generation.
    The frame should unambiguously depict the selected Kalshi outcome.
    """
    style = normalize_shorts_style(shorts_style)

    if style == "vibe_music_edit":
        return f"""Create exactly one 4K vertical 9:16 first frame for an 8-second Shorts-style edit.

BET TOPIC: {title}
SELECTED OUTCOME (must be visually true): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}
STYLE PRESET: VIBE MUSIC EDIT

PRIMARY GOAL:
- Show the selected outcome as already true in a stylish, fast-cut-ready frame.
- Make this feel like the opening still of a premium music-driven social edit.

SCENE DIRECTION:
- Dramatic cinematic composition with strong foreground/background depth.
- Bold color grading, controlled contrast, and striking light sources.
- Subject is in an expressive pose with implied motion.
- If character images are provided, those people must be the clear leads.

STRICT REQUIREMENTS:
1. Preserve identity from provided character images exactly.
2. No text, captions, logos, score bugs, or UI overlays.
3. No static studio portrait look.
4. Frame must feel instantly editable to beat-synced transitions.

Output exactly one image."""

    if style == "fantasy_ai_gen":
        return f"""Create exactly one 4K vertical 9:16 start frame for an 8-second fantasy short.

BET TOPIC: {title}
SELECTED OUTCOME (must be visually true): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}
STYLE PRESET: FANTASY AI-GEN ART

VISUAL DIRECTION:
- A breathtaking painterly 2D animated look: lush, vibrant, slightly surreal, and dreamlike.
- Layer in intricate handcrafted detail inspired by traditional Japanese woodblock print textures.
- Build a mythic natural world with towering ancient trees, luminous sprites, moss, petals, mist, and magical depth.
- If character images are provided, preserve their identity exactly while stylizing their clothing/materials to match the fantasy world.

NARRATIVE MOMENT:
- Capture a clear emotional beat of connection between human and nature or guardian-like beings.
- Show the selected outcome as already true in this world (literal or symbolic), with clear visual proof.
- Keep it cinematic and continuous, not collage-like.

STRICT REQUIREMENTS:
1. Outcome clarity is mandatory even in fantasy stylization.
2. No text, captions, logos, watermarks, or UI elements.
3. Keep readable subject silhouettes and strong focal hierarchy.
4. Preserve face identity from character references when provided.

Output exactly one richly detailed image."""

    return f"""Create exactly one 4K cinematic start frame for an 8-second vertical short video.

BET TOPIC: {title}
SELECTED OUTCOME (must be visually true): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}
STYLE PRESET: ACTION COMMENTARY

PRIMARY GOAL:
- Show the selected outcome as already happening right now.
- Build a high-impact, action-heavy moment, not a static portrait.

SCENE DIRECTION:
- Vertical 9:16 composition optimized for mobile shorts.
- Mid-action peak moment with motion cues (speed trails, debris, crowd reaction, dramatic body movement).
- Cinematic realism with strong contrast, atmosphere, and dramatic lighting.
- If the topic is sports, prioritize gameplay intensity and authentic uniforms.
- If character images are provided, those people must be the clear lead subjects.

STRICT REQUIREMENTS:
1. Use provided images as hard references for subject identity and styling.
2. Preserve recognizable faces and do not alter identity.
3. No text, captions, watermarks, graphics, or UI overlays.
4. No bland studio shots, no static posed lineup.
5. The frame must look ready to animate into a blockbuster sequence.

Output exactly one photorealistic image."""
