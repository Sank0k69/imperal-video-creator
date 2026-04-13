"""Tests for CTA Module."""
import pytest
from modules.cta import CTAModule


@pytest.fixture
def cta(ctx):
    return CTAModule(ctx)


class TestCTA:

    @pytest.mark.asyncio
    async def test_generate_engage(self, cta):
        result = await cta.execute("generate", {
            "context": "video about NVMe hosting benefits",
            "goal": "engage",
            "platform": "youtube",
        })
        assert result["status"] == "ok"
        assert result["data"]["goal"] == "engage"

    @pytest.mark.asyncio
    async def test_generate_redirect(self, cta):
        result = await cta.execute("generate", {
            "context": "tutorial on website speed",
            "goal": "redirect",
            "platform": "youtube",
        })
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_generate_link(self, cta):
        result = await cta.execute("generate", {
            "context": "hosting comparison",
            "goal": "link",
            "platform": "tiktok",
        })
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_generate_manychat(self, cta):
        result = await cta.execute("generate", {
            "context": "free hosting guide",
            "goal": "manychat",
            "platform": "instagram",
        })
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_all_goals(self, cta):
        for goal in ["engage", "redirect", "link", "manychat"]:
            result = await cta.execute("generate", {
                "context": "test", "goal": goal, "platform": "youtube",
            })
            assert result["status"] == "ok"
