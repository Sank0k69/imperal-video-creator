"""
BaseModule — contract every module must follow.

Principles:
- Each module is self-contained (own knowledge, prompts, logic)
- Modules don't import each other — pipelines wire them together
- Every public method returns ActionResult
- Knowledge loaded from JSON, not hardcoded
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


class BaseModule(ABC):
    """Interface for all Video Creator modules."""

    name: str = ""
    description: str = ""
    version: str = "1.0.0"

    def __init__(self, ctx: Any):
        self.ctx = ctx
        self._knowledge_cache: dict[str, Any] = {}

    # --- Knowledge loading ---

    def load_knowledge(self, filename: str) -> dict | list:
        """Load a JSON knowledge file. Cached per module lifetime."""
        if filename in self._knowledge_cache:
            return self._knowledge_cache[filename]
        path = KNOWLEDGE_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._knowledge_cache[filename] = data
        return data

    # --- Config helpers ---

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get user config value with fallback to default."""
        return self.ctx.config.get(key, default)

    def is_enabled(self) -> bool:
        """Check if this module is enabled in user config."""
        modules_cfg = self.get_config("modules", {})
        return modules_cfg.get(self.name, True)

    # --- AI helpers ---

    async def ask_ai(self, prompt: str, system: str = "") -> str:
        """Send prompt to AI via platform routing."""
        response = await self.ctx.ai.complete(prompt, system=system)
        return response.text

    # --- Store helpers ---

    async def save(self, key: str, data: Any) -> None:
        """Save data to module's namespace in store."""
        await self.ctx.store.set(f"{self.name}/{key}", data)

    async def load(self, key: str, default: Any = None) -> Any:
        """Load data from module's namespace in store."""
        result = await self.ctx.store.get(f"{self.name}/{key}")
        return result if result is not None else default

    async def list_items(self, prefix: str = "") -> list:
        """List all items in module's namespace."""
        return await self.ctx.store.list(f"{self.name}/{prefix}")

    # --- Abstract interface ---

    @abstractmethod
    async def execute(self, action: str, params: dict) -> dict:
        """
        Execute a module action.

        Args:
            action: The action name (e.g., "generate", "analyze", "list")
            params: Action-specific parameters

        Returns:
            dict with 'status' ('ok'|'error'), 'data', and optional 'summary'
        """
        ...

    def get_actions(self) -> list[dict]:
        """Return list of available actions with descriptions."""
        return []

    def get_system_prompt(self) -> str:
        """Return the system prompt fragment for this module's AI calls."""
        return ""
