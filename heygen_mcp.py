"""
HeyGen MCP Bridge — create videos via HeyGen MCP (uses account credits, not API credits).

Talks to heygen-mcp-proxy.mjs via stdio, sending JSON-RPC messages.
This is the ONLY way to create videos without API credits.
"""

import json
import subprocess
import sys
from pathlib import Path

PROXY_SCRIPT = Path(__file__).parent.parent.parent / "tools" / "heygen-mcp-proxy.mjs"
NODE = "/opt/homebrew/bin/node"


def _call_mcp(method: str, params: dict) -> dict:
    """Send a JSON-RPC call to HeyGen MCP via stdio proxy."""
    # Initialize + call + close
    init_msg = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "video-creator", "version": "1.0"}}
    })
    call_msg = json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": method, "arguments": params}
    })
    # Notification (no id) to signal initialized
    init_notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})

    stdin_data = init_msg + "\n" + init_notif + "\n" + call_msg + "\n"

    try:
        result = subprocess.run(
            [NODE, str(PROXY_SCRIPT)],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=30,
            env={"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
                 "HOME": str(Path.home())},
        )
    except subprocess.TimeoutExpired:
        return {"error": "MCP proxy timeout (30s)"}

    if result.returncode != 0 and not result.stdout.strip():
        return {"error": f"MCP proxy failed: {result.stderr.strip()[:200]}"}

    # Parse responses — we want id=2 (our actual call)
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            if msg.get("id") == 2:
                if "error" in msg:
                    return {"error": msg["error"].get("message", str(msg["error"]))}
                # Result contains content array
                content = msg.get("result", {}).get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        try:
                            return json.loads(item["text"])
                        except json.JSONDecodeError:
                            return {"text": item["text"]}
                return msg.get("result", {})
        except json.JSONDecodeError:
            continue

    return {"error": "No response from MCP", "stdout": result.stdout[:500], "stderr": result.stderr[:500]}


def create_video(prompt: str, orientation: str = "portrait", files: list | None = None) -> dict:
    """Create video via HeyGen Video Agent (uses account credits)."""
    params = {
        "prompt": prompt,
        "mode": "generate",
        "orientation": orientation,
    }
    if files:
        params["files"] = [{"type": "url", "url": f} for f in files]
    return _call_mcp("create_video_agent", params)


def create_video_from_avatar(script: str, avatar_id: str, voice_id: str = "",
                              aspect_ratio: str = "9:16", title: str = "") -> dict:
    """Create video from specific avatar+voice (uses account credits)."""
    params = {"avatarId": avatar_id, "script": script}
    if voice_id:
        params["voiceId"] = voice_id
    if aspect_ratio:
        params["aspectRatio"] = aspect_ratio
    if title:
        params["title"] = title
    return _call_mcp("create_video_from_avatar", params)


def get_video(video_id: str) -> dict:
    """Check video status."""
    return _call_mcp("get_video", {"videoId": video_id})


def list_avatar_groups(limit: int = 10, ownership: str = "public") -> dict:
    """List avatar groups."""
    return _call_mcp("list_avatar_groups", {"limit": limit, "ownership": ownership})


if __name__ == "__main__":
    # Quick test
    if len(sys.argv) < 2:
        print("Usage: python3 heygen_mcp.py test")
        print("       python3 heygen_mcp.py create 'Your prompt here'")
        print("       python3 heygen_mcp.py status <video_id>")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "test":
        print("Testing MCP connection...")
        result = list_avatar_groups(3)
        print(json.dumps(result, indent=2))
    elif cmd == "create":
        prompt = sys.argv[2] if len(sys.argv) > 2 else "Create a 30 second test video"
        print(f"Creating video: {prompt}")
        result = create_video(prompt)
        print(json.dumps(result, indent=2))
    elif cmd == "status":
        vid = sys.argv[2]
        result = get_video(vid)
        print(json.dumps(result, indent=2))
