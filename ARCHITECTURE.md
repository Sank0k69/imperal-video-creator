# Video Creator Extension — Architecture

## What It Is

An Imperal Cloud extension (Python, SDK v1.5.0+) that contains the entire Creator Monetize methodology as structured knowledge + AI-powered generation modules + a standalone Web UI for video creation via HeyGen.

Two operating modes:
1. **Imperal Extension** — runs inside Imperal Platform (chat commands + DUI panels)
2. **Standalone Web UI** — runs locally at `http://localhost:8910` (no Imperal dependency)

---

## Directory Structure

```
video-creator/
├── main.py                 ← Imperal Extension entry point (536 lines)
├── web.py                  ← Standalone dev server — 67 lines, thin wrapper
├── agent.py                ← CLI agent + Claude API (909 lines)
├── heygen_mcp.py           ← HeyGen MCP bridge (131 lines)
├── taskqueue.py            ← SQLite task queue (458 lines)
├── api/                    ← Web UI API routes (6 modules)
│   ├── __init__.py         ← Router registration (register_all)
│   ├── videos.py           ← My Videos: list, status, hide/unhide, delete
│   ├── generate.py         ← Script/ideas/hooks generation (Claude)
│   ├── heygen.py           ← HeyGen video creation (MCP + REST)
│   ├── assets.py           ← Brand assets listing (local + Figma)
│   ├── queue_api.py        ← Task queue endpoints
│   └── figma.py            ← Figma API (Designer extension bridge)
├── modules/                ← 16 content modules
│   ├── base.py             ← BaseModule class
│   ├── ideation.py         ← Perfect Idea Zone, Commence, Snatch & Twirl
│   ├── framing.py          ← 4-step concept framing
│   ├── packaging.py        ← Want vs Need, title/thumbnail strategy
│   ├── hooks.py            ← 7 psychological hook types
│   ├── scripting.py        ← Tier 1/2/3 script writing
│   ├── pcm.py              ← 6 PCM personality types
│   ├── captions.py         ← Curiosity loops, PCM captions
│   ├── cta.py              ← Platform-specific CTAs
│   ├── publishing.py       ← 6-step pre-publish checklist
│   ├── iteration.py        ← Track, analyze, iterate
│   ├── market_research.py  ← GSB, avatars, trajectories
│   ├── funnel_copy.py      ← VSL, page copy, RCIBO
│   ├── email_sequences.py  ← Promo, nurture, webinar, reactivation
│   ├── sales.py            ← Scripts, objections, offers, pricing
│   ├── launch.py           ← Pre-launch, quick activation, 28-day plan
│   └── video_production.py ← HeyGen integration (create, status, avatars, voices)
├── pipelines/              ← 3 pipeline orchestrators
│   ├── base.py             ← BasePipeline class
│   ├── full_video.py       ← 9-module creation pipeline
│   ├── quick_script.py     ← topic -> hook -> script -> CTA
│   └── batch_content.py    ← Batch scripts for multiple topics
├── ui/                     ← DUI panels for Imperal Platform
│   ├── dashboard.py        ← Main workspace (right panel, 597 lines)
│   ├── settings.py         ← Settings (left panel, 377 lines)
│   ├── sidebar.py          ← Status widget (186 lines)
│   └── calendar.py         ← Content calendar widget (80 lines)
├── knowledge/              ← 21 JSON knowledge files (~94KB total)
├── templates/
│   └── index.html          ← Standalone HTML UI (1900 lines)
├── assets/                 ← Brand assets from Figma
│   ├── graphics/           ← 23 icons + illustrations (PNG)
│   ├── logos/              ← Brand logos
│   ├── backgrounds/        ← Video backgrounds
│   └── footage/            ← B-roll footage
├── tests/                  ← ~200 tests
│   ├── conftest.py         ← Shared fixtures
│   ├── test_modules_base.py
│   ├── test_ideation.py
│   ├── test_hooks.py
│   ├── test_scripting.py
│   ├── test_pcm.py
│   ├── test_captions.py
│   ├── test_cta.py
│   ├── test_pipelines.py
│   └── test_sdk_compat.py  ← 16 SDK compatibility checks
├── config/
│   └── defaults.py         ← Default configuration values
├── imperal.json            ← Extension manifest (Imperal marketplace)
├── manifest.json           ← Extension metadata
├── pyproject.toml          ← Python project config
└── pytest.ini              ← Test configuration
```

