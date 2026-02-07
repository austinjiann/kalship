def create_video_prompt(
    title: str,
    outcome: str,
    original_bet_link: str,
) -> str:
    """
    Build a Veo prompt for an exciting short-form video.
    The generated sequence should clearly reinforce the selected outcome.
    """
    return f"""Create an 8-second vertical cinematic video from the provided start frame.

BET TOPIC: {title}
SELECTED OUTCOME (must stay consistent): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}

CORE DIRECTIVE:
- The sequence must clearly communicate that the selected outcome is happening.
- Keep subjects consistent with the start frame identity and styling.
- Prioritize action and momentum over abstract mood shots.

BEAT PLAN (8 SECONDS):
0.0-2.5s:
- Immediate kinetic action and camera push-in.
- Strong environmental motion (crowd surge, particles, debris, rain, confetti, field motion).
2.5-5.5s:
- Peak action moment in dramatic near-slow motion.
- Hero subject performs decisive movement tied to the outcome.
5.5-8.0s:
- Explosive payoff and reaction shot with cinematic finish.
- End on a clear, high-confidence visual that reinforces the outcome.

STYLE + CAMERA:
- Blockbuster sports-promo or movie-trailer intensity.
- Dynamic handheld/dolly/telephoto cuts, but keep continuity.
- Realistic physics, crisp detail, rich contrast, dramatic lighting.
- No static framing, no slideshow behavior, no reverse motion.

OUTPUT CONSTRAINTS:
- Vertical 9:16 composition.
- No text overlays, subtitles, logos, watermarks, or UI.
- No identity drift or face morphing."""
