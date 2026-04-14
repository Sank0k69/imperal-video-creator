#!/usr/bin/env python3
"""
Video Creator Agent — Autonomous video creation pipeline.

Uses Creator Monetize methodology (knowledge base), Anthropic Claude for
content generation, and HeyGen API for AI avatar video production.

Usage:
    python3 agent.py idea "web hosting"
    python3 agent.py script "why NVMe matters" --tier 2
    python3 agent.py hooks "cloud hosting benefits"
    python3 agent.py video "why NVMe matters"
    python3 agent.py status <video_id>
    python3 agent.py list-avatars
    python3 agent.py list-voices --lang en
"""

import argparse
import json
import os
import sys
import time
import textwrap
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
HEYGEN_API = "https://api.heygen.com"
HEYGEN_KEY = os.getenv("HEYGEN_API_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
# Model routing — haiku for cheap tasks, sonnet for quality tasks
MODEL_FAST = "claude-haiku-4-5-20251001"    # ~$0.25/M in, $1.25/M out
MODEL_SMART = "claude-sonnet-4-20250514"    # ~$3/M in, $15/M out

POLL_INTERVAL = 10  # seconds between HeyGen status checks
POLL_TIMEOUT = 600  # max seconds to wait for video generation

# Default video dimensions (vertical for Reels/TikTok/Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------


def load_knowledge(filename: str) -> dict:
    """Load a JSON knowledge file from the knowledge directory."""
    filepath = KNOWLEDGE_DIR / filename
    if not filepath.exists():
        print(f"[WARN] Knowledge file not found: {filepath}", file=sys.stderr)
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt() -> str:
    """
    Build a comprehensive system prompt from the knowledge base.
    Loaded once at startup and reused for all Claude calls.
    """
    ideation = load_knowledge("ideation_methods.json")
    scripts = load_knowledge("script_structures.json")
    hooks = load_knowledge("hook_templates.json")
    iteration = load_knowledge("content_iteration.json")
    checklist = load_knowledge("content_checklist.json")
    pcm = load_knowledge("pcm_types.json")
    cta = load_knowledge("cta_templates.json")
    video_formats = load_knowledge("video_formats.json")

    # --- Perfect Idea Zone ---
    piz = ideation.get("perfect_idea_zone", {})
    piz_text = (
        f"PERFECT IDEA ZONE: {piz.get('definition', '')}\n"
        f"Test: {piz.get('test', '')}"
    )

    # --- Ideation Methods ---
    methods_text = "IDEATION METHODS:\n"
    for key, method in ideation.get("methods", {}).items():
        methods_text += f"- {method.get('name', key)}: {method.get('description', '')}\n"
        steps = method.get("steps", [])
        if steps:
            for s in steps[:5]:
                methods_text += f"  * {s}\n"

    # --- Hook Types ---
    hooks_text = "7 HOOK TYPES:\n"
    for key, hook in hooks.get("types", {}).items():
        templates = hook.get("templates", [])
        examples = " | ".join(templates[:2])
        hooks_text += f"- {hook.get('name', key)}: {hook.get('trigger', '')} — e.g. {examples}\n"

    # --- Tier Structures ---
    tiers_text = "SCRIPT TIER STRUCTURES:\n"
    for tier_num, tier in scripts.get("tiers", {}).items():
        tiers_text += f"\nTIER {tier_num} — {tier.get('name', '')}:\n"
        tiers_text += f"  Description: {tier.get('description', '')}\n"
        tiers_text += f"  Guidance: {tier.get('guidance', '')}\n"
        structure = tier.get("structure", [])
        if isinstance(structure, list):
            for item in structure:
                if isinstance(item, dict):
                    for k, v in item.items():
                        tiers_text += f"  - {k}: {v}\n"
                else:
                    tiers_text += f"  - {item}\n"

    # --- Short Form Templates ---
    sf_text = "SHORT FORM TEMPLATES:\n"
    for key, tmpl in scripts.get("short_form_templates", {}).items():
        sf_text += f"- {tmpl.get('name', key)}: {tmpl.get('description', '')}\n"
        flow = tmpl.get("flow", [])
        sf_text += f"  Flow: {' → '.join(flow)}\n"

    # --- PCM 6 Types ---
    pcm_text = "PCM — 6 PERSONALITY TYPES (cover 3-6 per script):\n"
    pcm_data = iteration.get("pcm_for_content", {}).get("types", [])
    if not pcm_data:
        pcm_data = []
        for key, val in pcm.get("types", {}).items():
            pcm_data.append(val)
    for pt in pcm_data:
        pct = pt.get("percent", "")
        pct_str = f" ({pct}%)" if pct else ""
        pcm_text += f"- {pt.get('name', '')}{pct_str}: {pt.get('perception', pt.get('trait', ''))}\n"
        triggers = pt.get("script_triggers", pt.get("language", ""))
        if isinstance(triggers, list):
            pcm_text += f"  Triggers: {', '.join(triggers)}\n"
        elif triggers:
            pcm_text += f"  Language: {triggers}\n"

    # --- CTA Structure ---
    cta_structure = cta.get("structure", {})
    cta_text = "CTA STRUCTURE (5 parts):\n"
    for part in cta_structure.get("parts", []):
        cta_text += f"- {part.get('name', '')}: {part.get('description', '')}\n"

    # --- Quality Checklist ---
    qg = checklist.get("quality_gate", {})
    quality_text = "QUALITY CHECKLIST:\n"
    for check in qg.get("self_check", []):
        quality_text += f"- {check}\n"
    quality_text += f"- PCM: {qg.get('pcm_check', '')}\n"
    quality_text += f"- {qg.get('read_aloud', '')}\n"

    # --- Pre-script Fields ---
    pre_fields = scripts.get("pre_script_fields", {})
    pre_text = "PRE-SCRIPT FIELDS (fill before writing):\n"
    for field in pre_fields.get("fields", []):
        pre_text += f"- {field.get('field', '')}: {field.get('description', '')}\n"

    # --- Algorithm ---
    algo = iteration.get("algorithm_framework", {})
    algo_text = (
        f"CONTENT ASCENDANCY: {algo.get('formula', '')}\n"
        f"Core metric: {algo.get('core_metric', '')}\n"
    )

    # --- Scripting Principles ---
    principles_text = "SCRIPTING PRINCIPLES:\n"
    for p in scripts.get("principles", []):
        principles_text += f"- {p.get('name', '')}: {p.get('description', '')}\n"

    # --- Content Types ---
    ct = scripts.get("content_types", {})
    ct_text = "CONTENT TYPES:\n"
    for key, val in ct.items():
        ct_text += f"- {val.get('name', key)}: {val.get('description', '')}\n"

    system_prompt = textwrap.dedent(f"""\
    You are a professional short-form video scriptwriter and content strategist,
    trained on the Creator Monetize methodology. You create scripts optimized for
    maximum viewer retention, engagement, and conversion.

    You write for AI avatar videos (HeyGen) — direct-to-camera, talking head style.
    Scripts must sound natural when spoken aloud. No stage directions, no visual cues,
    no "[pause]" markers. Write ONLY the spoken words.

    === FRAMEWORKS ===

    {piz_text}

    {methods_text}

    {hooks_text}

    {tiers_text}

    {sf_text}

    {pcm_text}

    {cta_text}

    {algo_text}

    {principles_text}

    {ct_text}

    {pre_text}

    {quality_text}

    === RULES ===
    1. Every script MUST start with a hook (first 3 seconds grab attention).
    2. Every script MUST end with a clear CTA.
    3. Cover at least 3 PCM personality types per script.
    4. Write for spoken delivery — short sentences, conversational tone.
    5. No filler phrases. Every sentence must earn its place.
    6. For Tier 1: 60-90 seconds. For Tier 2/3: 2-5 minutes.
    7. Output ONLY the spoken script text. No formatting, no markdown headers.
    """)

    return system_prompt


# Tiered system prompts — loaded lazily, cached per tier
_PROMPT_CACHE: dict[str, str] = {}


def get_system_prompt(tier: str = "full") -> str:
    """
    Get tiered system prompt. Smaller = fewer tokens = cheaper.

    Tiers:
      "mini"   ~500 tokens  — ideas, hooks, captions (use with haiku)
      "medium" ~1200 tokens — scripts Tier 1, CTAs
      "full"   ~2500 tokens — scripts Tier 2/3, VSLs, complex tasks
    """
    if tier in _PROMPT_CACHE:
        return _PROMPT_CACHE[tier]

    if tier == "mini":
        prompt = _build_mini_prompt()
    elif tier == "medium":
        prompt = _build_medium_prompt()
    else:
        prompt = build_system_prompt()

    _PROMPT_CACHE[tier] = prompt
    return prompt


def _build_mini_prompt() -> str:
    """Minimal prompt for simple generation tasks (~500 tokens)."""
    hooks = load_knowledge("hook_templates.json")
    hooks_text = ", ".join(hooks.get("types", {}).keys())

    return textwrap.dedent(f"""\
    You are a video content expert using Creator Monetize methodology.
    Write for AI avatar (talking head, direct-to-camera). Natural spoken tone only.

    7 HOOK TYPES: {hooks_text}
    PCM 6 TYPES: Harmonizer(30%), Thinker(25%), Rebel(20%), Promoter(10%), Imaginer(10%), Persister(5%)

    RULES: Hook in first 3s. CTA at end. Cover 3+ PCM types. No filler. Only spoken words.
    Return ONLY valid JSON, no markdown fences.""")


def _build_medium_prompt() -> str:
    """Medium prompt for scripting tasks (~1200 tokens)."""
    scripts = load_knowledge("script_structures.json")
    hooks = load_knowledge("hook_templates.json")

    hooks_text = ""
    for key, hook in hooks.get("types", {}).items():
        hooks_text += f"- {hook.get('name', key)}: {hook.get('trigger', '')}\n"

    tiers_text = ""
    for tid, t in scripts.get("tiers", {}).items():
        tiers_text += f"TIER {tid}: {t.get('name','')} — {t.get('description','')}\n"

    return textwrap.dedent(f"""\
    You are a professional video scriptwriter trained on Creator Monetize methodology.
    Write for AI avatar videos — direct-to-camera, natural spoken tone.
    ONLY the spoken words. No stage directions, no visual cues.

    HOOKS:\n{hooks_text}
    TIERS:\n{tiers_text}
    PCM 6 TYPES: Harmonizer(30%), Thinker(25%), Rebel(20%), Promoter(10%), Imaginer(10%), Persister(5%)

    RULES:
    1. Hook in first 3 seconds. CTA at end. Cover 3+ PCM types.
    2. Tier 1: 60-90s (~150-220 words). Tier 2/3: 2-4 min (~300-600 words).
    3. Every sentence must earn its place. No filler.
    4. Conversational, short sentences. Written for speaking.
    Return ONLY valid JSON, no markdown fences.""")


# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------


def ask_claude(
    prompt: str,
    system: str = "",
    max_tokens: int = 2048,
    model: str = "",
    use_cache: bool = True,
) -> str:
    """
    Call Anthropic Messages API with prompt caching and model routing.

    Args:
        prompt: User message
        system: System prompt (uses task-specific prompt if empty)
        max_tokens: Max response tokens (keep low to save money)
        model: Model override. Default uses MODEL_FAST.
        use_cache: Enable prompt caching (saves ~90% on repeated system prompts)
    """
    if not ANTHROPIC_KEY:
        print("[ERROR] ANTHROPIC_API_KEY not set.", file=sys.stderr)
        raise RuntimeError("Agent error")

    if not system:
        system = get_system_prompt()

    if not model:
        model = MODEL_FAST

    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    # Prompt caching: system prompt cached for 5 min (saves ~90% on input tokens)
    if use_cache:
        headers["anthropic-beta"] = "prompt-caching-2024-07-31"
        system_block = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    else:
        system_block = system

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_block,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(ANTHROPIC_API, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            # Log token usage for monitoring
            usage = data.get("usage", {})
            cached = usage.get("cache_read_input_tokens", 0)
            total_in = usage.get("input_tokens", 0)
            total_out = usage.get("output_tokens", 0)
            cache_created = usage.get("cache_creation_input_tokens", 0)
            print(f"[TOKENS] in={total_in} out={total_out} cached={cached} cache_write={cache_created} model={model}", file=sys.stderr)

            content = data.get("content", [])
            texts = [block["text"] for block in content if block.get("type") == "text"]
            return "\n".join(texts)
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Claude API {e.response.status_code}: {e.response.text}", file=sys.stderr)
        raise RuntimeError("Agent error")
    except httpx.RequestError as e:
        print(f"[ERROR] Claude API request failed: {e}", file=sys.stderr)
        raise RuntimeError("Agent error")


# ---------------------------------------------------------------------------
# HeyGen API
# ---------------------------------------------------------------------------


def heygen_request(method: str, path: str, json_data: dict | None = None) -> dict:
    """
    Make an authenticated request to the HeyGen API.
    Returns the parsed JSON response.
    """
    if not HEYGEN_KEY:
        print("[ERROR] HEYGEN_API_KEY not set.", file=sys.stderr)
        raise RuntimeError("Agent error")

    url = f"{HEYGEN_API}{path}"
    headers = {
        "x-api-key": HEYGEN_KEY,
        "content-type": "application/json",
    }

    try:
        with httpx.Client(timeout=60) as client:
            if method.upper() == "GET":
                resp = client.get(url, headers=headers)
            elif method.upper() == "POST":
                resp = client.post(url, headers=headers, json=json_data or {})
            else:
                print(f"[ERROR] Unsupported HTTP method: {method}", file=sys.stderr)
                raise RuntimeError("Agent error")

            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] HeyGen API {e.response.status_code}: {e.response.text}", file=sys.stderr)
        raise RuntimeError("Agent error")
    except httpx.RequestError as e:
        print(f"[ERROR] HeyGen API request failed: {e}", file=sys.stderr)
        raise RuntimeError("Agent error")


# ---------------------------------------------------------------------------
# Avatars & Voices
# ---------------------------------------------------------------------------


def list_avatars() -> list[dict]:
    """List available HeyGen avatars. Returns simplified list."""
    data = heygen_request("GET", "/v2/avatars")
    avatars_raw = data.get("data", {}).get("avatars", [])

    avatars = []
    for av in avatars_raw:
        avatars.append({
            "avatar_id": av.get("avatar_id", ""),
            "avatar_name": av.get("avatar_name", ""),
            "gender": av.get("gender", ""),
            "avatar_type": av.get("type", ""),
        })
    return avatars


def list_voices(lang: str = "en") -> list[dict]:
    """List available HeyGen voices, optionally filtered by language."""
    data = heygen_request("GET", "/v2/voices")
    voices_raw = data.get("data", {}).get("voices", [])

    voices = []
    for v in voices_raw:
        voice_lang = v.get("language", "")
        if lang and not voice_lang.lower().startswith(lang.lower()):
            continue
        voices.append({
            "voice_id": v.get("voice_id", ""),
            "name": v.get("name", v.get("display_name", "")),
            "language": voice_lang,
            "gender": v.get("gender", ""),
        })
    return voices


def pick_default_avatar() -> str:
    """Pick a sensible default avatar from available ones."""
    avatars = list_avatars()
    if not avatars:
        print("[ERROR] No avatars available in your HeyGen account.", file=sys.stderr)
        raise RuntimeError("Agent error")

    # Prefer talking_photo type, then normal style
    for av in avatars:
        if av.get("avatar_type") == "talking_photo":
            return av["avatar_id"]

    # Fallback: first available
    return avatars[0]["avatar_id"]


def pick_default_voice(lang: str = "en") -> str:
    """Pick a sensible default English voice."""
    voices = list_voices(lang)
    if not voices:
        print(f"[ERROR] No voices available for language: {lang}", file=sys.stderr)
        raise RuntimeError("Agent error")
    return voices[0]["voice_id"]


# ---------------------------------------------------------------------------
# Content Generation
# ---------------------------------------------------------------------------


def generate_ideas(topic: str, count: int = 5) -> dict:
    """Generate video ideas using ideation methodology. Uses HAIKU (cheap)."""
    prompt = textwrap.dedent(f"""\
    Generate {count} video ideas about: "{topic}"

    For each idea provide:
    1. Title (compelling, specific)
    2. Hook angle (which hook type works best)
    3. Target audience
    4. Content type (static or dynamic)
    5. Estimated tier (1, 2, or 3)

    Apply Snatch & Twirl: take proven concepts, add a unique spin.

    Return as a JSON array of objects with keys: title, hook_angle, target, content_type, tier
    """)

    result = ask_claude(prompt, system=get_system_prompt("mini"), max_tokens=1024, model=MODEL_FAST)

    # Try to parse JSON from response
    try:
        # Handle possible markdown fences
        cleaned = result.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last fence lines
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        ideas = json.loads(cleaned)
        return {"topic": topic, "count": len(ideas), "ideas": ideas}
    except json.JSONDecodeError:
        return {"topic": topic, "raw_response": result}


def write_script(topic: str, tier: int = 1) -> dict:
    """Write a video script. Tier 1 uses HAIKU+medium, Tier 2/3 uses SONNET+full."""
    tier_str = str(tier)
    scripts_kb = load_knowledge("script_structures.json")
    tier_info = scripts_kb.get("tiers", {}).get(tier_str, {})

    if not tier_info:
        print(f"[ERROR] Invalid tier: {tier}. Use 1, 2, or 3.", file=sys.stderr)
        raise RuntimeError("Agent error")

    # Model routing: simple scripts → haiku, complex → sonnet
    if tier == 1:
        model = MODEL_FAST
        prompt_tier = "medium"
        max_tok = 1024
    else:
        model = MODEL_SMART
        prompt_tier = "full"
        max_tok = 2048

    prompt = textwrap.dedent(f"""\
    Write a complete video script about: "{topic}"

    Use TIER {tier} structure: {tier_info.get('name', '')} — {tier_info.get('description', '')}
    Guidance: {tier_info.get('guidance', '')}

    ONLY the words to be spoken aloud. Natural, conversational.
    Tier 1: 60-90s (~150-220 words). Tier 2/3: 2-4 min (~300-600 words).

    Return JSON: {{title, hook_type, tier, target, transformation, pcm_types_covered, script, word_count, estimated_duration_seconds}}
    """)

    result = ask_claude(prompt, system=get_system_prompt(prompt_tier), max_tokens=max_tok, model=model)

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        script_data = json.loads(cleaned)
        script_data["topic"] = topic
        return script_data
    except json.JSONDecodeError:
        return {"topic": topic, "tier": tier, "raw_response": result}


def rewrite_script(original_script: str, prompt: str) -> dict:
    """Rewrite a script based on user instructions. Uses HAIKU (cheap)."""
    user_prompt = textwrap.dedent(f"""\
    Here is an existing video script:

    ---
    {original_script}
    ---

    The user wants to change it. Their instruction: "{prompt}"

    Rewrite the script following the instruction. Keep the same overall structure
    and topic, but apply the requested changes. Write ONLY the spoken words.

    Return JSON: {{"script": "the rewritten script text", "changes_made": "brief description of what changed"}}
    """)

    result = ask_claude(user_prompt, system=get_system_prompt("medium"), max_tokens=1024, model=MODEL_FAST)

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        data = json.loads(cleaned)
        return data
    except json.JSONDecodeError:
        return {"script": result, "changes_made": "Rewritten based on: " + prompt}


def generate_hooks(topic: str, count: int = 5) -> dict:
    """Generate hook variations. Uses HAIKU (cheap)."""
    prompt = textwrap.dedent(f"""\
    Generate {count} hook variations for a video about: "{topic}"

    For each hook provide:
    1. The hook text (exactly as spoken in first 3 seconds)
    2. The hook type used (from the 7 types)
    3. Why it works (one sentence)

    Punchy, specific, attention-grabbing. For AI avatar direct-to-camera.

    Return JSON array: [{{text, type, reasoning}}]
    """)

    result = ask_claude(prompt, system=get_system_prompt("mini"), max_tokens=1024, model=MODEL_FAST)

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        hooks_list = json.loads(cleaned)
        return {"topic": topic, "count": len(hooks_list), "hooks": hooks_list}
    except json.JSONDecodeError:
        return {"topic": topic, "raw_response": result}


# ---------------------------------------------------------------------------
# HeyGen Video Creation
# ---------------------------------------------------------------------------


def create_video(
    script_text: str,
    avatar_id: str | None = None,
    voice_id: str | None = None,
    title: str = "Generated Video",
) -> dict:
    """
    Create a video via HeyGen v2 API.
    Returns the video_id for status polling.
    """
    if not avatar_id:
        print("[INFO] Picking default avatar...", file=sys.stderr)
        avatar_id = pick_default_avatar()
        print(f"[INFO] Using avatar: {avatar_id}", file=sys.stderr)

    if not voice_id:
        print("[INFO] Picking default voice...", file=sys.stderr)
        voice_id = pick_default_voice("en")
        print(f"[INFO] Using voice: {voice_id}", file=sys.stderr)

    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": script_text,
                    "voice_id": voice_id,
                },
            }
        ],
        "dimension": {"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
        "title": title,
    }

    print("[INFO] Submitting video to HeyGen...", file=sys.stderr)
    data = heygen_request("POST", "/v2/video/generate", payload)

    video_id = data.get("data", {}).get("video_id", "")
    if not video_id:
        print(f"[ERROR] No video_id in response: {json.dumps(data, indent=2)}", file=sys.stderr)
        raise RuntimeError("Agent error")

    return {
        "video_id": video_id,
        "avatar_id": avatar_id,
        "voice_id": voice_id,
        "status": "submitted",
        "title": title,
    }