---

## How It Works

### Mode 1: Imperal Extension

```
User -> Imperal Platform (chat or DUI panel)
         |
   main.py (chat functions + IPC methods)
         |
   16 modules (BaseModule -> load_knowledge() -> ask_ai() -> ActionResult)
         |
   21 JSON knowledge files
```

**Flow Example: `create_video` pipeline (9 modules)**
1. Ideation -> generates ideas using Perfect Idea Zone
2. Framing -> transforms idea into directed concept (4-step)
3. Packaging -> creates title + thumbnail strategy (Want vs Need)
4. Hooks -> generates hooks (7 psychological triggers)
5. Scripting -> writes script (Tier 1/2/3, Hook-Body-CTA)
6. PCM -> analyzes/enhances for 6 personality types
7. Captions -> generates curiosity/PCM captions
8. CTA -> generates platform-specific call-to-action
9. Publishing -> runs 6-step pre-publish checklist

### Mode 2: Standalone Web UI

```
User -> browser (localhost:8910)
         |
   web.py (FastAPI, 67 lines — registers routers, serves HTML)
         |
   api/*.py (6 route modules — each file = one feature)
         |
   +--> agent.py (Claude API for script generation)
   +--> heygen_mcp.py (MCP bridge for video creation)
   +--> taskqueue.py (async job queue for long tasks)
```

**Web UI pages:**
- **My Videos** — grid with thumbnails, play/download/deploy/hide/delete
- **Editor** — topic, tier, language, format, avatar picker, voice picker, presenters, montage presets, script editor
- **Settings** — HeyGen connection, platform API keys
- **Designer** — Figma component browser

### Mode 3: CLI Agent

```
User -> agent.py (CLI commands)
         |
   +--> Claude API (script generation with knowledge context)
   +--> heygen_mcp.py (video creation)
   +--> Polling loop (status checks until done)
```

Commands: `idea`, `script`, `hooks`, `video`, `status`, `list-avatars`, `list-voices`

---

## Key Design Decisions

1. **Modules don't import each other** — only pipelines wire them together
2. **Knowledge is JSON, not hardcoded** — easy to update without code changes
3. **Every module uses `ctx.ai.complete()`** — the platform handles LLM routing (BYOLLM)
4. **Toggleable per-user** — each module can be enabled/disabled in config
5. **Two video creation paths:**
   - `/api/create-video` — HeyGen REST API (requires API credits)
   - `/api/create-video-mcp` — HeyGen MCP (uses account credits, preferred)
6. **Modular API** — `web.py` is 67 lines; adding a feature = adding a file in `api/`
7. **HTML separate from Python** — `templates/index.html` (1900 lines), no build step
8. **MCP via stdio subprocess** — HeyGen MCP uses Streamable HTTP; stdio proxy bridges it
9. **Task queue is reusable** — same `taskqueue.py` works for Daria and Agent Platform
10. **Agent.py as shared library** — both CLI and web.py import from agent.py

---

## Montage Presets

The montage direction system translates UI settings into HeyGen Video Agent instructions:

| Preset | Energy | Pace | Text Overlays | B-Roll |
|--------|--------|------|---------------|--------|
| TikTok Viral | High | Fast cuts | Bold, large | Frequent |
| ADHD Brain | Maximum | Rapid | Aggressive | Constant |
| Promo | Medium | Balanced | Product-focused | Moderate |
| YouTube Pro | Medium-Low | Professional | Lower thirds | Selective |
| LinkedIn | Low | Corporate | Minimal, clean | Subtle |
| Custom | Configurable | Configurable | Configurable | Configurable |

---

## Knowledge Files (21)

