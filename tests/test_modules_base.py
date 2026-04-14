"""Tests for BaseModule and common functionality across all modules."""
import pytest
from modules import ALL_MODULES


class TestAllModulesContract:
    """Verify every module follows the BaseModule contract."""

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    def test_has_name(self, name, cls, ctx):
        mod = cls(ctx)
        assert mod.name == name

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    def test_has_description(self, name, cls, ctx):
        mod = cls(ctx)
        assert len(mod.description) > 0

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    def test_has_version(self, name, cls, ctx):
        mod = cls(ctx)
        assert mod.version in ("1.0.0", "2.0.0")

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    def test_has_actions(self, name, cls, ctx):
        mod = cls(ctx)
        actions = mod.get_actions()
        assert isinstance(actions, list)
        assert len(actions) > 0

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    def test_has_system_prompt(self, name, cls, ctx):
        mod = cls(ctx)
        prompt = mod.get_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    def test_is_enabled(self, name, cls, ctx):
        mod = cls(ctx)
        assert mod.is_enabled() is True

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self, name, cls, ctx):
        mod = cls(ctx)
        result = await mod.execute("__nonexistent__", {})
        assert result["status"] == "error"

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    @pytest.mark.asyncio
    async def test_save_and_load(self, name, cls, ctx):
        mod = cls(ctx)
        await mod.save("test_key", {"value": 42})
        loaded = await mod.load("test_key")
        assert loaded == {"value": 42}

    @pytest.mark.parametrize("name,cls", list(ALL_MODULES.items()))
    @pytest.mark.asyncio
    async def test_load_default(self, name, cls, ctx):
        mod = cls(ctx)
        loaded = await mod.load("nonexistent_key", "default_value")
        assert loaded == "default_value"
