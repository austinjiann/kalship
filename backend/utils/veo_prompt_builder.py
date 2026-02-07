def create_video_prompt(
    title: str,
    caption: str,
    original_bet_link: str,
) -> str:
    """
    Build a Veo prompt that creates logical motion between start and end frames.
    """
    return f"""Create a smooth, logical transition from the first frame to the last frame.

ACTION: {caption}

RULES:
- Motion must be physically realistic and logical
- Objects and people stay consistent (no disappearing helmets, no teleporting)
- Forward motion only - balls thrown forward, people move forward
- Can use cinematic cuts/transitions if needed to connect the scenes
- Think like a movie director editing a highlight reel

STYLE: Professional sports broadcast, cinematic, high energy

Connect these two frames with exciting but LOGICAL action."""
