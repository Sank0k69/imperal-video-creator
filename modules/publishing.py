"""
Publishing Module — 6-step pre-publishing checklist.
"""
from __future__ import annotations
from .base import BaseModule


class PublishingModule(BaseModule):
    name = "publishing"
    description = "Pre-publishing checklist and quality gate"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a content publishing quality assurance specialist.

6-step pre-publishing checklist:
1. Upload Times — Optimal time for highest active users
2. Hashtags — 3-4 per video, specific to each video
3. Sounds/Music — Viral or relevant sounds
4. Captions — Curiosity or PCM captions (MUST HAVE)
5. Story Boost — Whether to repost on story
6. Upload Quality — Always max resolution

YouTube-specific:
- Description (SEO optimized)
- Tags
- End screen (next video + subscribe)
- Cards at key moments

Quality gate self-check:
- Worth $5?
- Actually thought out?
- Proud of it?
- Would watch on FYP?
- Can improve?"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "check", "description": "Run pre-publishing checklist", "params": ["content"]},
            {"name": "generate_metadata", "description": "Generate platform metadata", "params": ["content", "platform"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "check":
            return await self._check(params)
        elif action == "generate_metadata":
            return await self._generate_metadata(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _check(self, params: dict) -> dict:
        content = params.get("content", {})
        checklist_data = self.load_knowledge("content_checklist.json")
        steps = checklist_data["pre_publish"]["steps"]
        quality_gate = checklist_data["quality_gate"]

        prompt = f"""Run the pre-publishing checklist on this content:

CONTENT:
{content}

CHECKLIST STEPS:
{steps}

QUALITY GATE:
{quality_gate}

For each step evaluate:
- Status: PASS / FAIL / MISSING
- What's provided vs what's needed
- Specific fix if FAIL

For quality gate, answer each self-check question honestly.

Output JSON: {{
  "checklist": [{{"step": "...", "status": "pass|fail|missing", "note": "..."}}],
  "quality_gate": [{{"question": "...", "answer": "...", "pass": bool}}],
  "overall": "ready|needs_work",
  "blockers": ["..."],
  "suggestions": ["..."]
}}"""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"checklist": response, "content_summary": str(content)[:100]},
            "summary": "Pre-publish checklist completed",
        }

    async def _generate_metadata(self, params: dict) -> dict:
        content = params.get("content", {})
        platform = params.get("platform", "youtube")

        prompt = f"""Generate publishing metadata for {platform}:

CONTENT:
{content}

Generate platform-specific metadata:
- Description (SEO optimized for {platform})
- Tags/Hashtags (3-4, specific to this content)
- Suggested posting time
- Category/Topic classification

Output as JSON."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"metadata": response, "platform": platform},
            "summary": f"Generated {platform} metadata",
        }
