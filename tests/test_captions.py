"""Tests for Captions Module."""
import pytest
from modules.captions import CaptionsModule


@pytest.fixture
def captions(ctx):
    return CaptionsModule(ctx)


class TestCaptions:

    @pytest.mark.asyncio
    async def test_generate_curiosity(self, captions):
        result = await captions.execute("generate", {
            "topic": "hosting speed tips",
            "style": "curiosity",
            "count": 5,
        })
        assert result["status"] == "ok"
        assert result["data"]["style"] == "curiosity"
        assert result["data"]["count"] == 5

    @pytest.mark.asyncio
    async def test_generate_pcm(self, captions):
        result = await captions.execute("generate", {
            "topic": "website migration",
            "style": "pcm",
            "count": 3,
        })
        assert result["status"] == "ok"
        assert result["data"]["style"] == "pcm"

    @pytest.mark.asyncio
    async def test_generate_engagement(self, captions):
        result = await captions.execute("generate", {
            "topic": "free SSL",
            "style": "engagement",
            "count": 3,
        })
        assert result["status"] == "ok"
