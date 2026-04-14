"""
Shared test fixtures for Video Creator extension.
Uses MockContext from Imperal SDK -- full workflow testing without a server.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock


class MockStore:
    """In-memory store for testing -- matches SDK store API.

    SDK signatures:
        get(collection, doc_id)
        create(collection, data)
        update(collection, doc_id, data)
        query(collection, filter)
        delete(collection, doc_id)
        count(collection)
    """

    def __init__(self):
        self._data = {}  # { "collection/doc_id": value }

    async def get(self, collection, doc_id):
        return self._data.get(f"{collection}/{doc_id}")

    async def create(self, collection, data):
        doc_id = data.get("_id", str(len(self._data)))
        self._data[f"{collection}/{doc_id}"] = data
        return doc_id

    async def update(self, collection, doc_id, data):
        key = f"{collection}/{doc_id}"
        existing = self._data.get(key, {})
        if isinstance(existing, dict) and isinstance(data, dict):
            existing.update(data)
            self._data[key] = existing
        else:
            self._data[key] = data

    async def query(self, collection, filter_dict=None):
        prefix = f"{collection}/"
        results = []
        for k, v in self._data.items():
            if k.startswith(prefix):
                results.append(k[len(prefix):])
        return results

    async def delete(self, collection, doc_id):
        self._data.pop(f"{collection}/{doc_id}", None)

    async def count(self, collection):
        prefix = f"{collection}/"
        return sum(1 for k in self._data if k.startswith(prefix))


class MockAI:
    """Mock AI client -- matches SDK ai API.

    SDK signature:
        ctx.ai.complete(prompt, system=system) -> CompletionResult with .text
    """

    def __init__(self, default_response="Mock AI response"):
        self.default_response = default_response
        self._responses = {}
        self.calls = []

    def set_response(self, keyword: str, response: str):
        """Set response for prompts containing a keyword."""
        self._responses[keyword] = response

    async def complete(self, prompt, system=""):
        # Store full context so tests can check both prompt and system
        full_text = f"{system}\n{prompt}" if system else prompt
        self.calls.append(full_text)

        for keyword, response in self._responses.items():
            if keyword.lower() in full_text.lower():
                return MagicMock(text=response)

        return MagicMock(text=self.default_response)


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
