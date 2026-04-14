"""My Videos — list, status, delete."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent import heygen_request, check_status
from heygen_mcp import _call_mcp, get_video as mcp_get_video

router = APIRouter(prefix="/api", tags=["videos"])


@router.get("/videos")
async def list_videos():
    """List all user videos from HeyGen, enriched with thumbnail/url."""
    try:
        data = heygen_request("GET", "/v1/video.list?limit=100")
        videos = data.get("data", {}).get("videos", [])
        for v in videos:
            if v.get("status") == "completed" and not v.get("video_url"):
                try:
                    detail = heygen_request("GET", f"/v1/video_status.get?video_id={v['video_id']}")
                    vd = detail.get("data", {})
                    v["video_url"] = vd.get("video_url", "")
                    v["thumbnail_url"] = vd.get("thumbnail_url", "")
                    v["duration"] = vd.get("duration", 0)
                except Exception:
                    pass
        return JSONResponse({"ok": True, "videos": videos})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/video/{video_id}")
async def video_status(video_id: str):
    """Get status of a single video (API key method)."""
    try:
        result = check_status(video_id)
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/video-mcp/{video_id}")
async def video_status_mcp(video_id: str):
    """Check video status via MCP."""
    try:
        result = mcp_get_video(video_id)
        if "error" in result:
            return JSONResponse({"ok": False, "error": result["error"]}, status_code=500)
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.delete("/video/{video_id}")
async def delete_video(video_id: str):
    """Delete a video from HeyGen permanently."""
    try:
        result = _call_mcp("delete_video", {"videoId": video_id})
        if "error" in result:
            try:
                heygen_request("DELETE", f"/v1/video.delete", {"video_ids": [video_id]})
            except Exception:
                return JSONResponse({"ok": False, "error": result["error"]}, status_code=500)
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
