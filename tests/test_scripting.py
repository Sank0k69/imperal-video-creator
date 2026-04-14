"""Tests for Scripting Module."""
import pytest
from modules.scripting import ScriptingModule


@pytest.fixture
def scripting(ctx):
    return ScriptingModule(ctx)


class TestScripting:

    @pytest.mark.asyncio
    async def test_write_tier1(self, scripting):
        result = await scripting.execute("write", {
            "topic": "5 reasons NVMe hosting is faster",
            "tier": 1,
            "format_type": "viral",
            "duration": "short",
        })
        assert result["status"] == "ok"
        assert result["data"]["tier"] == 1
        assert result["data"]["format"] == "viral"

    @pytest.mark.asyncio
    async def test_write_tier2(self, scripting):
        result = await scripting.execute("write", {
            "topic": "How I scaled my website",
            "tier": 2,
            "format_type": "pitch",
            "duration": "medium",
        })
        assert result["status"] == "ok"
        assert result["data"]["tier"] == 2

    @pytest.mark.asyncio
    async def test_write_with_prehook(self, scripting):
        result = await scripting.execute("write", {
            "topic": "hosting tips",
            "hook": "Nobody talks about this hosting secret...",
            "tier": 1,
            "format_type": "viral",
            "duration": "short",
        })
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_saves_to_store(self, scripting):
        await scripting.execute("write", {
            "topic": "test save",
            "tier": 1,
            "format_type": "viral",
            "duration": "short",
        })
        saved = await scripting.ctx.store.get("scripting", "scripts/test_save")
        assert saved is not None
        assert saved["topic"] == "test save"

    @pytest.mark.asyncio
    async def test_rewrite(self, scripting):
        result = await scripting.execute("rewrite", {
            "script": "Original script text here",
            "feedback": "Make it more energetic and add more social proof",
        })
        assert result["status"] == "ok"
        assert result["data"]["feedback"] == "Make it more energetic and add more social proof"

    @pytest.mark.asyncio
    async def test_all_format_types(self, scripting):
        for fmt in ["viral", "pitch", "false_statement"]:
            result = await scripting.execute("write", {
                "topic": "test", "tier": 1, "format_type": fmt, "duration": "short",
            })
            assert result["status"] == "ok"
