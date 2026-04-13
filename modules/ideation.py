"""
Ideation Module — Perfect Idea Zone methodology.
Generates and classifies video content ideas.
"""
from __future__ import annotations
from .base import BaseModule


class IdeationModule(BaseModule):
    name = "ideation"
    description = "Generate and classify video content ideas"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a video content ideation expert using the Perfect Idea Zone methodology.

A PERFECT idea lives at the intersection of:
1. Ideas the creator understands deeply (can explain for 5-20 minutes)
2. Ideas the market finds valuable (audience will care)

If BOTH are true → Perfect Idea. Otherwise → Sub-optimal.

Methods available:
- Commence: Systematic brainstorm from environment, competitors, books, movies, experiences
- Snatch & Twirl: Find existing viral ideas, grab the core concept, add unique spin
- Audience-Based: Use audience questions, comments, DMs as idea sources

Always output ideas with:
- Title (concise, compelling)
- Core angle (what makes this specific)
- Target audience (who cares most)
- Estimated engagement potential (low/medium/high)
- Classification (perfect/sub-optimal + reasoning)"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "generate", "description": "Generate video ideas", "params": ["topic", "count", "method"]},
            {"name": "classify", "description": "Classify idea as perfect/sub-optimal", "params": ["idea"]},
            {"name": "bank_add", "description": "Add idea to ideas bank", "params": ["idea"]},
            {"name": "bank_list", "description": "List saved ideas", "params": []},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "generate":
            return await self._generate(params)
        elif action == "classify":
            return await self._classify(params)
        elif action == "bank_add":
            return await self._bank_add(params)
        elif action == "bank_list":
            return await self._bank_list()
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _generate(self, params: dict) -> dict:
        topic = params.get("topic", "") or self.get_config("niche", "general")
        count = params.get("count", 10)
        method = params.get("method", "mixed")

        methods_knowledge = self.load_knowledge("ideation_methods.json")
        method_details = methods_knowledge.get("methods", {})

        method_context = ""
        if method == "mixed":
            method_context = "Use a MIX of all ideation methods: Commence brainstorming, Snatch & Twirl from competitors, and Audience-Based questions."
        elif method in method_details:
            m = method_details[method]
            method_context = f"Use the '{m['name']}' method: {m.get('description', '')}. Steps: {', '.join(m.get('steps', []))}"

        niche = self.get_config("niche", "")
        audience = self.get_config("target_audience", "")

        prompt = f"""Generate {count} video content ideas about: {topic}

Niche context: {niche or 'Not specified — use the topic as niche'}
Target audience: {audience or 'General audience interested in this topic'}

Method: {method_context}

For each idea provide:
1. Title (compelling, under 55 chars)
2. Core angle (1 sentence — what makes this specific)
3. Hook potential (which hook type from: desirable, social_proof, controversial, secret, negative, quick_solution, lesson)
4. Format (sitting_static, walkthrough, vlog_style, text_overlay)
5. Classification: PERFECT or SUB-OPTIMAL (with reasoning)

Output as structured JSON array."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"ideas": response, "method": method, "topic": topic, "count": count},
            "summary": f"Generated {count} video ideas about '{topic}' using {method} method",
        }

    async def _classify(self, params: dict) -> dict:
        idea = params.get("idea", "")
        niche = self.get_config("niche", "")
        audience = self.get_config("target_audience", "")

        methods_knowledge = self.load_knowledge("ideation_methods.json")
        classification = methods_knowledge.get("classification", {})

        prompt = f"""Classify this video idea using the Perfect Idea Zone framework:

Idea: {idea}
Creator's niche: {niche or 'Not specified'}
Target audience: {audience or 'General'}

Perfect Idea Zone criteria:
- PERFECT: {classification.get('perfect', {}).get('criteria', [])}
- SUB-OPTIMAL: {classification.get('sub_optimal', {}).get('criteria', [])}

Evaluate:
1. Can the creator explain this for 5-20 minutes? (depth test)
2. Does the market find value in this? (demand test)
3. Does it evoke emotion? (engagement test)
4. Does it open curiosity gaps? (retention test)

Output JSON: {{"classification": "perfect"|"sub_optimal", "reasoning": "...", "improvement_suggestions": [...], "score": 1-10}}"""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"classification": response, "idea": idea},
            "summary": f"Classified idea: '{idea[:50]}...'",
        }

    async def _bank_add(self, params: dict) -> dict:
        idea = params.get("idea", {})
        bank = await self.load("ideas_bank", [])
        bank.append(idea)
        await self.save("ideas_bank", bank)
        return {
            "status": "ok",
            "data": {"total_ideas": len(bank)},
            "summary": f"Added idea to bank. Total: {len(bank)}",
        }

    async def _bank_list(self) -> dict:
        bank = await self.load("ideas_bank", [])
        return {
            "status": "ok",
            "data": {"ideas": bank, "total": len(bank)},
            "summary": f"{len(bank)} ideas in bank",
        }
