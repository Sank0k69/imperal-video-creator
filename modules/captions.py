"""
Captions Module — Curiosity and PCM caption generation.
"""
from __future__ import annotations
from .base import BaseModule


class CaptionsModule(BaseModule):
    name = "captions"
    description = "Generate post captions using curiosity loops and PCM targeting"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a social media caption specialist.

Two caption systems:
1. CURIOSITY CAPTIONS — Create curiosity loops that increase watch time. Short, punchy, emoji-enhanced.
2. PCM CAPTIONS — Target specific personality types for broader appeal.

Caption rules:
- Short and punchy (1-2 lines max)
- Creates desire to watch/read
- Uses emojis for context (not decoration)
- Matches the content's energy
- Never reveals the full value (leave curiosity open)"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "generate", "description": "Generate captions", "params": ["topic", "style", "count"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "generate":
            return await self._generate(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _generate(self, params: dict) -> dict:
        topic = params.get("topic", "")
        style = params.get("style", "curiosity")
        count = params.get("count", 5)

        captions_data = self.load_knowledge("caption_templates.json")
        templates = captions_data["styles"].get(style, captions_data["styles"]["curiosity"])

        prompt = f"""Generate {count} captions for this video topic:

TOPIC: {topic}
STYLE: {style} — {templates['description']}
TEMPLATE EXAMPLES: {templates.get('templates', ['See PCM types for templates'])}

Requirements:
- Each caption should create a curiosity loop
- Max 2 lines
- Include 1-2 relevant emojis
- Never reveal the full value
- Match the topic's energy

Output as JSON array: [{{"caption": "...", "style": "...", "target_pcm": "..."}}]"""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"captions": response, "topic": topic, "style": style},
            "summary": f"Generated {count} {style} captions for '{topic}'",
        }
