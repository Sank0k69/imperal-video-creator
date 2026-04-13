"""Tests for Ideation Module."""
import pytest
from modules.ideation import IdeationModule


@pytest.fixture
def ideation(ctx):
    return IdeationModule(ctx)


class TestIdeation:

    @pytest.mark.asyncio
    async def test_generate_ideas(self, ideation):
        result = await ideation.execute("generate", {
            "topic": "web hosting speed",
            "count": 5,
            "method": "mixed",
        })
        assert result["status"] == "ok"
        assert result["data"]["topic"] == "web hosting speed"
        assert result["data"]["count"] == 5
        assert result["data"]["method"] == "mixed"

    @pytest.mark.asyncio
    async def test_generate_uses_niche_when_no_topic(self, ideation):
        result = await ideation.execute("generate", {"count": 3, "method": "commence"})
        assert result["status"] == "ok"
        assert result["data"]["topic"] == "web hosting"  # from config niche

    @pytest.mark.asyncio
    async def test_classify_idea(self, ideation):
        result = await ideation.execute("classify", {
            "idea": "Why 99% of websites load slowly and how to fix it",
        })
        assert result["status"] == "ok"
        assert "classification" in result["data"]

    @pytest.mark.asyncio
    async def test_bank_add_and_list(self, ideation):
        # Add ideas
        await ideation.execute("bank_add", {"idea": {"title": "Idea 1"}})
        await ideation.execute("bank_add", {"idea": {"title": "Idea 2"}})

        # List
        result = await ideation.execute("bank_list", {})
        assert result["status"] == "ok"
        assert result["data"]["total"] == 2

    @pytest.mark.asyncio
    async def test_unknown_action(self, ideation):
        result = await ideation.execute("nonexistent", {})
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_is_enabled(self, ideation):
        assert ideation.is_enabled() is True

    @pytest.mark.asyncio
    async def test_loads_knowledge(self, ideation):
        data = ideation.load_knowledge("ideation_methods.json")
        assert "methods" in data
        assert "commence" in data["methods"]

    @pytest.mark.asyncio
    async def test_ai_called_with_system_prompt(self, ideation):
        await ideation.execute("generate", {"topic": "test", "count": 1, "method": "mixed"})
        assert len(ideation.ctx.ai.calls) == 1
        assert "Perfect Idea Zone" in ideation.ctx.ai.calls[0]
