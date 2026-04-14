"""
API modules — each file = one feature domain.
Adding a feature = adding a file, not touching others.

Structure:
    api/
    ├── __init__.py      ← this file, registers all routers
    ├── videos.py        ← My Videos (list, status, delete)
    ├── generate.py      ← Script/ideas/hooks generation (Claude)
    ├── heygen.py        ← HeyGen video creation (MCP bridge)
    ├── assets.py        ← Brand assets (local folder + Figma)
    ├── queue.py         ← Task queue endpoints
    └── figma.py         ← Figma API (Designer extension bridge)
"""

from fastapi import FastAPI


def register_all(app: FastAPI):
    """Register all API routers on the app."""
    from . import videos, generate, heygen, assets, queue_api, figma

    for module in [videos, generate, heygen, assets, queue_api, figma]:
        app.include_router(module.router)
