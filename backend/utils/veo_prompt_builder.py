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
VEO MODEL: ve0-3.1

BET TOPIC: {title}
SELECTED OUTCOME (must stay consistent): {outcome}
KALSHI LINK CONTEXT: {original_bet_link}

# CHANGED: generalized from teams-only → entities/subjects (works for sports, events, objects, yes/no outcomes)
PARSE & CONSTRAINTS:
- Extract the primary entities, subjects, or actors from "BET TOPIC" (e.g., teams, people, vehicles, objects, events).
- Only depict those extracted entities; do NOT introduce unrelated characters, teams, objects, or concepts.
- If the SELECTED OUTCOME implies opposing sides (e.g., win/lose, success/failure), map positive outcomes to the successful entity and negative outcomes to the failing entity.
- If the SELECTED OUTCOME is binary or non-competitive (e.g., "rocket launches", "ship reaches space", "event occurs = yes"), depict only the progression and success/failure of the primary subject — no celebration or defeat from unrelated actors.  # ADDED
- If outcome is ambiguous, depict the most literal, direct visual interpretation consistent with BET TOPIC.

CORE DIRECTIVE:
- The sequence must clearly communicate that the selected outcome is happening.
- Keep subjects consistent with the start frame identity and styling.
- Prioritize action and momentum over abstract mood shots.
- Cinematic staging: emphasize camera choreography (pans, dollies, crane moves) and purposeful framing.

BEAT PLAN (8 SECONDS):
0.0-2.5s:
- Establishing wide that quickly ramps into a dynamic push-in (dolly + slight crane) to sell scale and motion.  # CHANGED
- Use a slow whip-pan or seamless match cut to transition into the action to preserve momentum.  # CHANGED
- Environmental motion appropriate to the scenario (crowd surge, wind, exhaust, debris, particles, rain, confetti).  # CHANGED: generalized environment

2.5-5.5s:
- Peak action moment in dramatic near-slow motion.
- Intercut a low-angle hero shot (telephoto compression) with a medium over-the-shoulder or tracking move to show decisive action or state change.  # CHANGED
- Use rack-focus transitions between subject and consequence to heighten clarity and drama.  # CHANGED
- Include a brief Dutch tilt or subtle handheld jitter for intensity (maintain continuity).

5.5-8.0s:
- Explosive payoff and reaction shot with cinematic finish.
- Wide-to-tight sequence: a theatrical pull-out followed by an ultra-tight close-up on the decisive visual proof of the outcome (impact, separation, ignition, celebration, arrival).  # CHANGED
- End on a clear, unambiguous visual that reinforces the outcome.

CAMERA & EDITING NOTES (stylistic constraints):
- Camera language: combine smooth dolly/crane moves, deliberate pans, telephoto close-ups, and one fast whip or arc move for energy.  # CHANGED
- Use varied camera angles: wide establishing, low-angle hero, tracking medium, close telephoto, reaction inserts.  # CHANGED
- Cuts should feel motivated by motion (match-on-action, whip-pan transitions), not arbitrary jump cuts.
- Light & atmosphere: volumetric lighting, lens streaks, subtle film grain, realistic particles for depth and scale.  # CHANGED
- Motion: controlled motion blur during fast moves; near-slow-motion for the emotional or mechanical peak.

# CHANGED: generalized continuity rules (no longer sports-specific)
CONTINUITY & LOGIC RULES:
- Maintain strict identity continuity of all primary entities (no swapping, morphing, or introducing new actors).
- Do not depict unrelated celebrations, reactions, or failures unless they are logically caused by the outcome.
- Visuals must logically follow from the BET TOPIC and SELECTED OUTCOME.

DRAMATIC EFFECTS & POLISH:
- Add cinematic visual effects: volumetric light shafts, particle sprays, subtle lens flares, and realistic environmental interaction.  # CHANGED
- Emphasize depth with layered foreground elements passing the lens during pans.

SOUND & RHYTHM (visual-first cueing):
- Edit rhythm like a movie trailer: accelerating cuts, swelling intensity toward the peak, sharp visual punctuation at payoff (visual timing cues only).  # CHANGED

STYLE + CAMERA:
- Blockbuster cinematic or high-impact trailer intensity.
- Dynamic handheld/dolly/telephoto movement with continuity.
- Realistic physics, crisp detail, rich contrast, dramatic lighting.
- No static framing, no slideshow behavior, no reverse motion.

OUTPUT CONSTRAINTS:
- Vertical 9:16 composition.
- No text overlays, subtitles, logos, watermarks, or UI.
- No identity drift or face morphing."""
