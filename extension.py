"""
Video Creator — Imperal Cloud Extension
========================================
AI-powered video content creation agent based on Creator Monetize methodology.

Architecture:
- 10 independent modules (microservices pattern)
- Modules don't know about each other
- Pipelines orchestrate modules for complex workflows
- Knowledge stored as JSON data, not hardcoded
- Every module is toggleable per-user
"""
from __future__ import annotations

from imperal_sdk import ChatExtension, Extension
from imperal_sdk.types import ActionResult

from config.defaults import DEFAULTS
from modules import ALL_MODULES
from pipelines import PipelineRegistry

# --- Extension setup ---

ext = Extension(
    name="video-creator",
    version="2.0.0",
    description="AI video content creation powered by Creator Monetize methodology",
)

chat = ChatExtension(ext)


# --- Module registry ---

_modules: dict = {}
_pipelines: PipelineRegistry | None = None


def _get_module(ctx, name: str):
    """Get or create a module instance. Lazy initialization."""
    if name not in _modules:
        if name not in ALL_MODULES:
            return None
        _modules[name] = ALL_MODULES[name](ctx)
    return _modules[name]


def _get_pipelines(ctx) -> PipelineRegistry:
    global _pipelines
    if _pipelines is None:
        _pipelines = PipelineRegistry(ctx, _get_module)
    return _pipelines


# --- Lifecycle ---

@ext.on_install
async def on_install(ctx):
    """Initialize default config on first install."""
    for key, value in DEFAULTS.items():
        existing = ctx.config.get(key)
        if existing is None:
            await ctx.config.set(key, value)
    return ActionResult.success(summary="Video Creator installed. Configure your niche and platforms in Settings.")


@ext.on_upgrade("1.0.0")
async def on_upgrade_1_0(ctx):
    """Migration for v1.0.0."""
    return ActionResult.success(summary="Upgraded to v1.0.0")


@ext.health_check
async def health(ctx):
    """Health check — verify modules and knowledge base."""
    enabled = [name for name, cls in ALL_MODULES.items() if _get_module(ctx, name).is_enabled()]
    return ActionResult.success(data={
        "version": "2.0.0",
        "modules_enabled": enabled,
        "modules_total": len(ALL_MODULES),
    })


# =====================================================
# CHAT FUNCTIONS — one per module capability
# =====================================================

# --- Ideation ---

@chat.function("generate_ideas", action_type="read")
async def generate_ideas(ctx, topic: str = "", count: int = 10, method: str = "mixed") -> ActionResult:
    """
    Generate video content ideas using Perfect Idea Zone methodology.

    Args:
        topic: Starting topic or niche area (optional, uses configured niche)
        count: Number of ideas to generate (default 10)
        method: Ideation method — 'commence', 'snatch_twirl', 'audience', 'mixed'
    """
    mod = _get_module(ctx, "ideation")
    result = await mod.execute("generate", {"topic": topic, "count": count, "method": method})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("classify_idea", action_type="read")
async def classify_idea(ctx, idea: str) -> ActionResult:
    """Classify an idea as 'perfect' or 'sub-optimal' using the Perfect Idea Zone framework."""
    mod = _get_module(ctx, "ideation")
    result = await mod.execute("classify", {"idea": idea})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Framing ---

@chat.function("frame_video", action_type="read")
async def frame_video(ctx, idea: str, avatar: str = "") -> ActionResult:
    """
    Transform a raw idea into a directed video concept using 4-step framing.
    Steps: Video Framing → Packaging Framing → Directional Framing → Grand Payoff.
    """
    mod = _get_module(ctx, "framing")
    result = await mod.execute("frame", {"idea": idea, "avatar": avatar})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Packaging ---

@chat.function("package_video", action_type="read")
async def package_video(ctx, concept: str, style: str = "niched") -> ActionResult:
    """
    Create title + thumbnail strategy using Want vs Need framework.

    Args:
        concept: The framed video concept
        style: 'niched' (search-optimized) or 'shareability' (trend-riding)
    """
    mod = _get_module(ctx, "packaging")
    result = await mod.execute("package", {"concept": concept, "style": style})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Hooks ---

@chat.function("generate_hooks", action_type="read")
async def generate_hooks(ctx, topic: str, hook_types: list[str] | None = None, count: int = 5) -> ActionResult:
    """
    Generate video hooks from 7 psychological trigger types.
    Types: desirable, social_proof, controversial, secret, negative, quick_solution, lesson.
    """
    mod = _get_module(ctx, "hooks")
    result = await mod.execute("generate", {"topic": topic, "types": hook_types, "count": count})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Scripting ---