| File | Content |
|------|---------|
| ideation_methods.json | Perfect Idea Zone, Commence, Snatch & Twirl |
| hook_templates.json | 7 hook types, psychological triggers |
| script_structures.json | Tier 1/2/3, Creation System, Typical Sequence |
| packaging_rules.json | Want vs Need, title/thumbnail strategy |
| pcm_types.json | 6 PCM personality types |
| caption_templates.json | Curiosity loops, PCM captions |
| cta_templates.json | 4 CTA categories per platform |
| content_checklist.json | 6-step pre-publish checklist |
| video_formats.json | Short/long form format rules |
| ai_copywriting.json | AI prompting for copy |
| market_research.json | GSB, 7 Tenets, 18 questions, client avatar |
| trajectory_pathways.json | 8 categories, 28-day pathways |
| offer_creation.json | Elixir Genesis 8-step, pricing, guarantees |
| sales_psychology.json | 5 awareness/sophistication stages, 36 tools, Zerbini |
| vsl_templates.json | Call/Value Video VSL 8-section, RCIBO |
| email_sequences.json | Promo, nurture, webinar, reactivation |
| funnels.json | Call/Live Expert/Value Video funnel pages |
| sales_system.json | 12-stage sales script, objection handling |
| community_tracking.json | Community, onboarding, flywheels, hiring |
| traffic_conversion.json | IG/TT/YT systems, CTA hierarchy |
| content_iteration.json | Algorithms, iteration protocol, GSB, PCM |

---

## Modules (16)

| # | Module | Type | Key Actions |
|---|--------|------|-------------|
| 1 | ideation | v1 | generate, classify, bank_add, bank_list |
| 2 | framing | v1 | frame (4-step) |
| 3 | packaging | v1 | package (Want vs Need) |
| 4 | hooks | v1 | generate (7 types) |
| 5 | scripting | v1 | write, rewrite |
| 6 | pcm | v1 | analyze, enhance |
| 7 | captions | v1 | generate |
| 8 | cta | v1 | generate |
| 9 | publishing | v1 | check (6-step) |
| 10 | iteration | v1 | track, analyze |
| 11 | market_research | v2 | gsb_analyze, build_avatar, classify_trajectory, research_questions |
| 12 | funnel_copy | v2 | write_vsl, page_copy, rcibo_prompt, presentation_outline |
| 13 | email_sequences | v2 | promo, nurture, webinar, reactivation, newsletter |
| 14 | sales | v2 | sales_script, handle_objection, create_offer, unique_mechanism, price_anchor |
| 15 | launch | v2 | pre_launch_plan, quick_activation, launch_28_day |
| 16 | video_production | v2 | create_video, check_status, list_avatars, list_voices, clean_script |

---

## Dependencies

- **Imperal SDK v1.5.0+** (imperal_sdk) — for extension mode
- **FastAPI + Uvicorn** — for standalone web server
- **Claude API (Anthropic)** — for script generation
- **HeyGen MCP** — for video creation (account credits)
- **Figma API** — for Designer tab (optional)
- **SQLite3** — for task queue (built into Python)

---

## Code Stats

| Component | Lines |
|-----------|-------|
| main.py | 536 |
| web.py | 67 |
| agent.py | 909 |
| heygen_mcp.py | 131 |
| taskqueue.py | 458 |
| api/*.py (6 files) | 553 |
| ui/*.py (4 panels) | 1,240 |
| modules/*.py (16 + base) | 2,884 |
| templates/index.html | 1,900 |
| tests/*.py | 925 |
| **Total** | **~9,600** |

---

## What's Next

### Immediate
- YouTube Data API v3 integration (publish from Deploy modal)
- TikTok Content Posting API integration
- Instagram Graph API integration (via Meta)
- LinkedIn Share API integration
- Real video status webhooks (replace polling)

### Medium-term
- Celery + Redis upgrade for task queue (multi-server scaling)
- Analytics dashboard (views, engagement, conversion tracking)
- Content calendar automation (scheduled video creation + publishing)
- A/B testing for thumbnails and titles
- Batch video generation with queue management

### Long-term
- Full autonomous video agent (idea -> script -> video -> publish -> analyze -> iterate)
- Multi-language content generation at scale
- Cross-platform performance optimization based on analytics
- Community-driven content suggestions
