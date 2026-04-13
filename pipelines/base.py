"""
Pipeline base — orchestration layer.
Pipelines wire modules together. Modules never import each other.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class BasePipeline(ABC):
    """Base class for all pipelines."""

    name: str = ""
    description: str = ""
    steps: list[str] = []

    def __init__(self, ctx: Any, get_module: Callable):
        self.ctx = ctx
        self._get_module = get_module

    def module(self, name: str):
        """Get a module instance by name."""
        return self._get_module(self.ctx, name)

    @abstractmethod
    async def run(self, params: dict) -> dict:
        """Execute the pipeline. Returns dict with 'status', 'data', 'summary'."""
        ...

    def get_steps(self) -> list[str]:
        """Return list of step names for progress tracking."""
        return self.steps


class PipelineRegistry:
    """Registry of available pipelines. Lazy instantiation."""

    def __init__(self, ctx: Any, get_module: Callable):
        self.ctx = ctx
        self._get_module = get_module
        self._cache: dict[str, BasePipeline] = {}

        # Register pipelines
        from .full_video import FullVideoPipeline
        from .quick_script import QuickScriptPipeline
        from .batch_content import BatchContentPipeline

        self._registry: dict[str, type[BasePipeline]] = {
            "full_video": FullVideoPipeline,
            "quick_script": QuickScriptPipeline,
            "batch_content": BatchContentPipeline,
        }

    def get(self, name: str) -> BasePipeline:
        """Get a pipeline by name. Creates instance if needed."""
        if name not in self._cache:
            if name not in self._registry:
                raise ValueError(f"Unknown pipeline: {name}")
            self._cache[name] = self._registry[name](self.ctx, self._get_module)
        return self._cache[name]

    def list_pipelines(self) -> list[dict]:
        """List all available pipelines."""
        return [
            {"name": name, "description": cls.description, "steps": cls.steps}
            for name, cls in self._registry.items()
        ]
