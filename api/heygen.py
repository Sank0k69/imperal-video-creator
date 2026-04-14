"""HeyGen video creation via MCP bridge + prompt builder."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from agent import list_avatars, list_voices, heygen_request
from heygen_mcp import create_video as mcp_create_video

router = APIRouter(prefix="/api", tags=["heygen"])


# ---------------------------------------------------------------------------
# Prompt builder — montage settings → detailed HeyGen instructions
# ---------------------------------------------------------------------------

def build_video_prompt(script: str, title: str, montage: dict) -> str:
    """Build a detailed prompt for HeyGen Video Agent based on montage settings."""
    pace = montage.get("pace", "dynamic")
    scene_change = montage.get("scene_change", "5-7")
    broll = montage.get("broll", True)
    text_overlays = montage.get("text_overlays", True)
    presenter_style = montage.get("presenter_style", "mixed")
    bg_variety = montage.get("bg_variety", True)
    energy = montage.get("energy", "high")
    preset = montage.get("preset", "")

    # Preset overrides
    presets = {
        "tiktok_viral": ("aggressive", "3-5", "high", True, True, "mixed", True),
        "youtube_pro": ("dynamic", "5-8", "medium", True, True, "mixed", True),
        "linkedin_corp": ("chill", "8-12", "low", False, True, "fullscreen", False),
        "adhd": ("adhd", "1-3", "max", True, True, "mixed", True),
        "promo": ("aggressive", "3-4", "high", True, True, "none", True),
    }
    if preset in presets:
        pace, scene_change, energy, broll, text_overlays, presenter_style, bg_variety = presets[preset]

    brief = montage.get("brief", "")

    parts = []
    parts.append(f"Title: {title}")
    if brief:
        parts.append(f"Video Brief (context for visual style and tone): {brief}")
    parts.append(f"Script (speak this WORD FOR WORD, do not change or summarize): {script}")
    parts.append("")
    parts.append("=== MONTAGE DIRECTION ===")

    # Pacing
    pacing = {
        "adhd": """PACING: MAXIMUM ADHD DOPAMINE OVERLOAD. This video must feel like a dopamine hit every single second.
