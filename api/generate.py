"""Script / Ideas / Hooks generation via Claude."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from agent import generate_ideas, write_script, generate_hooks, rewrite_script

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/script")
async def api_script(req: Request):
    body = await req.json()
    topic = body.get("topic", "").strip()
    if not topic:
        return JSONResponse({"ok": False, "error": "Topic is required"}, status_code=400)
    brief = body.get("brief", "").strip()
    tier = max(1, min(body.get("tier", 1), 3))
    # Prepend brief to topic for richer context
    full_topic = f"[Brief: {brief}]\n\n{topic}" if brief else topic
    try:
        result = write_script(full_topic, tier=tier)
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.post("/script/rewrite")
async def api_rewrite_script(req: Request):
    body = await req.json()
    original_script = body.get("script", "").strip()
    prompt = body.get("prompt", "").strip()
    if not original_script:
        return JSONResponse({"ok": False, "error": "Script is required"}, status_code=400)
    if not prompt:
        return JSONResponse({"ok": False, "error": "Rewrite prompt is required"}, status_code=400)
    try:
        result = rewrite_script(original_script, prompt)
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.post("/ideas")
async def api_ideas(req: Request):
    body = await req.json()
    topic = body.get("topic", "").strip()
    if not topic:
        return JSONResponse({"ok": False, "error": "Topic is required"}, status_code=400)
    count = max(1, min(body.get("count", 5), 20))
    try:
        result = generate_ideas(topic, count=count)
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.post("/hooks")
async def api_hooks(req: Request):
    body = await req.json()
    topic = body.get("topic", "").strip()
    if not topic:
        return JSONResponse({"ok": False, "error": "Topic is required"}, status_code=400)
    count = max(1, min(body.get("count", 5), 20))
    try:
        result = generate_hooks(topic, count=count)
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
