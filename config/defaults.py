"""
Default configuration for Video Creator extension.
All values can be overridden per-user via ctx.config.
"""

DEFAULTS = {
    # User's niche/industry
    "niche": "",
    # Target audience description
    "target_audience": "",
    # Brand voice keywords
    "brand_voice": [],
    # Preferred content language
    "language": "en",

    # HeyGen API key for video production
    "heygen_api_key": "",

    # Platform settings
    "platforms": {
        "youtube": {"enabled": False, "api_key": ""},
        "tiktok": {"enabled": False, "api_key": ""},
        "instagram": {"enabled": False, "api_key": ""},
        "linkedin": {"enabled": False, "api_key": ""},
    },

    # Content preferences
    "content": {
        "default_post_time": "20:00",
        "timezone": "UTC",
        "min_word_count": 150,
        "max_hashtags": 4,
        "caption_style": "curiosity",  # curiosity | pcm | custom
    },

    # Quality gates
    "quality": {
        "pcm_min_types": 3,        # min PCM personality types per script
        "hook_max_seconds": 3,      # hook must grab in N seconds
        "title_max_chars": 55,      # YouTube title limit
        "thumbnail_max_words": 4,   # words on thumbnail
    },

    # Module toggles — enable/disable individually
    "modules": {
        "ideation": True,
        "framing": True,
        "packaging": True,
        "hooks": True,
        "scripting": True,
        "pcm": True,
        "captions": True,
        "cta": True,
        "publishing": True,
        "iteration": True,
        "market_research": True,
        "funnel_copy": True,
        "email_sequences": True,
        "sales": True,
        "launch": True,
        "video_production": True,
    },
}