- Change SOMETHING visually every 1-2 seconds — zoom, cut, pan, text pop, color flash, transition
- Never EVER hold a static shot for more than 2 seconds
- Use rapid zoom-ins on key words as they're spoken
- Flash bold text overlays that appear and disappear fast
- Quick-cut between presenter, B-roll, graphics, memes, stock footage
- Use split-screen, picture-in-picture, rotating angles
- Kinetic typography — words fly in, bounce, shake, scale up
- Background must shift colors/gradients constantly
- Think: Mr Beast meets TikTok meets music video editing
- Every sentence = new visual scene minimum
- 1.2x-1.3x voice speed for urgency""",
        "aggressive": "PACING: Fast, punchy edits. Maximum energy. Every 3-5 seconds must have a visual change — new camera angle, B-roll cut, text popup, zoom, or transition. Never stay on one static shot for more than 4 seconds. Think TikTok/Reels energy.",
        "dynamic": "PACING: Dynamic and engaging. Change visuals every 5-7 seconds. Mix between presenter talking, B-roll footage, and text overlays. Keep the viewer's eye moving.",
    }
    parts.append(pacing.get(pace, "PACING: Professional and composed. Scene changes every 8-12 seconds. Clean transitions."))

    if broll:
        parts.append("B-ROLL: Insert relevant stock footage, graphics, or illustrations between presenter shots to visualize what's being said.")
    if text_overlays:
        parts.append("TEXT OVERLAYS: Add bold, readable text overlays for key stats, numbers, and important phrases. Animated — slide in, pop up, or scale.")

    # Presenter
    if presenter_style == "none":
        parts.append("FORMAT: PROMO VIDEO — NO talking head avatar. ONLY voiceover + B-roll + motion graphics + animated text. Commercial/ad style.")
    elif presenter_style == "mixed":
        parts.append("PRESENTER: Alternate between full-screen presenter, corner overlay with visuals behind, and full-screen B-roll with voiceover.")
    elif presenter_style == "corner":
        parts.append("PRESENTER: Small circle/corner overlay. Main screen shows B-roll, graphics, text overlays.")
    else:
        parts.append("PRESENTER: Full-screen with changing backgrounds.")

    if bg_variety:
        parts.append("BACKGROUNDS: Variety — modern office, gradients, outdoor, abstract tech. Change every 2-3 scenes. NO plain white.")

    # Energy
    energy_map = {
        "max": "ENERGY: MAXIMUM. Extreme passion and urgency. Fast delivery. Voice 1.2x-1.3x speed.",
        "high": "ENERGY: High energy, expressive. Gestures, emphasis, direct eye contact.",
        "medium": "ENERGY: Confident and warm. Professional but not stiff.",
    }
    parts.append(energy_map.get(energy, "ENERGY: Calm authority. Measured, trustworthy."))

    # Scenes
    scenes = montage.get("scenes", [])
    if scenes:
        parts.append("\n=== SCENE BREAKDOWN ===")
        for i, scene in enumerate(scenes, 1):
            parts.append(f"\nSCENE {i}:")
            if scene.get("location"):
                parts.append(f"  Location: {scene['location']}")
            if scene.get("visual"):
                parts.append(f"  Visual: {scene['visual']}")
            if scene.get("image_url"):
                parts.append(f"  Reference image: {scene['image_url']}")
            if scene.get("script_segment"):
                parts.append(f"  Script: \"{scene['script_segment']}\"")

    # Locations
    locations = montage.get("locations", [])
    if locations and not scenes:
        parts.append("\n=== LOCATIONS ===")
        for loc in locations:
            parts.append(f"- {loc.get('name', 'Scene')}: {loc.get('description', '')}")

    # Brand assets
    brand_assets = montage.get("brand_assets", [])
    if brand_assets:
        parts.append("\n=== BRAND ASSETS ===")
        parts.append("Attached brand files. USE THEM — logo for end card, footage as B-roll:")
        for asset in brand_assets:
            parts.append(f"- {asset.get('name', 'file')}: {asset.get('description', '')}")

    parts.append("\nCRITICAL RULES:")
    parts.append("- Script MUST be spoken exactly as written")
    parts.append("- Visually dynamic — viewer should never feel bored")
    parts.append("- NO plain white backgrounds")
    parts.append("- NO single static shot for entire video")
    min_scenes = max(3, len(script.split()) // 50, len(scenes))
    parts.append(f"- Minimum {min_scenes} distinct visual scenes")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/avatars")
async def api_avatars():
    """List avatars with preview images."""
    try:
        data = heygen_request("GET", "/v2/avatars")
        avatars_raw = data.get("data", {}).get("avatars", [])
        avatars = [{
            "avatar_id": a.get("avatar_id", ""),
            "avatar_name": a.get("avatar_name", ""),
            "gender": a.get("gender", ""),
            "preview_image": a.get("preview_image_url", ""),
            "preview_video": a.get("preview_video_url", ""),
            "premium": a.get("premium", False),
        } for a in avatars_raw]
        return JSONResponse({"ok": True, "avatars": avatars})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/voices")
async def api_voices(lang: str = "en"):
    """List voices with preview audio."""
    try:
        data = heygen_request("GET", "/v2/voices")
        voices_raw = data.get("data", {}).get("voices", [])
        voices = []
        for v in voices_raw:
            voice_lang = v.get("language", "")
            if lang and lang != "all" and not voice_lang.lower().startswith(lang.lower()):
                continue
            voices.append({
                "voice_id": v.get("voice_id", ""),
                "name": v.get("name", "").strip(),
                "language": voice_lang,
                "gender": v.get("gender", ""),
                "preview_audio": v.get("preview_audio", ""),
            })
        return JSONResponse({"ok": True, "voices": voices})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.post("/create-video-mcp")
async def create_video_mcp(req: Request):
    """Create video via HeyGen MCP (account credits)."""
    body = await req.json()
    script = body.get("script", "")
    title = body.get("title", "Generated Video")
    fmt = body.get("format", "portrait")
    montage = body.get("montage", {})
    asset_urls = body.get("asset_urls", [])
    orientation = "portrait" if fmt == "portrait" else "landscape"

    prompt = build_video_prompt(script, title, montage)

    try:
        result = mcp_create_video(prompt, orientation=orientation, files=asset_urls or None)
        if "error" in result:
            return JSONResponse({"ok": False, "error": result["error"]}, status_code=500)
        return JSONResponse({
            "ok": True,
            "video_id": result.get("video_id", ""),
            "session_id": result.get("session_id", ""),
            "status": result.get("status", "submitted"),
            "title": title,
            "method": "mcp",
        })
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
