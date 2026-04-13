"""
Shared test fixtures for Video Creator extension.
Uses MockContext from Imperal SDK — full workflow testing without a server.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock


class MockStore:
    """In-memory key-value store for testing."""

    def __init__(self):
        self._data = {}

    async def get(self, key, default=None):
        return self._data.get(key, default)

    async def set(self, key, value):
        self._data[key] = value

    async def list(self, prefix=""):
        return [k for k in self._data if k.startswith(prefix)]

    async def delete(self, key):
        self._data.pop(key, None)


class MockAI:
    """Mock AI client with configurable responses."""

    def __init__(self, default_response="Mock AI response"):
        self.default_response = default_response
        self._responses = {}
        self.calls = []

    def set_response(self, keyword: str, response: str):
        """Set response for prompts containing a keyword."""
        self._responses[keyword] = response

    async def chat(self, messages):
        prompt = " ".join(m.get("content", "") for m in messages)
        self.calls.append(prompt)

        for keyword, response in self._responses.items():
            if keyword.lower() in prompt.lower():
                return MagicMock(content=response)

        return MagicMock(content=self.default_response)


class MockNotify:
    """Mock notification client."""

    def __init__(self):
        self.sent = []

    async def push(self, title="", body=""):
        self.sent.append({"title": title, "body": body})


class MockConfig:
    """Mock config with dict-like access."""

    def __init__(self, data=None):
        self._data = data or {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    async def set(self, key, value):
        self._data[key] = value


class MockContext:
    """Full mock context replicating Imperal SDK's ctx object."""

    def __init__(self, config=None, ai_response="Mock AI response"):
        self.store = MockStore()
        self.ai = MockAI(default_response=ai_response)
        self.config = MockConfig(config or {
            "niche": "web hosting",
            "target_audience": "Small business owners looking for reliable hosting",
            "brand_voice": ["confident", "helpful", "technical-but-accessible"],
            "language": "en",
            "modules": {
                "ideation": True, "framing": True, "packaging": True,
                "hooks": True, "scripting": True, "pcm": True,
                "captions": True, "cta": True, "publishing": True,
                "iteration": True,
            },
            "quality": {"pcm_min_types": 3, "title_max_chars": 55},
            "content": {"default_post_time": "20:00", "caption_style": "curiosity"},
        })
        self.notify = MockNotify()


@pytest.fixture
def ctx():
    """Default MockContext for testing."""
    return MockContext()


@pytest.fixture
def ctx_custom():
    """Factory for customized MockContext."""
    def _create(config=None, ai_response="Mock response"):
        return MockContext(config=config, ai_response=ai_response)
    return _create
