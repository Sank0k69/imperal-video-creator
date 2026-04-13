"""
PCM Module — Process Communication Model analysis and enhancement.
Ensures scripts resonate with all 6 personality types.
"""
from __future__ import annotations
from .base import BaseModule


class PCMModule(BaseModule):
    name = "pcm"
    description = "Analyze and enhance scripts for PCM personality type coverage"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are an expert in the Process Communication Model (PCM) applied to content creation.

The 6 PCM personality types:
1. REBEL — Playful, reactive. Needs: fun, stimulation. Triggers: humor, rebellion, spontaneous energy
2. PERSISTER — Values-driven, opinionated. Needs: recognition of convictions. Triggers: strong opinions, mission-driven language
3. THINKER — Logical, analytical. Needs: recognition of work. Triggers: data, frameworks, step-by-step, cause/effect
4. HARMONIZER — Emotional, warm. Needs: unconditional acceptance. Triggers: emotional stories, empathy, personal connection
5. PROMOTER — Action-oriented, commanding. Needs: excitement. Triggers: direct commands, urgency, bold statements
6. IMAGINER — Visionary, introspective. Needs: solitude/reflection. Triggers: future pacing, visualization, what-if scenarios

Scoring:
- 5-6 types covered = Excellent
- 3-4 types covered = Good
- 0-2 types covered = Needs work

Goal: Every script should cover at LEAST 3 types, ideally 5-6."""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "analyze", "description": "Analyze script for PCM coverage", "params": ["script"]},
            {"name": "enhance", "description": "Enhance script to cover missing types", "params": ["script", "target_types"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "analyze":
            return await self._analyze(params)
        elif action == "enhance":
            return await self._enhance(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _analyze(self, params: dict) -> dict:
        script = params.get("script", "")
        pcm_data = self.load_knowledge("pcm_types.json")
        types_info = pcm_data["types"]
        scoring = pcm_data["scoring"]
        min_types = self.get_config("quality", {}).get("pcm_min_types", 3)

        prompt = f"""Analyze this script for PCM personality type coverage:

SCRIPT:
{script}

For each of the 6 PCM types, identify:
1. Whether it's present (yes/no)
2. Which specific lines/phrases trigger that type
3. How strongly it's represented (weak/medium/strong)

PCM Types reference:
{', '.join(f"{k}: {v['trait']} — triggers: {v['script_triggers']}" for k, v in types_info.items())}

Then provide:
- Total types covered (out of 6)
- Score: {'|'.join(f"{v['label']} ({v['min_types']}+)" for v in scoring.values())}
- Missing types with specific suggestions for adding them
- Minimum required: {min_types}

Output as JSON: {{
  "types_found": {{"rebel": {{"present": bool, "evidence": [...], "strength": "..."}}, ...}},
  "total_covered": int,
  "score_label": "...",
  "missing": ["type1", ...],
  "suggestions": [{{"type": "...", "suggestion": "..."}}],
  "passes_minimum": bool
}}"""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"analysis": response, "min_required": min_types},
            "summary": "PCM analysis complete",
        }

    async def _enhance(self, params: dict) -> dict:
        script = params.get("script", "")
        target_types = params.get("target_types") or []
        pcm_data = self.load_knowledge("pcm_types.json")

        targets_info = ""
        for t in target_types:
            if t in pcm_data["types"]:
                info = pcm_data["types"][t]
                targets_info += f"\n{info['name']}: {info['trait']}. Triggers: {info['script_triggers']}. Caption templates: {info['caption_templates']}"

        prompt = f"""Enhance this script to better cover these PCM personality types:

SCRIPT:
{script}

TARGET TYPES TO ADD/STRENGTHEN:
{targets_info if targets_info else 'All missing types — analyze first, then add what is missing.'}

Rules:
- Keep the original message and structure intact
- Weave in PCM triggers naturally (don't force them)
- Each addition should feel like it belongs
- Mark enhanced sections with [PCM: type_name] annotations

Output the enhanced script with annotations, plus a summary of changes made."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"enhanced_script": response, "target_types": target_types},
            "summary": f"Enhanced script for PCM types: {', '.join(target_types) if target_types else 'auto-detected'}",
        }
