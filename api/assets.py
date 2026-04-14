"""Brand assets — local folder management."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["assets"])

ASSETS_DIR = Path(__file__).parent.parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)


@router.get("/assets")
async def list_assets(folder: str = ""):
    """List assets in a folder."""
    target = ASSETS_DIR / folder if folder else ASSETS_DIR
    if not target.exists() or not str(target.resolve()).startswith(str(ASSETS_DIR.resolve())):
        return JSONResponse({"ok": False, "error": "Invalid folder"}, status_code=400)

    items = []
    for p in sorted(target.iterdir()):
        if p.name.startswith("."):
            continue
        item = {
            "name": p.name,
            "path": str(p.relative_to(ASSETS_DIR)),
            "is_dir": p.is_dir(),
            "size": p.stat().st_size if p.is_file() else 0,
        }
        ext = p.suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"):
            item["type"] = "image"
        elif ext in (".mp4", ".mov", ".webm"):
            item["type"] = "video"
        elif ext in (".mp3", ".wav", ".m4a"):
            item["type"] = "audio"
        else:
            item["type"] = "other"
        item["url"] = f"/assets/{item['path']}"
        items.append(item)
    return JSONResponse({"ok": True, "items": items, "folder": folder})


@router.get("/assets/folders")
async def asset_folders():
    """List asset subfolders."""
    folders = [d.name for d in ASSETS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
    return JSONResponse({"ok": True, "folders": sorted(folders)})
