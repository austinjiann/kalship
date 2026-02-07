def create_first_image_prompt(
    title: str,
    caption: str,
    original_bet_link: str,
) -> str:
    """
    Build a first-frame prompt for Gemini image generation.
    Works for any topic: sports, politics, crypto, entertainment, etc.
    """
    return f"""Create a 4K cinematic frame for a viral short-form video advertisement.

SCENARIO: {title}

ANALYZE THE SCENARIO AND CREATE THE MOST DRAMATIC VISUAL:

For SPORTS (games, championships, players):
- Mid-action athletic moment: diving catch, slam dunk, goal celebration
- Player faces must match any provided headshot references
- Accurate team uniforms and stadium atmosphere

For POLITICS (elections, candidates, legislation):
- Dramatic podium moment, victory celebration, or tense debate scene
- Politician faces must match any provided photo references
- Capitol building, rally crowd, or press conference setting

For FINANCE/CRYPTO (stocks, Bitcoin, markets):
- Dramatic visualization: rocket launch, explosion of coins, trading floor chaos
- Abstract energy: glowing charts, digital particles, futuristic aesthetic
- Can include symbolic imagery (bulls, bears, rockets, moons)

For ENTERTAINMENT (awards, movies, celebrities):
- Red carpet glamour, award moment, or performance shot
- Celebrity faces must match any provided photo references
- Stage lighting, audience reactions, flashbulbs

REQUIREMENTS:
1. Use any provided images as REFERENCE for faces, style, or composition
2. Vertical 9:16 aspect ratio (mobile/TikTok format)
3. 4K cinematic quality - dramatic lighting, sharp details
4. NO text, NO graphics, NO watermarks, NO overlays
5. This frame will be animated into a video - make it dynamic and exciting

Create a single powerful frame that makes viewers stop scrolling."""
