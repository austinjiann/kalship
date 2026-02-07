from utils.shorts_style import normalize_shorts_style


def create_video_prompt(
    title: str,
    outcome: str,
    original_bet_link: str,
    shorts_style: str | None = None,
) -> str:
    """
    Build a Veo prompt for an 8-second short-form video.
    The generated sequence should clearly reinforce the selected outcome.
    """
    style = normalize_shorts_style(shorts_style)

    if style == "vibe_music_edit":
        return f"""Create an 8-second vertical 9:16 cinematic music-edit video from the provided start frame.
VEO MODEL: veo-3.1

BET TOPIC: {title}
SELECTED OUTCOME (must stay consistent): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}
STYLE PRESET: VIBE MUSIC EDIT

CORE DIRECTIVE:
- Keep all subjects consistent with the start frame and character identity.
- Show the selected outcome as already true through visual storytelling.
- Prioritize style, rhythm, and motion continuity.

EDIT RHYTHM AND CAMERA:
- Fast montage language: jump cuts, whip pans, speed ramps, match-on-action transitions.
- Use wide, medium, and tight inserts with deliberate beat-synced transitions.
- Keep movement fluid and intentional, never chaotic or random.

BEAT PLAN:
0.0-2.5s: Strong hook shot, immediate motion, visual tone established.
2.5-5.5s: Escalation with rhythmic cuts and one hero moment.
5.5-8.0s: Clean payoff shot proving the selected outcome.

AUDIO PLAN:
- Generate original high-quality instrumental music that matches scene energy.
- Music must have clear beat transitions aligned with visual cuts.
- No dialogue, no narration, no vocals.
- Keep SFX subtle so music remains primary.

OUTPUT CONSTRAINTS:
- Vertical 9:16 only.
- No text, subtitles, logos, watermarks, or UI overlays.
- No identity drift, no face morphing, no reverse motion."""

    if style == "fantasy_ai_gen":
        return f"""Create an 8-second vertical 9:16 fantasy art video from the provided start frame.
VEO MODEL: veo-3.1

BET TOPIC: {title}
SELECTED OUTCOME (must stay consistent): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}
STYLE PRESET: FANTASY AI-GEN ART

VISUAL LANGUAGE:
- Breathtaking painterly 2D animation style with lush, vibrant, dreamlike atmosphere.
- Intricate handcrafted detail inspired by traditional Japanese woodblock textures.
- Ancient forest-cathedral environments, glowing sprites, drifting petals, magical mist, and rich depth layers.
- Keep subjects and faces consistent with provided references, even under stylized rendering.

NARRATIVE ARC:
- Build a continuous visual narrative of wonder, respect, and connection between humans and a colossal nature guardian.
- Translate the selected outcome into this world while keeping the outcome unambiguously true.
- Motion should feel graceful and enchanted: fold-like transformations, gentle camera glides, and magical environmental reactions.

BEAT PLAN:
0.0-2.5s: Sacred reveal of the world and lead subjects.
2.5-5.5s: Relationship/action beat that advances the selected outcome.
5.5-8.0s: Emotional payoff showing clear outcome proof and ecological harmony.

AUDIO PLAN:
- Generate emotionally resonant orchestral fantasy score with natural ambience.
- Include subtle leaves, birds, and airy forest texture under the score.
- No spoken dialogue or narration.

OUTPUT CONSTRAINTS:
- Vertical 9:16 only.
- No text, subtitles, logos, watermarks, or UI overlays.
- No identity drift, no face morphing, no unnatural body deformation."""

    return f"""Create an 8-second vertical 9:16 action video from the provided start frame.
VEO MODEL: veo-3.1

BET TOPIC: {title}
SELECTED OUTCOME (must stay consistent): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}
STYLE PRESET: ACTION COMMENTARY

PARSE AND CONSTRAINTS:
- Extract the primary entities or actors from BET TOPIC.
- Depict only those entities and logically related participants.
- Keep the selected outcome visually true from beginning to end.

CORE DIRECTIVE:
- High-impact cinematic momentum with clear visual storytelling.
- Keep identities, uniforms, and subject styling consistent with the start frame.
- Emphasize decisive action, consequence, and payoff.

BEAT PLAN:
0.0-2.5s: Dynamic hook shot and immediate momentum.
2.5-5.5s: Peak action sequence with near-slow-motion hero beat.
5.5-8.0s: Decisive payoff shot that clearly proves the outcome.

CAMERA LANGUAGE:
- Purposeful dolly/crane movement, one whip transition, varied angles (wide/medium/tight).
- Match cuts motivated by action, not random cuts.
- Controlled motion blur and realistic physics.

AUDIO PLAN:
- Generate commentator-style voiceover (one concise excited line) that matches the selected outcome.
- Add realistic action SFX and environment sound.
- No background music.

OUTPUT CONSTRAINTS:
- Vertical 9:16 only.
- No text, subtitles, logos, watermarks, or UI overlays.
- No identity drift, no face morphing, no reverse motion."""
