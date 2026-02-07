def create_video_prompt(
    title: str,
    caption: str,
    original_bet_link: str,
) -> str:
    """
    Build a Veo prompt for an exciting short-form video.
    Works for any topic: sports, politics, crypto, entertainment, etc.
    """
    return f"""Create an 8-second cinematic viral video clip.

SCENARIO: {title}

Animate this starting frame into a dramatic, attention-grabbing sequence.

ANALYZE THE SCENARIO AND CREATE APPROPRIATE MOTION:

For SPORTS: Athletic action, slow-mo replay, crowd eruption, confetti celebration
For POLITICS: Dramatic speech moment, crowd cheering, victory gestures, camera flashes
For FINANCE/CRYPTO: Explosive growth visualization, rockets launching, coins flying, chart explosions
For ENTERTAINMENT: Award moment, standing ovation, confetti drop, spotlight drama

SEQUENCE STRUCTURE:
0-3s: Build tension - dramatic action or movement begins
3-5s: Peak moment - slow-motion on the key instant
5-8s: Release - celebration, reaction, or dramatic conclusion

CINEMATIC STYLE:
- Super Bowl commercial / movie trailer quality
- Dynamic camera movement: dolly, zoom, rack focus
- Dramatic lighting with lens flares and atmosphere
- Quick cuts between angles are encouraged
- Professional color grading

MOTION REQUIREMENTS:
- Smooth, realistic physics
- Forward momentum - never reverse or rewind
- Environmental motion: particles, confetti, crowd movement
- Subject motion: gestures, reactions, movement

Make it feel like a blockbuster movie moment compressed into 8 seconds."""