def check_status(video_id: str) -> dict:
    """Check the status of a HeyGen video generation job."""
    data = heygen_request("GET", f"/v1/video_status.get?video_id={video_id}")
    video_data = data.get("data", {})

    result = {
        "video_id": video_id,
        "status": video_data.get("status", "unknown"),
    }

    if video_data.get("video_url"):
        result["video_url"] = video_data["video_url"]
    if video_data.get("thumbnail_url"):
        result["thumbnail_url"] = video_data["thumbnail_url"]
    if video_data.get("duration"):
        result["duration"] = video_data["duration"]
    if video_data.get("error"):
        result["error"] = video_data["error"]

    return result


def poll_until_done(video_id: str) -> dict:
    """Poll HeyGen until video is completed or failed."""
    elapsed = 0
    while elapsed < POLL_TIMEOUT:
        status = check_status(video_id)
        current = status.get("status", "unknown")

        print(f"[INFO] Status: {current} ({elapsed}s elapsed)", file=sys.stderr)

        if current == "completed":
            return status
        elif current in ("failed", "error"):
            print(f"[ERROR] Video generation failed: {json.dumps(status, indent=2)}", file=sys.stderr)
            return status

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    print(f"[ERROR] Timed out after {POLL_TIMEOUT}s waiting for video.", file=sys.stderr)
    return {"video_id": video_id, "status": "timeout", "elapsed": elapsed}


