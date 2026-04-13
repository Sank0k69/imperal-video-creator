"""
CTA Module — Call-to-Action generation with 4 goal categories.
"""
from __future__ import annotations
from .base import BaseModule


class CTAModule(BaseModule):
    name = "cta"
    description = "Generate CTAs for video content across 4 goal categories"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a CTA specialist for video content.

Every CTA follows a 5-part structure:
1. Relevance hook — tie to video topic
2. Benefit — state what they gain
3. Clear step — spell out exactly what to do
4. Urgency/positioning — light encouragement to act now
5. Reassurance — safe, no-pressure framing

4 CTA categories:
- ENGAGE: Like, comment, subscribe — increase engagement metrics
- REDIRECT: Direct to another video — increase session time
- LINK: Description link — drive traffic to external resource
- MANYCHAT: Comment trigger — automated DM delivery"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "generate", "description": "Generate CTA for content", "params": ["context", "goal", "platform"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "generate":
            return await self._generate(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _generate(self, params: dict) -> dict:
        context = params.get("context", "")
        goal = params.get("goal", "engage")
        platform = params.get("platform", "youtube")

        cta_data = self.load_knowledge("cta_templates.json")
        category = cta_data["categories"].get(goal, cta_data["categories"]["engage"])
        structure = cta_data["structure"]

        prompt = f"""Generate a CTA for this video:

VIDEO CONTEXT: {context}
GOAL: {category['name']} — {category['goal']}
PLATFORM: {platform}
TEMPLATES: {category['templates']}

CTA Structure (must follow all 5 parts):
{structure['parts']}

Requirements:
- Natural spoken tone
- Specific to the video topic
- Not pushy or desperate
- Platform-appropriate (YouTube/TikTok/Instagram/LinkedIn)

Output JSON: {{
  "cta_text": "The full CTA ready to speak",
  "goal": "{goal}",
  "structure_breakdown": {{
    "relevance_hook": "...",
    "benefit": "...",
    "clear_step": "...",
    "urgency": "...",
    "reassurance": "..."
  }},
  "platform_notes": "..."
}}"""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"cta": response, "goal": goal, "platform": platform},
            "summary": f"Generated '{goal}' CTA for {platform}",
        }