@chat.function("write_script", action_type="write", event="script.created")
async def write_script(ctx, topic: str, hook: str = "", tier: int = 1,
                       format_type: str = "viral", duration: str = "short") -> ActionResult:
    """
    Write a complete video script using Hook-Body-CTA architecture.

    Args:
        topic: What the video is about
        hook: Pre-written hook (optional, generates one if empty)
        tier: Script complexity — 1 (simple) or 2 (setup/stress/payoff)
        format_type: 'viral', 'pitch', or 'false_statement'
        duration: 'short' (60s), 'medium' (3-5min), 'long' (10+min)
    """
    mod = _get_module(ctx, "scripting")
    result = await mod.execute("write", {
        "topic": topic, "hook": hook, "tier": tier,
        "format_type": format_type, "duration": duration,
    })
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- PCM Analysis ---

@chat.function("analyze_pcm", action_type="read")
async def analyze_pcm(ctx, script: str) -> ActionResult:
    """Analyze a script for PCM personality type coverage (6 types). Returns coverage score and suggestions."""
    mod = _get_module(ctx, "pcm")
    result = await mod.execute("analyze", {"script": script})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("enhance_pcm", action_type="read")
async def enhance_pcm(ctx, script: str, target_types: list[str] | None = None) -> ActionResult:
    """Rewrite a script to cover missing PCM personality types."""
    mod = _get_module(ctx, "pcm")
    result = await mod.execute("enhance", {"script": script, "target_types": target_types})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Captions ---

@chat.function("generate_captions", action_type="read")
async def generate_captions(ctx, topic: str, style: str = "curiosity", count: int = 5) -> ActionResult:
    """
    Generate post captions.
    Styles: 'curiosity' (curiosity loops), 'pcm' (personality-targeted), 'mixed'.
    """
    mod = _get_module(ctx, "captions")
    result = await mod.execute("generate", {"topic": topic, "style": style, "count": count})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- CTA ---

@chat.function("generate_cta", action_type="read")
async def generate_cta(ctx, context: str, goal: str = "engage", platform: str = "youtube") -> ActionResult:
    """
    Generate call-to-action for video content.
    Goals: 'engage' (like/comment/sub), 'redirect' (to another video), 'link' (description link), 'manychat' (comment trigger).
    """
    mod = _get_module(ctx, "cta")
    result = await mod.execute("generate", {"context": context, "goal": goal, "platform": platform})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Publishing ---

@chat.function("pre_publish_check", action_type="read")
async def pre_publish_check(ctx, content: dict) -> ActionResult:
    """Run 6-step pre-publishing checklist on content before posting."""
    mod = _get_module(ctx, "publishing")
    result = await mod.execute("check", {"content": content})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Iteration ---

@chat.function("track_performance", action_type="write", event="content.tracked")
async def track_performance(ctx, content_id: str, metrics: dict) -> ActionResult:
    """Record performance metrics for published content (views, retention, CTR, etc.)."""
    mod = _get_module(ctx, "iteration")
    result = await mod.execute("track", {"content_id": content_id, "metrics": metrics})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("analyze_performance", action_type="read")
async def analyze_performance(ctx, content_id: str = "", period: str = "week") -> ActionResult:
    """Analyze content performance and suggest iterations."""
    mod = _get_module(ctx, "iteration")
    result = await mod.execute("analyze", {"content_id": content_id, "period": period})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# =====================================================
# PIPELINES — complex multi-module workflows
# =====================================================

