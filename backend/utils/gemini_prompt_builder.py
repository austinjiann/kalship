def create_first_image_prompt(
    title: str,
    outcome: str,
    original_bet_link: str,
) -> str:
    """
    Build the first-frame prompt for Gemini image generation.
    The frame should unambiguously depict the selected Kalshi outcome.
    """
    return f"""Create a single 4K cinematic start frame for an 8-second vertical short video.

BET TOPIC: {title}
SELECTED OUTCOME (must be visually true): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}

PRIMARY GOAL:
- Show the selected outcome as already happening right now.
- Build a high-impact, action-heavy moment, not a static portrait.

SCENE DIRECTION:
- Vertical 9:16 composition optimized for mobile shorts.
- Mid-action peak moment with motion cues (speed trails, debris, crowd reaction, dramatic body movement).
- Cinematic realism with strong contrast, stadium/event atmosphere, and dramatic lighting.
- If the topic is sports, prioritize gameplay intensity and authentic uniforms.
- If people are provided in references, they must be the clear lead subjects.

STRICT REQUIREMENTS:
1. Use provided images as hard references for subject identity and styling.
2. Preserve recognizable faces and do not alter identity.
3. No text, captions, watermarks, graphics, or UI overlays.
4. No bland studio shots, no static posed lineup.
5. The frame must look ready to animate into a blockbuster sequence.

Output exactly one photorealistic image."""
