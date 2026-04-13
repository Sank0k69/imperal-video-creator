"""
Full Video Pipeline — complete idea-to-publish workflow.
Ideation → Framing → Packaging → Hooks → Script → PCM → Captions → CTA → Checklist
"""
from __future__ import annotations
from .base import BasePipeline


class FullVideoPipeline(BasePipeline):
    name = "full_video"
    description = "Complete video creation: idea → framing → packaging → script → PCM → publish-ready"
    steps = [
        "ideation",
        "framing",
        "packaging",
        "hooks",
        "scripting",
        "pcm_analysis",
        "pcm_enhance",
        "captions",
        "cta",
        "publishing_check",
    ]

    async def run(self, params: dict) -> dict:
        topic = params.get("topic", "")
        tier = params.get("tier", 1)
        format_type = params.get("format_type", "viral")
        results = {}

        # Step 1: Generate ideas from topic (skip if topic is specific enough)
        ideation = self.module("ideation")
        idea_result = await ideation.execute("generate", {
            "topic": topic, "count": 3, "method": "mixed",
        })
        results["ideation"] = idea_result

        # Step 2: Frame the best idea
        framing = self.module("framing")
        frame_result = await framing.execute("frame", {
            "idea": topic,  # Use original topic as the framing input
        })
        results["framing"] = frame_result

        # Step 3: Package — title + thumbnail
        packaging = self.module("packaging")
        package_result = await packaging.execute("package", {
            "concept": topic,
            "style": "niched",
        })
        results["packaging"] = package_result

        # Step 4: Generate hooks
        hooks = self.module("hooks")
        hook_result = await hooks.execute("generate", {
            "topic": topic, "count": 5,
        })
        results["hooks"] = hook_result

        # Step 5: Write script
        scripting = self.module("scripting")
        script_result = await scripting.execute("write", {
            "topic": topic,
            "tier": tier,
            "format_type": format_type,
            "duration": "short" if tier == 1 else "medium",
        })
        results["script"] = script_result

        # Step 6: PCM analysis
        pcm = self.module("pcm")
        script_text = script_result.get("data", {}).get("script", "")
        pcm_result = await pcm.execute("analyze", {"script": script_text})
        results["pcm_analysis"] = pcm_result

        # Step 7: PCM enhancement (if needed)
        pcm_data = pcm_result.get("data", {})
        analysis = pcm_data.get("analysis", "")
        if "needs_work" in str(analysis).lower() or "false" in str(analysis).lower():
            enhance_result = await pcm.execute("enhance", {"script": script_text})
            results["pcm_enhance"] = enhance_result

        # Step 8: Generate captions
        captions = self.module("captions")
        caption_result = await captions.execute("generate", {
            "topic": topic, "style": "mixed", "count": 3,
        })
        results["captions"] = caption_result

        # Step 9: Generate CTA
        cta = self.module("cta")
        cta_result = await cta.execute("generate", {
            "context": topic, "goal": "engage",
        })
        results["cta"] = cta_result

        # Step 10: Pre-publish check
        publishing = self.module("publishing")
        check_result = await publishing.execute("check", {
            "content": {
                "topic": topic,
                "script": script_text,
                "captions": caption_result.get("data"),
                "cta": cta_result.get("data"),
            },
        })
        results["publishing_check"] = check_result

        return {
            "status": "ok",
            "data": {
                "topic": topic,
                "pipeline": "full_video",
                "steps_completed": len(results),
                "results": results,
            },
            "summary": f"Full video pipeline complete for '{topic}': {len(results)} steps executed",
        }
