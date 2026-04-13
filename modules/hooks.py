"""
Hooks Module — 7 psychological trigger types for video hooks.
"""
from __future__ import annotations
from .base import BaseModule


class HooksModule(BaseModule):
    name = "hooks"
    description = "Generate video hooks from 7 psychological trigger types"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a video hook specialist. You know that the HOOK is the most important part of any video — the first 3 seconds determine everything.

The hook must:
1. GRAB attention instantly (3 seconds)
2. Promise a massive payoff at the end
3. Create curiosity that can only be resolved by watching

7 Hook Types (each targets a different psychological trigger):
- DESIRABLE: Appeals to aspirational outcome
- SOCIAL PROOF: Leverages personal results as credibility
- CONTROVERSIAL: Challenges beliefs to create engagement
- SECRET: Creates forbidden-knowledge curiosity
- NEGATIVE: Calls out failure to create urgency
- QUICK SOLUTION: Rejects old way, offers new solution
- LESSON: Positions creator as experienced guide

Every hook you write must feel natural when spoken aloud.
Never be generic. Always be specific to the topic."""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "generate", "description": "Generate hooks for a topic", "params": ["topic", "types", "count"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "generate":
            return await self._generate(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _generate(self, params: dict) -> dict:
        topic = params.get("topic", "")
        requested_types = params.get("types") or list(self.load_knowledge("hook_templates.json")["types"].keys())
        count = params.get("count", 5)

        templates = self.load_knowledge("hook_templates.json")
        niche = self.get_config("niche", "")
        audience = self.get_config("target_audience", "")

        types_context = ""
        for t in requested_types:
            if t in templates["types"]:
                info = templates["types"][t]
                types_context += f"\n{info['name']} ({info['trigger']}):\nTemplates: {info['templates']}\n"

        prompt = f"""Generate {count} video hooks for this topic:

TOPIC: {topic}
NICHE: {niche or 'Not specified'}
TARGET AUDIENCE: {audience or 'General'}

Use these hook types:
{types_context}

Requirements:
- Each hook must work in the FIRST 3 SECONDS of a video
- Must feel natural spoken aloud (not robotic or written)
- Must be specific to the topic (not generic)
- Must create a curiosity loop that can only be resolved by watching
- Include the hook type label for each

For each hook provide:
1. The hook text (ready to speak)
2. Hook type used
3. Why it works (1 sentence)
4. Estimated retention impact (low/medium/high)

Output as JSON array."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"hooks": response, "topic": topic, "types_used": requested_types},
            "summary": f"Generated {count} hooks for '{topic}'",
        }
