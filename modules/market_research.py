"""
Market Research Module — GSB analysis, client avatars, trajectory classification.
Uses Creator Monetize methodology for market selection and audience profiling.
"""
from __future__ import annotations
from .base import BaseModule


class MarketResearchModule(BaseModule):
    name = "market_research"
    description = "Market research, client avatars, GSB analysis"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are an expert market researcher using the Creator Monetize methodology.

Your core frameworks:
1. GSB (Gold-Silver-Bronze) Analysis — classify content tiers by quality, depth, and monetization potential. Gold = premium authority content, Silver = solid mid-tier, Bronze = entry-level accessible content. Compare creator's current position against each tier.

2. Client Avatar Building — use the 18-question deep avatar framework to build a detailed profile of the ideal client. Cover demographics, psychographics, pain points, desires, objections, buying behavior, content consumption habits, and transformation goals.

3. The 7 Tenets of Market Selection — evaluate niche viability through: market size, purchasing power, accessibility, passion level, competition landscape, expertise depth, and growth trajectory.

4. Designating Trajectory System — classify creators into 1 of 8 pathways based on current position (followers, platform, offer status, niche type) and generate a tailored 28-day roadmap for each pathway.

5. Market Research Questions — generate structured questionnaires to validate assumptions about target market before building offers.

Always ground your analysis in data and frameworks. Never guess — if information is insufficient, ask for more details. Output structured, actionable insights that a creator can immediately use to make decisions."""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {
                "name": "gsb_analyze",
                "description": "Run Gold Silver Bronze analysis",
                "params": ["niche", "platform"],
            },
            {
                "name": "build_avatar",
                "description": "Build client avatar using 18-question framework",
                "params": ["niche", "product"],
            },
            {
                "name": "classify_trajectory",
                "description": "Classify creator into 1 of 8 pathways",
                "params": ["followers_count", "platform", "has_offer", "niche_type"],
            },
            {
                "name": "research_questions",
                "description": "Generate market research questionnaire",
                "params": ["niche"],
            },
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "gsb_analyze":
            return await self._gsb_analyze(params)
        elif action == "build_avatar":
            return await self._build_avatar(params)
        elif action == "classify_trajectory":
            return await self._classify_trajectory(params)
        elif action == "research_questions":
            return await self._research_questions(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _gsb_analyze(self, params: dict) -> dict:
        niche = params.get("niche", "") or self.get_config("niche", "general")
        platform = params.get("platform", "") or self.get_config("platform", "youtube")

        knowledge = self.load_knowledge("market_research.json")
        gsb_framework = knowledge.get("gsb_framework", {})

        prompt = f"""Run a complete Gold-Silver-Bronze analysis for:

Niche: {niche}
Platform: {platform}

GSB Framework:
{gsb_framework}

For each tier (Gold, Silver, Bronze), analyze:
1. Content quality expectations
2. Production value needed
3. Audience size and engagement benchmarks
4. Monetization potential and methods
5. Time investment required
6. Skills and resources needed
7. Example content formats

Then provide:
- Current tier recommendation for a new creator in this niche
- Progression roadmap from Bronze to Gold
- Quick wins for each tier

Output as structured JSON with keys: gold, silver, bronze, recommendation, roadmap, quick_wins."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_gsb", {"niche": niche, "platform": platform, "result": response})
        return {
            "status": "ok",
            "data": {"analysis": response, "niche": niche, "platform": platform},
            "summary": f"GSB analysis completed for '{niche}' on {platform}",
        }

    async def _build_avatar(self, params: dict) -> dict:
        niche = params.get("niche", "") or self.get_config("niche", "general")
        product = params.get("product", "") or self.get_config("product", "")

        knowledge = self.load_knowledge("market_research.json")
        avatar_template = knowledge.get("avatar_template", {})
        avatar_questions = knowledge.get("avatar_questions", [])

        prompt = f"""Build a detailed client avatar for:

Niche: {niche}
Product/Offer: {product or 'Not specified — build a general avatar for this niche'}

Avatar Template:
{avatar_template}

Use these 18 core questions as your framework:
{avatar_questions}

Build a complete avatar profile including:
1. Demographics (age, gender, location, income, education, job)
2. Psychographics (values, beliefs, aspirations, fears)
3. Pain points (top 5, ranked by intensity)
4. Dream outcome (vivid description of their ideal state)
5. Current situation (where they are now vs where they want to be)
6. Objections to buying (top 5 with severity rating)
7. Content consumption (platforms, formats, times, influencers they follow)
8. Buying triggers (what pushes them to act)
9. Language patterns (exact phrases they use to describe their problems)
10. Day-in-the-life narrative (morning to night)

Output as structured JSON with all sections clearly labeled."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_avatar", {"niche": niche, "product": product, "result": response})
        return {
            "status": "ok",
            "data": {"avatar": response, "niche": niche, "product": product},
            "summary": f"Client avatar built for '{niche}' — product: '{product or 'general'}'",
        }

    async def _classify_trajectory(self, params: dict) -> dict:
        followers_count = params.get("followers_count", 0)
        platform = params.get("platform", "") or self.get_config("platform", "youtube")
        has_offer = params.get("has_offer", False)
        niche_type = params.get("niche_type", "") or self.get_config("niche", "general")

        pathways = self.load_knowledge("trajectory_pathways.json")

        prompt = f"""Classify this creator into one of the 8 Designating Trajectory pathways:

Creator Profile:
- Followers: {followers_count}
- Platform: {platform}
- Has existing offer: {has_offer}
- Niche type: {niche_type}

Available Pathways:
{pathways}

Steps:
1. Evaluate the creator's current position across all dimensions
2. Match to the most appropriate pathway (1-8)
3. Generate a complete 28-day roadmap specific to their pathway
4. Include daily actions, milestones, and success metrics

Output as structured JSON with keys: pathway_number, pathway_name, reasoning, roadmap_28_day (array of 28 day objects with: day, task, milestone, metric)."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_trajectory", {
            "followers": followers_count,
            "platform": platform,
            "has_offer": has_offer,
            "niche_type": niche_type,
            "result": response,
        })
        return {
            "status": "ok",
            "data": {"classification": response, "followers": followers_count, "platform": platform},
            "summary": f"Creator classified — {followers_count} followers on {platform}, offer: {has_offer}",
        }

    async def _research_questions(self, params: dict) -> dict:
        niche = params.get("niche", "") or self.get_config("niche", "general")

        knowledge = self.load_knowledge("market_research.json")
        research_framework = knowledge.get("research_framework", {})

        prompt = f"""Generate a comprehensive market research questionnaire for:

Niche: {niche}

Research Framework:
{research_framework}

Create questions across these categories:
1. Problem Awareness (5 questions) — do they know they have the problem?
2. Solution Awareness (5 questions) — have they tried solving it?
3. Willingness to Pay (5 questions) — budget, price sensitivity, past purchases
4. Content Preferences (5 questions) — how they learn, what they consume
5. Buying Behavior (5 questions) — where they buy, triggers, timeline
6. Competitive Landscape (5 questions) — who else they follow, alternatives they've tried
7. Dream Outcome (3 questions) — what perfect looks like for them

For each question provide:
- The question itself (conversational tone)
- Why we're asking (internal note)
- Expected insight (what the answer tells us)

Output as structured JSON array grouped by category."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"questionnaire": response, "niche": niche},
            "summary": f"Generated market research questionnaire for '{niche}'",
        }
