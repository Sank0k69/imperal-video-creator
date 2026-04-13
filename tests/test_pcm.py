"""Tests for PCM Module."""
import pytest
from modules.pcm import PCMModule


@pytest.fixture
def pcm(ctx):
    return PCMModule(ctx)


class TestPCM:

    @pytest.mark.asyncio
    async def test_analyze(self, pcm):
        result = await pcm.execute("analyze", {
            "script": "Imagine if your website loaded in under 1 second. "
                      "I believe every business deserves fast hosting. "
                      "It doesn't make sense to pay more for slower service. "
                      "You have to switch to NVMe today. "
                      "I love how it transforms small businesses. "
                      "So funny when people say speed doesn't matter.",
        })
        assert result["status"] == "ok"
        assert "analysis" in result["data"]

    @pytest.mark.asyncio
    async def test_enhance(self, pcm):
        result = await pcm.execute("enhance", {
            "script": "NVMe hosting is fast. You should try it.",
            "target_types": ["rebel", "imaginer", "harmonizer"],
        })
        assert result["status"] == "ok"
        assert result["data"]["target_types"] == ["rebel", "imaginer", "harmonizer"]

    @pytest.mark.asyncio
    async def test_enhance_auto_detect(self, pcm):
        result = await pcm.execute("enhance", {
            "script": "NVMe hosting is fast. You should try it.",
        })
        assert result["status"] == "ok"
        assert result["data"]["target_types"] == []

    @pytest.mark.asyncio
    async def test_loads_pcm_types(self, pcm):
        data = pcm.load_knowledge("pcm_types.json")
        assert len(data["types"]) == 6
        assert "rebel" in data["types"]
        assert "imaginer" in data["types"]
