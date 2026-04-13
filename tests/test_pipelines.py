"""Tests for Pipelines — orchestration layer."""
import pytest
from modules import ALL_MODULES
from pipelines import PipelineRegistry


def _get_module(ctx, name):
    """Module factory for testing."""
    return ALL_MODULES[name](ctx)


@pytest.fixture
def registry(ctx):
    return PipelineRegistry(ctx, _get_module)


class TestPipelineRegistry:

    def test_list_pipelines(self, registry):
        pipelines = registry.list_pipelines()
        assert len(pipelines) == 3
        names = [p["name"] for p in pipelines]
        assert "full_video" in names
        assert "quick_script" in names
        assert "batch_content" in names

    def test_get_unknown_pipeline(self, registry):
        with pytest.raises(ValueError):
            registry.get("nonexistent")

    def test_pipeline_caching(self, registry):
        p1 = registry.get("quick_script")
        p2 = registry.get("quick_script")
        assert p1 is p2


class TestQuickScript:

    @pytest.mark.asyncio
    async def test_run(self, registry):
        pipeline = registry.get("quick_script")
        result = await pipeline.run({"topic": "NVMe speed benefits"})
        assert result["status"] == "ok"
        assert result["data"]["pipeline"] == "quick_script"
        assert result["data"]["steps_completed"] == 3

    @pytest.mark.asyncio
    async def test_steps_list(self, registry):
        pipeline = registry.get("quick_script")
        assert pipeline.get_steps() == ["hooks", "scripting", "cta"]


class TestFullVideo:

    @pytest.mark.asyncio
    async def test_run(self, registry):
        pipeline = registry.get("full_video")
        result = await pipeline.run({
            "topic": "Why your website is slow",
            "tier": 1,
            "format_type": "viral",
        })
        assert result["status"] == "ok"
        assert result["data"]["pipeline"] == "full_video"
        assert result["data"]["steps_completed"] >= 9  # At least 9 steps (pcm_enhance conditional)

    @pytest.mark.asyncio
    async def test_steps_list(self, registry):
        pipeline = registry.get("full_video")
        assert len(pipeline.get_steps()) == 10


class TestBatchContent:

    @pytest.mark.asyncio
    async def test_run(self, registry):
        pipeline = registry.get("batch_content")
        result = await pipeline.run({
            "topics": ["NVMe speed", "Free SSL", "Cloud hosting"],
            "format_type": "viral",
        })
        assert result["status"] == "ok"
        assert result["data"]["total_topics"] == 3

    @pytest.mark.asyncio
    async def test_empty_topics(self, registry):
        pipeline = registry.get("batch_content")
        result = await pipeline.run({"topics": []})
        assert result["status"] == "error"
