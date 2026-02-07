def create_video_prompt(
    title: str,
    caption: str,
    metadata: dict | None = None
) -> str:
    """
    Build an exciting, action-focused prompt for Veo video generation.

    Veo takes: start frame image + end frame image + prompt
    This prompt should describe the ACTION/MOTION between the frames.

    Args:
        title: Short title (e.g., "Epic UFC Knockout")
        caption: Description of what happens (e.g., "Topuria throws a devastating left hook")
        metadata: Optional context (e.g., {"sport": "mma", "event": "UFC 298"})

    Returns:
        Cinematic, action-packed video prompt
    """
    # Base prompt structure for exciting video
    prompt_parts = []

    # Add cinematic context
    prompt_parts.append("Cinematic sports footage, dramatic slow motion, high energy")

    # Add the main action from caption
    if caption:
        # Transform caption into action-focused language
        action_prompt = caption
        # Add intensity modifiers
        action_prompt = f"{action_prompt}, crowd erupts, intense atmosphere"
        prompt_parts.append(action_prompt)

    # Add title context
    if title:
        prompt_parts.append(f"Scene: {title}")

    # Add metadata context if relevant
    if metadata:
        if metadata.get("sport"):
            prompt_parts.append(f"Sport: {metadata['sport']}")
        if metadata.get("event"):
            prompt_parts.append(f"Event: {metadata['event']}")
        if metadata.get("style"):
            prompt_parts.append(f"Style: {metadata['style']}")

    # Add quality/style modifiers
    prompt_parts.append("Professional broadcast quality, dynamic camera movement, vivid colors")

    return "\n".join(prompt_parts)