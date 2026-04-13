"""
Batch Content Pipeline — create scripts for multiple topics at once.
Runs quick_script pipeline for each topic in parallel concept.
"""
from __future__ import annotations
from .base import BasePipeline


class BatchContentPipeline(BasePipeline):
    name = "batch_content"
    description = "Batch create scripts for multiple topics"
    steps = ["batch_scripting"]

    async def run(self, params: dict) -> dict:
        topics = params.get("topics", [])
        format_type = params.get("format_type", "viral")

        if not topics:
            return {"status": "error", "data": None, "summary": "No topics provided"}

        results = {}
        for i, topic in enumerate(topics):
            # Run quick pipeline for each topic
            scripting = self.module("scripting")
            hooks = self.module("hooks")
            cta = self.module("cta")

            hook_result = await hooks.execute("generate", {
                "topic": topic, "count": 1,
            })

            script_result = await scripting.execute("write", {
                "topic": topic,
                "tier": 1,
                "format_type": format_type,
                "duration": "short",
            })

            cta_result = await cta.execute("generate", {
                "context": topic, "goal": "engage",
            })

            results[f"topic_{i}"] = {
                "topic": topic,
                "hooks": hook_result,
                "script": script_result,
                "cta": cta_result,
            }

        return {
            "status": "ok",
            "data": {
                "pipeline": "batch_content",
                "total_topics": len(topics),
                "results": results,
            },
            "summary": f"Batch complete: {len(topics)} scripts created",
        }
