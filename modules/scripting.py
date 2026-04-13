"""
Scripting Module — Hook-Body-CTA architecture with Tier 1 and Tier 2 structures.
"""
from __future__ import annotations
from .base import BaseModule


class ScriptingModule(BaseModule):
    name = "scripting"
    description = "Write complete video scripts using Hook-Body-CTA architecture"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are an expert video scriptwriter using the Creator Monetize scripting methodology.

Every script has 3 mandatory components:
1. HOOK (first 3 seconds) — Grab attention, promise massive payoff
2. BODY — Hold attention so they watch until end
3. CTA — Call to action at the end

Two script tiers:
- TIER 1 (Simple): Hook → P1 → P2 → P3 → CTA
- TIER 2 (Advanced): Hook → P1(Setup/Stress/Payoff) → P2(S/S/P) → P3(S/S/P) → P4(S/S/P) → CTA
  Each point has nested tension: Setup introduces → Stress builds stakes → Payoff resolves + transitions

Three short-form templates:
- VIRAL: Negative Hook → Alternative Options → Promise → Solutions → CTA
- PITCH: Problem → Opportunity → Practical Steps → Promise
- FALSE STATEMENT: False Statement → Turning Point → Social Proof → Disprove → More Proof → CTA

Quality checklist before output:
- Covers 3-6 PCM personality types?
- Sounds natural read aloud?
- Worth $5?
- Would you watch on FYP?"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "write", "description": "Write a complete video script", "params": ["topic", "hook", "tier", "format_type", "duration"]},
            {"name": "rewrite", "description": "Rewrite/improve existing script", "params": ["script", "feedback"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "write":
            return await self._write(params)
        elif action == "rewrite":
            return await self._rewrite(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _write(self, params: dict) -> dict:
        topic = params.get("topic", "")
        hook = params.get("hook", "")
        tier = params.get("tier", 1)
        format_type = params.get("format_type", "viral")
        duration = params.get("duration", "short")

        structures = self.load_knowledge("script_structures.json")
        tier_info = structures["tiers"].get(str(tier), structures["tiers"]["1"])
        template_info = structures["short_form_templates"].get(format_type, structures["short_form_templates"]["viral"])

        niche = self.get_config("niche", "")
        audience = self.get_config("target_audience", "")
        voice = self.get_config("brand_voice", [])

        duration_guide = {
            "short": "60 seconds (~150 words). Punchy, no filler.",
            "medium": "3-5 minutes (~500-800 words). Room for stories and examples.",
            "long": "10+ minutes (~1500+ words). Deep dive with multiple Setup/Stress/Payoff loops.",
        }

        prompt = f"""Write a complete video script:

TOPIC: {topic}
{"HOOK (pre-written): " + hook if hook else "Generate a hook (first 3 seconds)."}
TIER: {tier_info['name']} — {tier_info['description']}
FORMAT: {template_info['name']} — Flow: {' → '.join(template_info['flow'])}
DURATION: {duration} — {duration_guide.get(duration, duration_guide['short'])}
NICHE: {niche or 'Not specified'}
AUDIENCE: {audience or 'General'}
BRAND VOICE: {', '.join(voice) if voice else 'Confident, authentic, value-driven'}

STRUCTURE TO FOLLOW:
{tier_info['guidance']}

QUALITY CHECKLIST (verify before outputting):
{structures['scripting_process']['stages'][-2]['steps']}

Output the script with clear section markers:
[HOOK]
[BODY - P1] (with Setup/Stress/Payoff if Tier 2)
[BODY - P2]
[BODY - P3]
[BODY - P4] (if Tier 2)
[CTA]

Also provide:
- Estimated word count
- Estimated duration
- Editing notes (SFX, visuals, transitions)
- PCM types covered

Output as JSON with 'script' (the full text), 'sections' (array of labeled sections), 'metadata' (word count, duration, pcm_types, editing_notes)."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)

        # Save to store for tracking
        await self.save(f"scripts/{topic[:30].replace(' ', '_')}", {
            "topic": topic, "tier": tier, "format": format_type,
            "duration": duration, "script": response,
        })

        return {
            "status": "ok",
            "data": {"script": response, "topic": topic, "tier": tier, "format": format_type},
            "summary": f"Wrote {duration} Tier {tier} '{format_type}' script about '{topic}'",
        }

    async def _rewrite(self, params: dict) -> dict:
        script = params.get("script", "")
        feedback = params.get("feedback", "")

        prompt = f"""Rewrite this video script based on the feedback:

CURRENT SCRIPT:
{script}

FEEDBACK:
{feedback}

Apply the feedback while maintaining:
- Hook-Body-CTA structure
- PCM personality type diversity
- Natural spoken tone
- The original topic and message

Output the complete rewritten script in the same format."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"script": response, "feedback": feedback},
            "summary": "Script rewritten with feedback applied",
        }
