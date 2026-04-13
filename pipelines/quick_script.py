"""
Quick Script Pipeline — fast topic-to-script workflow.
Hooks → Script → CTA. Skip framing/packaging for speed.
"""
from __future__ import annotations
from .base import BasePipeline


class QuickScriptPipeline(BasePipeline):
    name = "quick_script"
    description = "Fast script creation: topic → hooks → script → CTA"
    steps = ["hooks", "scripting", "cta"]

    async def run(self, params: dict) -> dict:
        topic = params.get("topic", "")
        format_type = params.get("format_type", "viral")
        results = {}

        # Step 1: Generate hooks
        hooks = self.module("hooks")
        hook_result = await hooks.execute("generate", {
            "topic": topic, "count": 3,
        })
        results["hooks"] = hook_result

        # Step 2: Write script (Tier 1 for speed)
        scripting = self.module("scripting")
        script_result = await scripting.execute("write", {
            "topic": topic,
            "tier": 1,
            "format_type": format_type,
            "duration": "short",
        })
        results["script"] = script_result

        # Step 3: Generate CTA
        cta = self.module("cta")
        cta_result = await cta.execute("generate", {
            "context": topic, "goal": "engage",
        })
        results["cta"] = cta_result

        return {
            "status": "ok",
            "data": {
                "topic": topic,
                "pipeline": "quick_script",
                "steps_completed": len(results),
                "results": results,
            },
            "summary": f"Quick script ready for '{topic}'",
        }
