#!/usr/bin/env python3
"""
Video Creator — Web UI entry point.

Thin wrapper: registers API routers, serves HTML, starts task queue worker.
All logic lives in api/ modules. HTML in templates/index.html.

Run:
    python3 web.py          (starts on http://localhost:8910)
    python3 web.py --port 3000
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Load .env
load_dotenv(Path(__file__).parent / ".env")

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent))

# App
app = FastAPI(title="Video Creator", docs_url=None, redoc_url=None)

# Static assets (served publicly so HeyGen can fetch them via tunnel)
ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Register all API routers (each file = one feature)
from api import register_all
register_all(app)


# Task queue worker
from taskqueue import queue

@app.on_event("startup")
async def _start_worker():
    asyncio.create_task(queue.run_worker(concurrency=3))


# HTML — served from templates/index.html
TEMPLATE = Path(__file__).parent / "templates" / "index.html"

@app.get("/", response_class=HTMLResponse)
async def index():
    return TEMPLATE.read_text(encoding="utf-8")


# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video Creator — Web UI")
    parser.add_argument("--port", type=int, default=8910)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()
    print(f"\n  Video Creator UI \u2192 http://localhost:{args.port}\n")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
