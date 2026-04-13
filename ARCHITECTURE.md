# Video Creator Extension — Architecture & Status

## What It Is

An Imperal Cloud extension (Python, SDK v1.5.0) that contains the ENTIRE Creator Monetize methodology as structured knowledge + AI-powered generation modules.

## How It Works

```
User → Imperal Platform (chat or UI panel)
         ↓
  extension.py (31 chat functions, 6 IPC methods)
         ↓
  15 modules (each: BaseModule → load_knowledge() → ask_ai() → ActionResult)
         ↓
  21 JSON knowledge files (frameworks, templates, structures from Creator Monetize course)
```

### Flow Example: "create_video" pipeline
1. Ideation module → generates ideas using Perfect Idea Zone
2. Framing module → transforms idea into directed concept (4-step framing)
3. Packaging module → creates title + thumbnail strategy
4. Hooks module → generates hooks (7 psychological triggers)
5. Scripting module → writes script (Tier 1/2/3, Hook-Body-CTA)
6. PCM module → analyzes/enhances for 6 personality types
7. Captions module → generates curiosity/PCM captions
8. CTA module → generates platform-specific call-to-action
9. Publishing module → runs 6-step pre-publish checklist

### Key Design Decisions
- **Modules don't import each other** — only pipelines wire them together
- **Knowledge is JSON, not hardcoded** — easy to update without code changes
- **Every module uses ctx.ai.chat()** — the platform handles LLM routing (BYOLLM)
- **Toggleable per-user** — each module can be enabled/disabled in config

## What It Does NOT Do (Yet)

1. **No video creation** — generates scripts/strategy, not actual video files
2. **No HeyGen integration** — no Avatar IV, no voice synthesis, no B-roll
3. **No social media publishing** — no YouTube/Instagram/TikTok API calls
4. **No analytics tracking** — no real performance data collection
5. **No content calendar automation** — scheduled reminder only

## File Inventory

### Knowledge (21 files)
| File | Version | Content |
|------|---------|---------|
| ideation_methods.json | v1.0 | Perfect Idea Zone, Commence, Snatch & Twirl |
| hook_templates.json | v1.0 | 7 hook types, psychological triggers |
| script_structures.json | v2.0 | Tier 1/2/3, Creation System, Typical Sequence |
| packaging_rules.json | v1.0 | Want vs Need, title/thumbnail strategy |
| pcm_types.json | v1.0 | 6 PCM personality types |
| caption_templates.json | v1.0 | Curiosity loops, PCM captions |
| cta_templates.json | v1.0 | 4 CTA categories per platform |
| content_checklist.json | v1.0 | 6-step pre-publish checklist |
| video_formats.json | v1.0 | Short/long form format rules |
| ai_copywriting.json | v1.0 | AI prompting for copy |
| market_research.json | v2.0 | GSB, 7 Tenets, 18 questions, client avatar |
| trajectory_pathways.json | v2.0 | 8 categories, 28-day pathways |
| offer_creation.json | v2.0 | Elixir Genesis 8-step, pricing, guarantees |
| sales_psychology.json | v2.0 | 5 awareness/sophistication stages, 36 tools, Zerbini |
| vsl_templates.json | v2.0 | Call/Value Video VSL 8-section, RCIBO |
| email_sequences.json | v2.0 | Promo, nurture, webinar, reactivation |
| funnels.json | v2.0 | Call/Live Expert/Value Video funnel pages |
| sales_system.json | v2.0 | 12-stage sales script, objection handling |
| community_tracking.json | v2.0 | Community, onboarding, flywheels, hiring |
| traffic_conversion.json | v2.0 | IG/TT/YT systems, CTA hierarchy |
| content_iteration.json | v2.0 | Algorithms, iteration protocol, GSB, PCM |

### Modules (15)
| Module | Type | Actions |
|--------|------|---------|
| ideation | v1 original | generate, classify, bank_add, bank_list |
| framing | v1 original | frame (4-step) |
| packaging | v1 original | package (Want vs Need) |
| hooks | v1 original | generate (7 types) |
| scripting | v1 original | write, rewrite |
| pcm | v1 original | analyze, enhance |
| captions | v1 original | generate |
| cta | v1 original | generate |
| publishing | v1 original | check (6-step) |
| iteration | v1 original | track, analyze |
| market_research | v2 new | gsb_analyze, build_avatar, classify_trajectory, research_questions |
| funnel_copy | v2 new | write_vsl, page_copy, rcibo_prompt, presentation_outline |
| email_sequences | v2 new | promo_sequence, nurture_sequence, webinar_sequence, reactivation, newsletter |
| sales | v2 new | sales_script, handle_objection, create_offer, unique_mechanism, price_anchor |
| launch | v2 new | pre_launch_plan, quick_activation, launch_28_day |

### Pipelines (3)
- full_video — full creation pipeline (9 modules)
- quick_script — fast pipeline (topic → hook → script → CTA)
- batch_content — batch scripts for multiple topics

### UI Panels (3)
- dashboard — overview panel
- settings — config panel
- calendar — content calendar

### Tests
- 11 tests (v1.0.0 modules only, new modules untested)

## Dependencies
- Imperal SDK v1.5.0 (imperal_sdk)
- Imperal platform must be running to deploy
- No external API dependencies (all generation via ctx.ai)

## What's Needed to Become a Real Video Agent

### Option A: HeyGen Integration (via extension)
- Add HeyGen API calls via ctx.http
- Avatar IV video creation from scripts
- Voice synthesis (175+ languages)
- B-roll generation (Sora 2 / Veo 3.1)
- Cost: ~6 credits/min for Avatar IV

### Option B: HeyGen MCP (via Claude Code)
- HeyGen Remote MCP: https://mcp.heygen.com/mcp/v1/
- OAuth authentication
- Direct video creation from Claude Code
- No Imperal dependency

### Option C: Standalone Agent (no Imperal)
- Python script with HeyGen API + knowledge base
- Run locally or on VPS
- Full autonomy: script → video → publish
- No marketplace, but works TODAY

### Publishing Integrations Needed
- YouTube Data API v3
- Instagram Graph API (via Meta)
- TikTok Content Posting API
- LinkedIn Share API

### Analytics Integrations Needed
- YouTube Analytics API
- Instagram Insights API
- TikTok Analytics API
