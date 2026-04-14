<div align="center">

# Video Creator

### AI-powered video content agent for Imperal Cloud.

**Script generation. HeyGen avatar videos. Task queue. Full publishing pipeline.**

[![Imperal SDK](https://img.shields.io/badge/imperal--sdk-%E2%89%A51.5.0-blue)](https://pypi.org/project/imperal-sdk/)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.11-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue)](LICENSE)

[Features](#-features) | [Quick Start](#-quick-start) | [Architecture](#-architecture) | [Modules](#-modules) | [API](#-api) | [Imperal Platform](https://imperal.io)

</div>

---

## What is Video Creator?

Video Creator is an **Imperal Cloud extension** that turns a topic into a publish-ready video — from ideation through scripting, avatar generation, and multi-platform publishing.

Built on the **Creator Monetize methodology**, it encodes 10+ proven frameworks (hook psychology, PCM personality targeting, tiered scripting, packaging strategy) as structured knowledge, then orchestrates them through AI-powered modules and pipelines.

```bash
# From topic to script in one command
python3 agent.py script "why NVMe hosting matters" --tier 2

# From script to HeyGen avatar video
python3 agent.py video "why NVMe hosting matters"

# Check video status
python3 agent.py status <video_id>
```

---

## Features

| Feature | Description |
|---------|-------------|
| **15 Content Modules** | Ideation, Framing, Packaging, Hooks, Scripting, PCM, Captions, CTA, Publishing, Iteration, Market Research, Funnel Copy, Email Sequences, Sales, Launch |
| **HeyGen Integration** | AI avatar videos with voice synthesis, automatic polling, vertical/horizontal formats |
| **Task Queue** | SQLite-backed async queue with status tracking, retry logic, and REST API |
| **3 Pipelines** | Full Video (9-step), Quick Script, Batch Content |
| **21 Knowledge Files** | Structured JSON frameworks — hook templates, script tiers, PCM types, CTA patterns |
| **Creator Monetize Method** | Perfect Idea Zone, 7 psychological triggers, 6 PCM personality types, tiered scripts |
| **Multi-Platform** | YouTube, TikTok, Instagram Reels, LinkedIn — format-aware output |
| **REST API** | FastAPI endpoints for video generation, asset management, queue monitoring |
| **Figma Integration** | Pull brand assets via the Designer extension (IPC) |
| **Per-User Config** | Every module toggleable, custom niche, audience, brand voice, platform keys |

---

## Quick Start

### As Imperal Extension

```bash
pip install imperal-sdk
git clone https://github.com/Sank0k69/video-creator.git
cd video-creator
pip install -e ".[dev]"
```

Configure in `imperal.json` or through the Imperal platform settings:

```json
{
  "niche": "web hosting",
  "target_audience": "small business owners",
  "language": "en",
  "platforms": {
    "youtube": { "enabled": true }
  }
}
```

### Standalone Agent

```bash
# Set API keys
export HEYGEN_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Generate ideas
python3 agent.py idea "cloud hosting"

# Generate a full script with hooks
python3 agent.py script "why uptime matters" --tier 2

# Create an avatar video
python3 agent.py video "why uptime matters"

# List available HeyGen avatars
python3 agent.py list-avatars
```

### Run Tests

```bash
pytest
```

---

## Architecture

```
User (chat or API)
     |
     v
main.py — Extension + ChatExtension (31 functions, 6 IPC methods)
     |
     +--- Pipelines (orchestrate multi-step workflows)
     |       full_video.py    — 9-step idea-to-publish
     |       quick_script.py  — fast script generation
     |       batch_content.py — bulk content runs
     |
     +--- 15 Modules (each self-contained)
     |       ideation → framing → packaging → hooks → scripting
     |       pcm → captions → cta → publishing → iteration
     |       market_research → funnel_copy → email_sequences → sales → launch
     |
     +--- Knowledge (21 JSON files)
     |       hook_templates, script_structures, pcm_types, ...
     |
     +--- agent.py — CLI agent (Claude + HeyGen direct integration)
     |
     +--- api/ — REST API (FastAPI)
     |       generate, videos, queue, assets, figma, heygen
     |
     +--- taskqueue.py — SQLite async task queue
```

### Design Principles

- **Modules don't import each other** — only pipelines wire them together
- **Knowledge is JSON, not hardcoded** — update frameworks without code changes
- **Every module uses `ctx.ai.complete()`** — the platform handles LLM routing (BYOLLM)
- **Toggleable per-user** — each module can be enabled/disabled in config
- **BaseModule contract** — every module inherits `BaseModule` with `execute()`, `ask_ai()`, `save()`, `load()`

---

## Modules

| Module | Purpose |
|--------|---------|
| **Ideation** | Generate video ideas using Perfect Idea Zone, Commence, Snatch & Twirl methods |
| **Framing** | Transform raw ideas into directed concepts (4-step framing) |
| **Packaging** | Title + thumbnail strategy using Want vs Need framework |
| **Hooks** | Generate hooks using 7 psychological triggers |
| **Scripting** | Write full scripts — Tier 1 (short), Tier 2 (medium), Tier 3 (long) |
| **PCM** | Analyze and enhance content for 6 personality types |
| **Captions** | Generate curiosity-loop and PCM-targeted captions |
| **CTA** | Platform-specific call-to-action generation |
| **Publishing** | 6-step pre-publish checklist and scheduling |
| **Iteration** | Performance analysis and content improvement |
| **Market Research** | GSB analysis, 7 Tenets, client avatar building |
| **Funnel Copy** | VSL scripts, landing pages, opt-in copy |
| **Email Sequences** | Automated email flows for launches and nurture |
| **Sales** | Offer creation, objection handling, closing scripts |
| **Launch** | Full launch playbooks and trajectory pathways |

---

## API

### CLI Agent

```bash
python3 agent.py idea <topic>              # Generate video ideas
python3 agent.py script <topic> [--tier N] # Generate script (tier 1/2/3)
python3 agent.py hooks <topic>             # Generate hooks only
python3 agent.py video <topic>             # Full pipeline: script + HeyGen video
python3 agent.py status <video_id>         # Check HeyGen video status
python3 agent.py list-avatars              # List available HeyGen avatars
python3 agent.py list-voices [--lang en]   # List available voices
```

### REST API (FastAPI)

```
POST /api/generate          — Start video generation pipeline
GET  /api/videos             — List generated videos
GET  /api/videos/{id}        — Get video details
GET  /api/queue              — Task queue status
POST /api/assets/figma       — Pull assets from Figma
POST /api/heygen/create      — Create HeyGen video directly
```

### IPC (Inter-Extension)

Other Imperal extensions can call Video Creator functions:

```python
result = await ctx.extensions.call("video-creator", "generate_script",
                                    topic="web hosting", tier=2)
```

---

## Configuration

All config lives in `imperal.json` or the Imperal platform settings panel:

| Key | Type | Description |
|-----|------|-------------|
| `niche` | string | Your content niche |
| `target_audience` | string | Who you're creating for |
| `brand_voice` | list | Tone descriptors |
| `language` | string | Output language (default: `en`) |
| `platforms.*` | object | Per-platform enable/disable + API keys |
| `content.caption_style` | string | `curiosity` or `pcm` |
| `quality.hook_max_seconds` | int | Max hook duration (default: 3) |
| `quality.pcm_min_types` | int | Min PCM types to target (default: 3) |
| `modules.*` | bool | Enable/disable individual modules |

---

## Links

- **Imperal Platform:** [imperal.io](https://imperal.io)
- **Imperal SDK:** [github.com/imperalcloud/imperal-sdk](https://github.com/imperalcloud/imperal-sdk)
- **License:** [AGPL-3.0](LICENSE)

---

<div align="center">

**Built for [Imperal Cloud](https://imperal.io)**

</div>
