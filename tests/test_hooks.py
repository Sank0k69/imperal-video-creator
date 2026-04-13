"""Tests for Hooks Module."""
import pytest
from modules.hooks import HooksModule


@pytest.fixture
def hooks(ctx):
    return HooksModule(ctx)


class TestHooks:

    @pytest.mark.asyncio
    async def test_generate_hooks(self, hooks):
        result = await hooks.execute("generate", {
            "topic": "NVMe hosting speed",
            "count": 5,
        })
        assert result["status"] == "ok"
        assert result["data"]["topic"] == "NVMe hosting speed"
        assert result["data"]["count"] == 5

    @pytest.mark.asyncio
    async def test_generate_specific_types(self, hooks):
        result = await hooks.execute("generate", {
            "topic": "website speed",
            "types": ["controversial", "secret"],
            "count": 3,
        })
        assert result["status"] == "ok"
        assert result["data"]["types_used"] == ["controversial", "secret"]

    @pytest.mark.asyncio
    async def test_generate_all_types_by_default(self, hooks):
        result = await hooks.execute("generate", {
            "topic": "hosting",
        })
        assert result["status"] == "ok"
        assert len(result["data"]["types_used"]) == 7  # all 7 types

    @pytest.mark.asyncio
    async def test_loads_templates(self, hooks):
        data = hooks.load_knowledge("hook_templates.json")
        assert "types" in data
        assert len(data["types"]) == 7

    @pytest.mark.asyncio
    async def test_unknown_action(self, hooks):
        result = await hooks.execute("unknown", {})
        assert result["status"] == "error"
