"""
Iteration Module — Performance tracking and content iteration.
Post → Cook 10h → Track → Analyze → Iterate.
"""
from __future__ import annotations
from .base import BaseModule


class IterationModule(BaseModule):
    name = "iteration"
    description = "Track performance and suggest iterations for content improvement"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a content performance analyst using the Creator Monetize iteration methodology.

Core principle: Content creation is a SYSTEM, not guesswork.
1. Post content
2. Let it cook for 10 hours
3. Track metrics
4. Analyze what worked/failed
5. Iterate — do it again but better

Key metrics:
- Average View Duration (most important for algorithm)
- Click Through Rate (CTR) — title/thumbnail effectiveness
- Retention curve — where do viewers drop off?
- Engagement rate — likes/comments/shares vs views
- Conversion — did CTA work?

Algorithm equation: Grab Attention + Hold Attention = Mass Reach
30% retention increase = difference between 296K and 1.3M views.

Never optimize for vanity metrics (total views without quality).
Always ask: did the content attract the RIGHT audience?"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "track", "description": "Record performance metrics", "params": ["content_id", "metrics"]},
            {"name": "analyze", "description": "Analyze performance and suggest iterations", "params": ["content_id", "period"]},
            {"name": "compare", "description": "Compare two content pieces", "params": ["content_id_a", "content_id_b"]},
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "track":
            return await self._track(params)
        elif action == "analyze":
            return await self._analyze(params)
        elif action == "compare":
            return await self._compare(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _track(self, params: dict) -> dict:
        content_id = params.get("content_id", "")
        metrics = params.get("metrics", {})

        existing = await self.load(f"metrics/{content_id}", {"history": []})
        existing["history"].append(metrics)
        existing["latest"] = metrics
        await self.save(f"metrics/{content_id}", existing)

        return {
            "status": "ok",
            "data": {"content_id": content_id, "metrics": metrics, "total_entries": len(existing["history"])},
            "summary": f"Tracked metrics for content '{content_id}'",
        }

    async def _analyze(self, params: dict) -> dict:
        content_id = params.get("content_id", "")
        period = params.get("period", "week")

        if content_id:
            data = await self.load(f"metrics/{content_id}", {})
            context = f"Content '{content_id}' metrics: {data}"
        else:
            all_metrics = await self.list_items("metrics/")
            context = f"All tracked content ({len(all_metrics)} pieces) over {period}"

        formats_data = self.load_knowledge("video_formats.json")
        algorithm = formats_data.get("algorithm_principles", {})

        prompt = f"""Analyze content performance and suggest iterations:

DATA:
{context}

ALGORITHM PRINCIPLES:
{algorithm}

Analyze:
1. What's working? (high retention, good CTR, engagement)
2. What's failing? (drop-off points, low CTR, wrong audience)
3. Pattern recognition (which hook types perform best, which formats, which topics)
4. Specific iteration suggestions for next content

Output JSON: {{
  "performance_summary": "...",
  "working": ["..."],
  "failing": ["..."],
  "patterns": ["..."],
  "iterations": [{{"suggestion": "...", "based_on": "...", "expected_impact": "..."}}],
  "next_content_recommendations": ["..."]
}}"""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"analysis": response, "period": period},
            "summary": f"Performance analysis complete for {period}",
        }

    async def _compare(self, params: dict) -> dict:
        id_a = params.get("content_id_a", "")
        id_b = params.get("content_id_b", "")

        data_a = await self.load(f"metrics/{id_a}", {})
        data_b = await self.load(f"metrics/{id_b}", {})

        prompt = f"""Compare performance of two content pieces:

CONTENT A ({id_a}): {data_a}
CONTENT B ({id_b}): {data_b}

Compare:
1. Retention (who held attention better?)
2. CTR (which title/thumbnail won?)
3. Engagement (which drove more interaction?)
4. Audience quality (right people?)

What can we learn from the winner? What should we replicate?

Output JSON with comparison table and lessons."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"comparison": response, "content_a": id_a, "content_b": id_b},
            "summary": f"Compared '{id_a}' vs '{id_b}'",
        }
