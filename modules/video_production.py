"""
Video Production Module — HeyGen integration for actual video creation.
Bridges the gap between script generation and real video output.
"""
from __future__ import annotations

import json
from .base import BaseModule


HEYGEN_API = "https://api.heygen.com"


class VideoProductionModule(BaseModule):
    name = "video_production"
    description = "Create actual videos via HeyGen API from scripts"
    version = "2.0.0"

    SYSTEM_PROMPT = """You are a video production specialist. You take scripts written by
the scripting module and prepare them for HeyGen avatar video creation.

Your job:
1. Clean scripts for voice synthesis (remove stage directions, visual cues)
2. Split long scripts into segments if needed
3. Select appropriate avatar and voice based on content
4. Format the HeyGen API payload correctly

Keep the spoken text natural and conversational. Remove anything that shouldn't
be spoken aloud (like [HOOK], [CTA], editing notes, etc.)."""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {"name": "create_video", "description": "Create video from script via HeyGen", "params": ["script", "avatar_id", "voice_id", "dimension"]},
            {"name": "check_status", "description": "Check video generation status", "params": ["video_id"]},
            {"name": "list_avatars", "description": "List available HeyGen avatars", "params": ["limit"]},
            {"name": "list_voices", "description": "List available voices", "params": ["language"]},
            {"name": "clean_script", "description": "Clean a script for voice synthesis", "params": ["script"]},
        ]

    def _get_heygen_key(self) -> str:
        """Get HeyGen API key from config."""
        return self.get_config("heygen_api_key", "")

    async def _heygen_request(self, method: str, path: str, json_data: dict | None = None) -> dict:
        """Make authenticated request to HeyGen API."""
        key = self._get_heygen_key()
        if not key:
            return {"status": "error", "data": None, "summary": "HeyGen API key not configured. Set it in Settings."}

        headers = {"x-api-key": key, "Content-Type": "application/json"}
        url = f"{HEYGEN_API}{path}"

        if method == "GET":
            resp = await self.ctx.http.get(url, headers=headers)
        elif method == "POST":
            resp = await self.ctx.http.post(url, headers=headers, json=json_data)
        else:
            return {"status": "error", "data": None, "summary": f"Unsupported method: {method}"}

        if resp.status_code >= 400:
            return {"status": "error", "data": resp.json(), "summary": f"HeyGen API error: {resp.status_code}"}

        return resp.json()

    async def execute(self, action: str, params: dict) -> dict:
        if action == "create_video":
            return await self._create_video(params)
        elif action == "check_status":
            return await self._check_status(params)
        elif action == "list_avatars":
            return await self._list_avatars(params)
        elif action == "list_voices":
            return await self._list_voices(params)
        elif action == "clean_script":
            return await self._clean_script(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _clean_script(self, params: dict) -> dict:
        """Clean a raw script for voice synthesis."""
        script = params.get("script", "")

        prompt = f"""Clean this video script for voice synthesis. Remove:
- Section markers like [HOOK], [BODY], [CTA], [P1], etc.
- Stage directions and editing notes
- Visual cues (e.g., "show graphic", "cut to B-roll")
- Sound effect notes
- Anything in brackets or parentheses that is not spoken

Keep ONLY the words that should be spoken aloud by the avatar.
Make it flow naturally as spoken text.

SCRIPT:
{script}

Output ONLY the clean spoken text, nothing else."""

        clean = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"clean_script": clean, "original_length": len(script), "clean_length": len(clean)},
            "summary": "Script cleaned for voice synthesis",
        }

    async def _create_video(self, params: dict) -> dict:
        """Create a video via HeyGen API."""
        script = params.get("script", "")
        avatar_id = params.get("avatar_id", "")
        voice_id = params.get("voice_id", "")
        dimension = params.get("dimension", "portrait")

        if not script:
            return {"status": "error", "data": None, "summary": "No script provided"}

        # Default dimensions
        dims = {"width": 1080, "height": 1920}  # portrait/reels
        if dimension == "landscape":
            dims = {"width": 1920, "height": 1080}
        elif dimension == "square":
            dims = {"width": 1080, "height": 1080}

        # Auto-select avatar if not specified
        if not avatar_id:
            avatars_resp = await self._heygen_request("GET", "/v2/avatars")
            if isinstance(avatars_resp, dict) and avatars_resp.get("data"):
                avatar_list = avatars_resp["data"].get("avatars", [])
                if avatar_list:
                    avatar_id = avatar_list[0].get("avatar_id", "")

        # Auto-select voice if not specified
        if not voice_id:
            voices_resp = await self._heygen_request("GET", "/v2/voices")
            if isinstance(voices_resp, dict) and voices_resp.get("data"):
                voice_list = voices_resp["data"].get("voices", [])
                en_voices = [v for v in voice_list if "en" in v.get("language", "").lower()]
                if en_voices:
                    voice_id = en_voices[0].get("voice_id", "")

        if not avatar_id or not voice_id:
            return {"status": "error", "data": None, "summary": "Could not determine avatar or voice"}

        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id,
                },
            }],
            "dimension": dims,
        }

        resp = await self._heygen_request("POST", "/v2/video/generate", payload)

        if isinstance(resp, dict) and resp.get("data"):
            video_id = resp["data"].get("video_id", "")
            return {
                "status": "ok",
                "data": {"video_id": video_id, "avatar_id": avatar_id, "voice_id": voice_id, "dimension": dims},
                "summary": f"Video creation started. ID: {video_id}. Use check_status to monitor.",
            }

        return {"status": "error", "data": resp, "summary": "Failed to start video creation"}

    async def _check_status(self, params: dict) -> dict:
        """Check video generation status."""
        video_id = params.get("video_id", "")
        if not video_id:
            return {"status": "error", "data": None, "summary": "No video_id provided"}

        resp = await self._heygen_request("GET", f"/v1/video_status.get?video_id={video_id}")

        if isinstance(resp, dict) and resp.get("data"):
            data = resp["data"]
            status = data.get("status", "unknown")
            result = {
                "video_id": video_id,
                "status": status,
                "duration": data.get("duration"),
                "video_url": data.get("video_url"),
                "thumbnail_url": data.get("thumbnail_url"),
            }
            summary = f"Video {video_id}: {status}"
            if status == "completed" and data.get("video_url"):
                summary += f" — Download: {data['video_url']}"
            return {"status": "ok", "data": result, "summary": summary}

        return {"status": "error", "data": resp, "summary": "Failed to check status"}

    async def _list_avatars(self, params: dict) -> dict:
        """List available HeyGen avatars."""
        limit = params.get("limit", 20)
        resp = await self._heygen_request("GET", "/v2/avatars")

        if isinstance(resp, dict) and resp.get("data"):
            avatars = resp["data"].get("avatars", [])[:limit]
            return {
                "status": "ok",
                "data": {"avatars": [{"id": a.get("avatar_id"), "name": a.get("avatar_name"), "gender": a.get("gender")} for a in avatars], "total": len(resp["data"].get("avatars", []))},
                "summary": f"Found {len(resp['data'].get('avatars', []))} avatars",
            }

        return {"status": "error", "data": resp, "summary": "Failed to list avatars"}

    async def _list_voices(self, params: dict) -> dict:
        """List available voices."""
        language = params.get("language", "en")
        resp = await self._heygen_request("GET", "/v2/voices")

        if isinstance(resp, dict) and resp.get("data"):
            voices = resp["data"].get("voices", [])
            filtered = [v for v in voices if language.lower() in v.get("language", "").lower()]
            return {
                "status": "ok",
                "data": {"voices": [{"id": v.get("voice_id"), "name": v.get("display_name"), "language": v.get("language"), "gender": v.get("gender")} for v in filtered[:30]], "total": len(filtered)},
                "summary": f"Found {len(filtered)} voices for '{language}'",
            }

        return {"status": "error", "data": resp, "summary": "Failed to list voices"}