@chat.function("create_video", action_type="write", event="video.created")
async def create_video(ctx, topic: str, tier: int = 1, format_type: str = "viral") -> ActionResult:
    """
    Full video creation pipeline: Ideation → Framing → Packaging → Hooks → Script → PCM → Captions → CTA → Checklist.
    """
    registry = _get_pipelines(ctx)
    pipeline = registry.get("full_video")
    result = await pipeline.run({"topic": topic, "tier": tier, "format_type": format_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("quick_script", action_type="write", event="script.created")
async def quick_script(ctx, topic: str, format_type: str = "viral") -> ActionResult:
    """Quick pipeline: Topic → Hook → Script → CTA. Skip framing/packaging for speed."""
    registry = _get_pipelines(ctx)
    pipeline = registry.get("quick_script")
    result = await pipeline.run({"topic": topic, "format_type": format_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("batch_content", action_type="write", event="batch.created")
async def batch_content(ctx, topics: list[str], format_type: str = "viral") -> ActionResult:
    """Batch create scripts for multiple topics at once."""
    registry = _get_pipelines(ctx)
    pipeline = registry.get("batch_content")
    result = await pipeline.run({"topics": topics, "format_type": format_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# =====================================================
# NEW MODULES — Market Research, Funnels, Email, Sales, Launch
# =====================================================

# --- Market Research ---

@chat.function("gsb_analyze", action_type="read")
async def gsb_analyze(ctx, niche: str = "", platform: str = "youtube") -> ActionResult:
    """Run Gold Silver Bronze competitive content analysis for your niche."""
    mod = _get_module(ctx, "market_research")
    result = await mod.execute("gsb_analyze", {"niche": niche, "platform": platform})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("build_avatar", action_type="write", event="avatar.created")
async def build_avatar(ctx, niche: str = "", product: str = "") -> ActionResult:
    """Build a detailed client avatar using 18-question framework."""
    mod = _get_module(ctx, "market_research")
    result = await mod.execute("build_avatar", {"niche": niche, "product": product})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("classify_trajectory", action_type="read")
async def classify_trajectory(ctx, followers_count: int = 0, platform: str = "youtube", has_offer: bool = False, niche_type: str = "high") -> ActionResult:
    """Classify creator into 1 of 8 pathways and get 28-day roadmap."""
    mod = _get_module(ctx, "market_research")
    result = await mod.execute("classify_trajectory", {"followers_count": followers_count, "platform": platform, "has_offer": has_offer, "niche_type": niche_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

# --- Funnel Copy ---

@chat.function("write_vsl", action_type="write", event="vsl.created")
async def write_vsl(ctx, funnel_type: str = "call", offer: str = "", audience: str = "", tone: str = "casual but confident") -> ActionResult:
    """Write a complete VSL script following the 8-section structure."""
    mod = _get_module(ctx, "funnel_copy")
    result = await mod.execute("write_vsl", {"funnel_type": funnel_type, "offer": offer, "audience": audience, "tone": tone})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("page_copy", action_type="write", event="page.created")
async def page_copy(ctx, page_type: str = "opt_in", offer: str = "", headline: str = "") -> ActionResult:
    """Generate funnel page copy (opt-in, booking, sales, post-booking)."""
    mod = _get_module(ctx, "funnel_copy")
    result = await mod.execute("page_copy", {"page_type": page_type, "offer": offer, "headline": headline})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("presentation_outline", action_type="write", event="presentation.created")
async def presentation_outline(ctx, topic: str = "", offer: str = "") -> ActionResult:
    """Generate webinar presentation outline using 26-step structure."""
    mod = _get_module(ctx, "funnel_copy")
    result = await mod.execute("presentation_outline", {"topic": topic, "offer": offer})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

# --- Email Sequences ---

@chat.function("promo_sequence", action_type="write", event="email.created")
async def promo_sequence(ctx, product_name: str = "", offer: str = "", deadline: str = "") -> ActionResult:
    """Generate 6-email promotional sequence with urgency cascade."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("promo_sequence", {"product_name": product_name, "offer": offer, "deadline": deadline})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("nurture_sequence", action_type="write", event="email.created")
async def nurture_sequence(ctx, product: str = "", dream_outcome: str = "") -> ActionResult:
    """Generate 6-email nurture sequence for value video funnel."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("nurture_sequence", {"product": product, "dream_outcome": dream_outcome})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("webinar_sequence", action_type="write", event="email.created")
async def webinar_sequence(ctx, webinar_title: str = "", date: str = "", link: str = "", channels: list[str] | None = None) -> ActionResult:
    """Generate webinar reminder sequence (email + telegram + sms)."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("webinar_sequence", {"webinar_title": webinar_title, "date": date, "link": link, "channels": channels or ["email"]})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("reactivate_list", action_type="write", event="email.created")
async def reactivate_list(ctx, brand: str = "", niche: str = "", time_away: str = "") -> ActionResult:
    """Generate email list reactivation email for dormant subscribers."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("reactivation", {"brand": brand, "niche": niche, "time_away": time_away})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

# --- Sales ---

@chat.function("sales_script", action_type="write", event="script.created")
async def sales_script(ctx, product: str = "", price: str = "", niche: str = "") -> ActionResult:
    """Generate customized 12-stage sales call script."""
    mod = _get_module(ctx, "sales")
    result = await mod.execute("sales_script", {"product": product, "price": price, "niche": niche})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("handle_objection", action_type="read")
async def handle_objection(ctx, objection: str = "", context: str = "") -> ActionResult:
    """Handle a sales objection using DECPC formula."""
    mod = _get_module(ctx, "sales")
    result = await mod.execute("handle_objection", {"objection": objection, "context": context})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("create_offer", action_type="write", event="offer.created")
async def create_offer(ctx, dream_outcome: str = "", target_audience: str = "", product_type: str = "course") -> ActionResult:
    """Build complete offer using 8-step Elixir Genesis methodology."""
    mod = _get_module(ctx, "sales")
    result = await mod.execute("create_offer", {"dream_outcome": dream_outcome, "target_audience": target_audience, "product_type": product_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

# --- Launch ---

@chat.function("pre_launch_plan", action_type="write", event="launch.planned")
async def pre_launch_plan(ctx, product: str = "", launch_date: str = "", launch_type: str = "loud") -> ActionResult:
    """Generate pre-launch plan with timeline, tasks, and discount strategy."""
    mod = _get_module(ctx, "launch")
    result = await mod.execute("pre_launch_plan", {"product": product, "launch_date": launch_date, "launch_type": launch_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("launch_roadmap", action_type="write", event="launch.planned")
async def launch_roadmap(ctx, pathway_number: int = 1, niche: str = "", product: str = "") -> ActionResult:
    """Generate full 28-day launch roadmap based on trajectory pathway."""
    mod = _get_module(ctx, "launch")
    result = await mod.execute("launch_28_day", {"pathway_number": pathway_number, "niche": niche, "product": product})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# =====================================================
# EXPOSED API — for Daria and other extensions (IPC)
# =====================================================

@ext.expose("generate_ideas")
async def api_generate_ideas(ctx, topic: str = "", count: int = 5) -> ActionResult:
    """IPC: Generate video ideas. Callable by Daria and other extensions."""
    mod = _get_module(ctx, "ideation")
    result = await mod.execute("generate", {"topic": topic, "count": count, "method": "mixed"})
    return ActionResult.success(data=result["data"])


@ext.expose("write_script")
async def api_write_script(ctx, topic: str, tier: int = 1, format_type: str = "viral") -> ActionResult:
    """IPC: Write a video script. Callable by Daria and other extensions."""
    mod = _get_module(ctx, "scripting")
    result = await mod.execute("write", {
        "topic": topic, "tier": tier, "format_type": format_type, "duration": "short",
    })
    return ActionResult.success(data=result["data"])


@ext.expose("full_pipeline")
async def api_full_pipeline(ctx, topic: str, tier: int = 1) -> ActionResult:
    """IPC: Run full video creation pipeline. Callable by Daria."""
    registry = _get_pipelines(ctx)
    pipeline = registry.get("full_video")
    result = await pipeline.run({"topic": topic, "tier": tier, "format_type": "viral"})
    return ActionResult.success(data=result["data"])


# --- New IPC Methods ---

@ext.expose("write_vsl")
async def api_write_vsl(ctx, funnel_type: str = "call", offer: str = "", audience: str = "") -> ActionResult:
    """IPC: Write a VSL script. Callable by other extensions."""
    mod = _get_module(ctx, "funnel_copy")
    result = await mod.execute("write_vsl", {"funnel_type": funnel_type, "offer": offer, "audience": audience, "tone": "casual but confident"})
    return ActionResult.success(data=result["data"])

@ext.expose("create_offer")
async def api_create_offer(ctx, dream_outcome: str = "", target_audience: str = "") -> ActionResult:
    """IPC: Create an offer using Elixir Genesis. Callable by other extensions."""
    mod = _get_module(ctx, "sales")
    result = await mod.execute("create_offer", {"dream_outcome": dream_outcome, "target_audience": target_audience, "product_type": "course"})
    return ActionResult.success(data=result["data"])

@ext.expose("promo_sequence")
async def api_promo_sequence(ctx, product_name: str = "", offer: str = "", deadline: str = "") -> ActionResult:
    """IPC: Generate promo email sequence. Callable by other extensions."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("promo_sequence", {"product_name": product_name, "offer": offer, "deadline": deadline})
    return ActionResult.success(data=result["data"])


# =====================================================
# SCHEDULED TASKS
# =====================================================

@ext.schedule("content_reminder", cron="0 9 * * *")
async def daily_content_reminder(ctx):
    """Daily reminder to create content. Checks pending ideas and suggests today's topic."""
    mod = _get_module(ctx, "ideation")
    ideas = await mod.load("ideas_bank", [])
    if ideas:
        top_idea = ideas[0]
        await ctx.notify.push(
            title="Time to create content",
            body=f"Top idea: {top_idea.get('title', 'Check your ideas bank')}",
        )
    return ActionResult.success(summary="Daily reminder sent")
