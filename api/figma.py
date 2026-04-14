"""Figma API — bridge to Designer extension."""

import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/figma", tags=["figma"])


def _token() -> str:
    return os.getenv("FIGMA_TOKEN", "")


@router.get("/components")
async def list_components(file_key: str = "", query: str = ""):
    """List Figma components."""
    import httpx
    token = _token()
    if not token:
        return JSONResponse({"ok": False, "error": "FIGMA_TOKEN not set in .env"}, status_code=400)
    if not file_key:
        return JSONResponse({"ok": False, "error": "file_key required"}, status_code=400)

    try:
        headers = {"X-Figma-Token": token}
        with httpx.Client(timeout=30) as client:
            resp = client.get(f"https://api.figma.com/v1/files/{file_key}", headers=headers)
            if resp.status_code >= 400:
                return JSONResponse({"ok": False, "error": f"Figma API {resp.status_code}"}, status_code=500)
            data = resp.json()

        components = []
        def walk(node, depth=0):
            if depth > 10:
                return
            if node.get("type") in ("COMPONENT", "COMPONENT_SET"):
                components.append({
                    "id": node.get("id", ""),
                    "name": node.get("name", ""),
                    "type": node.get("type", ""),
                })
            for child in node.get("children", []):
                walk(child, depth + 1)
        walk(data.get("document", {}))

        if query:
            q = query.lower()
            components = [c for c in components if q in c["name"].lower()]

        return JSONResponse({"ok": True, "components": components, "count": len(components)})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/export")
async def export_component(file_key: str, node_id: str, format: str = "png", scale: float = 2.0):
    """Export a Figma component as image."""
    import httpx
    token = _token()
    if not token:
        return JSONResponse({"ok": False, "error": "FIGMA_TOKEN not set"}, status_code=400)

    try:
        headers = {"X-Figma-Token": token}
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format={format}&scale={scale}",
                headers=headers,
            )
            if resp.status_code >= 400:
                return JSONResponse({"ok": False, "error": f"Figma API {resp.status_code}"}, status_code=500)
            data = resp.json()

        url = data.get("images", {}).get(node_id, "")
        return JSONResponse({"ok": True, "url": url, "node_id": node_id, "format": format})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
