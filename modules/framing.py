"""
Framing Module — 4-step idea-to-video direction pipeline.
Transforms vague ideas into specific, audience-targeted video concepts.
"""
from __future__ import annotations
from .base import BaseModule


class FramingModule(BaseModule):
    name = "framing"
    description = "Transform raw ideas into directed video concepts"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a video content strategist using the 4-Step Framing System.

Every idea must go through 4 steps:
1. VIDEO FRAMING — The raw idea (broad topic)
2. PACKAGING FRAMING — Create the title (what market WANTS to see)
3. DIRECTIONAL FRAMING — Add specificity (who, circumstances, unique angle)
4. GRAND PAYOFF — The overarching question the viewer MUST stay to answer

Framing Checklist (all 4 must pass):
- I am passionate about this specific angle
- It targets the client avatar
- It evokes emotional response (fear, anger, desire, hope)
- It opens multiple curiosity gaps (not answerable by simple Google search)

Also determine scripting pre-work:
- Target: who is the audience
- Transformation: what change will they experience
- Stakes: what happens if they don't act
- Objection: what might prevent them from believing"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "frame", "description": "Run 4-step framing on an idea", "params": ["idea", "avatar"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "frame":
            return await self._frame(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _frame(self, params: dict) -> dict:
        idea = params.get("idea", "")
        avatar = params.get("avatar", "") or self.get_config("target_audience", "")
        niche = self.get_config("niche", "")

        packaging = self.load_knowledge("packaging_rules.json")
        framing_system = packaging.get("framing_system", {})

        prompt = f"""Apply the 4-Step Framing System to this raw idea:

RAW IDEA: {idea}
NICHE: {niche or 'Not specified'}
TARGET AVATAR: {avatar or 'General audience'}

Execute each step:

STEP 1 — VIDEO FRAMING:
Restate the broad idea clearly.

STEP 2 — PACKAGING FRAMING:
Create 3 title options (max 55 chars each). Each should call out what the market WANTS.
Apply rules: curiosity, end outcome/goal, drama welcome, negativity welcome, simplicity.

STEP 3 — DIRECTIONAL FRAMING:
For each title, add hyper-specific direction. Who exactly? What circumstances? What unique angle?

STEP 4 — GRAND PAYOFF:
For each direction, identify THE overarching question the viewer has when they click.
This is the reason they MUST stay until the end.

FRAMING CHECKLIST (evaluate each option):
{framing_system.get('checklist', [])}

SCRIPTING PRE-WORK (for the best option):
- Target: who is the audience
- Transformation: what change will they experience
- Stakes: what happens if they don't act
- Objection: what might prevent them from believing

Output as structured JSON with 'options' array and 'recommended' index."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"framing": response, "original_idea": idea},
            "summary": f"Framed idea into directed video concept: '{idea[:50]}...'",
        }
