# Context Sync — Auto-Updated Status
<!-- This file is auto-generated every hour. ~200 tokens to read. -->
<!-- Last update: 2026-04-14T19:00:00Z -->

## Stage: MVP / Pre-Launch
- Platform: Imperal Cloud (SDK 1.5.1)
- Model: MCP bridge (account credits, no API credits yet)
- Users: Internal team only (no public pricing)
- Deploy: git push → Imperal auto-pulls

## Active Extensions
| Extension | Repo | Status |
|-----------|------|--------|
| Imperal Video Creator | github.com/Sank0k69/imperal-video-creator | v2.0.0, public, standalone web UI works |
| Imperal Designer | github.com/Sank0k69/imperal-designer | v1.0.0, public, Figma connected |

## Infrastructure
- VPS: 23.106.73.57 (Debian 12, 16GB)
- Prod: agent.lexa-lox.xyz:3777 (old server.js)
- Staging: agent.lexa-lox.xyz/staging/ (v3.1, modular)
- Chrome CDP: port 9222
- Video Creator: localhost:8910

## HeyGen
- API key: working (read-only, 0 API credits)
- MCP bridge: working (account credits via OAuth)
- Video Agent: generates via account, ~3-5 min per video
- Concurrency: 1 (MCP limitation)

## Figma
- Token: Denchik's (figd_4BSb...), file_content:read scope
- WHM file: RnzTojZLJjuDRSa9Vpj5fm (23 assets exported)
- MCP: not connected (OAuth needed for own files)

## Today's Done
- Web UI: modular (api/ + templates/)
- Task queue: SQLite + async workers
- Montage presets: 6 (TikTok/ADHD/Promo/YouTube/LinkedIn/Custom)
- Staging: message queue, chat history, task board, 11 UI fixes
- GitHub: Sank0k69, 2 public repos
- Training system: building on VPS

## Blockers
- HeyGen API credits = 0 (MCP workaround active)
- Figma: own account token fails (using Denchik's)
- Staging → Prod push: pending QA
