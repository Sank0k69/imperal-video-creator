"""
Packaging Module — Want vs Need framework for titles and thumbnails.
"""
from __future__ import annotations
from .base import BaseModule


class PackagingModule(BaseModule):
    name = "packaging"
    description = "Create titles and thumbnail strategies using Want vs Need framework"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a video packaging expert.

CORE PRINCIPLE: Position content as what market WANTS (title/thumbnail) → deliver what they NEED (video).

Title Rules:
- Max 55 characters
- Must include: curiosity + end outcome/goal
- Good: drama, negativity, simplicity
- Clickbait + deliver value = NOT clickbait

Thumbnail Rules:
- Max 4 words of text
- Text reinforces storyline (does NOT rewrite title)
- Green/Blue = higher click rate
- Must portray story of the video
- Face on thumbnail (brand recognition)
- Eye contact = talking to viewer
- Exaggeration welcome (but deliver)

Two styles:
- NICHED: Clearly identifies niche → search + recommended
- SHAREABILITY: Attaches to broader trend/celebrity/culture → new audiences"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "package", "description": "Create title + thumbnail strategy", "params": ["concept", "style"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "package":
            return await self._package(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _package(self, params: dict) -> dict:
        concept = params.get("concept", "")
        style = params.get("style", "niched")
        niche = self.get_config("niche", "")

        rules = self.load_knowledge("packaging_rules.json")
        title_rules = rules.get("title_rules", {})
        thumb_rules = rules.get("thumbnail_rules", {})

        prompt = f"""Package this video concept for maximum CTR:

CONCEPT: {concept}
STYLE: {style}
NICHE: {niche or 'General'}

Generate:

1. TITLES (5 options):
   Rules: {title_rules}
   Each must be under {title_rules.get('max_chars', 55)} chars.
   Rate each for: curiosity (1-5), clarity (1-5), emotion (1-5)

2. THUMBNAIL CONCEPTS (for top 3 titles):
   Rules: {thumb_rules}
   For each: text ({thumb_rules.get('max_words', 4)} words max), visual description, color scheme, emotion conveyed

3. WANT vs NEED MAPPING:
   - What the TITLE promises (the WANT)
   - What the VIDEO delivers (the NEED)
   - How they connect (the fulfillment)

Output as structured JSON."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"packaging": response, "concept": concept, "style": style},
            "summary": f"Created packaging for: '{concept[:50]}...'",
        }
