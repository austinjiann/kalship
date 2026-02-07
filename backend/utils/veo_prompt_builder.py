def create_video_prompt(
    custom_prompt: str | None,
    global_context: str | None,
    annotation_description: str | None
) -> str:
    """Build the video generation prompt from components"""
    parts = []

    if global_context:
        parts.append(f"Context: {global_context}")

    if custom_prompt:
        parts.append(custom_prompt)

    if annotation_description:
        parts.append(f"Animation notes: {annotation_description}")

    return "\n\n".join(parts) if parts else "Generate a video"