# ---------------------------------------------------------------------------
# Full Pipeline
# ---------------------------------------------------------------------------


def full_pipeline(
    topic: str,
    tier: int = 1,
    avatar_id: str | None = None,
    voice_id: str | None = None,
) -> dict:
    """
    Full autonomous pipeline:
    1. Generate script with Claude
    2. Create video with HeyGen
    3. Poll until complete
    4. Return video URL
    """
    print(f"[PIPELINE] Starting full pipeline for: \"{topic}\"", file=sys.stderr)
    print(f"[PIPELINE] Tier: {tier}", file=sys.stderr)

    # Step 1: Write script
    print("[PIPELINE] Step 1/3 — Generating script...", file=sys.stderr)
    script_data = write_script(topic, tier=tier)

    script_text = script_data.get("script", "")
    if not script_text:
        # Fallback if Claude returned raw text
        script_text = script_data.get("raw_response", "")
        if not script_text:
            print("[ERROR] Failed to generate script.", file=sys.stderr)
            raise RuntimeError("Agent error")

    title = script_data.get("title", topic)
    word_count = len(script_text.split())

    print(f"[PIPELINE] Script generated: \"{title}\" ({word_count} words)", file=sys.stderr)

    # Step 2: Create video
    print("[PIPELINE] Step 2/3 — Creating video via HeyGen...", file=sys.stderr)
    video_info = create_video(
        script_text=script_text,
        avatar_id=avatar_id,
        voice_id=voice_id,
        title=title,
    )

    video_id = video_info["video_id"]
    print(f"[PIPELINE] Video submitted: {video_id}", file=sys.stderr)

    # Step 3: Poll until done
    print("[PIPELINE] Step 3/3 — Waiting for video generation...", file=sys.stderr)
    final_status = poll_until_done(video_id)

    # Combine all data
    result = {
        "pipeline": "complete",
        "topic": topic,
        "tier": tier,
        "script": {
            "title": title,
            "word_count": word_count,
            "hook_type": script_data.get("hook_type", ""),
            "pcm_types_covered": script_data.get("pcm_types_covered", []),
            "text": script_text,
        },
        "video": final_status,
    }

    if final_status.get("video_url"):
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"  VIDEO READY: {final_status['video_url']}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def output(data: dict | list) -> None:
    """Print formatted JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="Video Creator Agent — autonomous video creation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        Examples:
          python3 agent.py idea "web hosting"
          python3 agent.py script "why NVMe matters" --tier 2
          python3 agent.py hooks "cloud hosting benefits"
          python3 agent.py video "why NVMe matters" --tier 2
          python3 agent.py status abc123
          python3 agent.py list-avatars
          python3 agent.py list-voices --lang en
        """),
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- idea ---
    p_idea = subparsers.add_parser("idea", help="Generate video ideas for a topic")
    p_idea.add_argument("topic", help="Topic to generate ideas about")
    p_idea.add_argument("--count", type=int, default=5, help="Number of ideas (default: 5)")

    # --- script ---
    p_script = subparsers.add_parser("script", help="Write a video script")
    p_script.add_argument("topic", help="Topic to write a script about")
    p_script.add_argument("--tier", type=int, default=1, choices=[1, 2, 3],
                          help="Script tier: 1=Simple, 2=Setup/Stress/Payoff, 3=Fully Written (default: 1)")

    # --- hooks ---
    p_hooks = subparsers.add_parser("hooks", help="Generate hook variations")
    p_hooks.add_argument("topic", help="Topic to generate hooks for")
    p_hooks.add_argument("--count", type=int, default=5, help="Number of hooks (default: 5)")

    # --- video ---
    p_video = subparsers.add_parser("video", help="Full pipeline: script + HeyGen video")
    p_video.add_argument("topic", help="Topic for the video")
    p_video.add_argument("--tier", type=int, default=1, choices=[1, 2, 3],
                         help="Script tier (default: 1)")
    p_video.add_argument("--avatar", default=None, help="HeyGen avatar ID (auto-picks if omitted)")
    p_video.add_argument("--voice", default=None, help="HeyGen voice ID (auto-picks if omitted)")

    # --- status ---
    p_status = subparsers.add_parser("status", help="Check HeyGen video generation status")
    p_status.add_argument("video_id", help="HeyGen video ID to check")

    # --- list-avatars ---
    subparsers.add_parser("list-avatars", help="List available HeyGen avatars")

    # --- list-voices ---
    p_voices = subparsers.add_parser("list-voices", help="List available HeyGen voices")
    p_voices.add_argument("--lang", default="en", help="Filter by language code (default: en, use 'all' for all)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        raise RuntimeError("Agent error")

    # Dispatch commands
    if args.command == "idea":
        output(generate_ideas(args.topic, count=args.count))

    elif args.command == "script":
        output(write_script(args.topic, tier=args.tier))

    elif args.command == "hooks":
        output(generate_hooks(args.topic, count=args.count))

    elif args.command == "video":
        output(full_pipeline(
            topic=args.topic,
            tier=args.tier,
            avatar_id=args.avatar,
            voice_id=args.voice,
        ))

    elif args.command == "status":
        output(check_status(args.video_id))

    elif args.command == "list-avatars":
        avatars = list_avatars()
        output({"count": len(avatars), "avatars": avatars})

    elif args.command == "list-voices":
        lang = args.lang if args.lang != "all" else ""
        voices = list_voices(lang)
        output({"count": len(voices), "language_filter": args.lang, "voices": voices})


if __name__ == "__main__":
    main()
