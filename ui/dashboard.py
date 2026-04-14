"""
Dashboard Panel -- main hub of Video Creator extension.
Three tabs: My Videos | Editor | Designer
Renders in the main slot of Imperal Cloud OS.
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Page, Section, Row, Column, Stack, Grid, Tabs,
    Header, Text, Stat, Stats, Badge, Divider,
    DataTable, DataColumn, Button, Card, Image, Icon,
    Form, Input, TextArea, Select, Slider, TagInput,
    Timeline, Progress, Alert, Markdown,
    SlideOver, Dialog, Chart, Empty,
    Call,
)


def register_dashboard(ext):
    """Register the dashboard panel on the extension."""

    @ext.panel("dashboard", slot="right")
    async def dashboard_panel(ctx):
        # ------- Load all data -------
        ideas_bank = await ctx.store.get("ideation", "ideas_bank") or []
        scripts = await ctx.store.query("scripting_scripts", {})
        metrics = await ctx.store.query("iteration_metrics", {})
        videos = await ctx.store.get("video_production", "videos") or []
        recent_activity = await ctx.store.get("activity", "recent") or []

        # Count video statuses
        completed = [v for v in videos if v.get("status") == "completed"]
        processing = [v for v in videos if v.get("status") in ("processing", "pending")]
        failed = [v for v in videos if v.get("status") == "failed"]

        # ------- Tab content builders -------
        videos_tab = _build_videos_tab(videos, completed, processing, failed, recent_activity)
        editor_tab = _build_editor_tab(ideas_bank, scripts)
        designer_tab = _build_designer_tab()

        return Page(
            title="Video Creator",
            children=[
                Tabs(tabs=[
                    {"label": "My Videos", "content": videos_tab},
                    {"label": "Editor", "content": editor_tab},
                    {"label": "Designer", "content": designer_tab},
                ]),
            ],
        )

    return dashboard_panel


# =====================================================
# TAB 1: MY VIDEOS
# =====================================================

def _build_videos_tab(videos, completed, processing, failed, recent_activity):
    """My Videos tab -- stats, table, activity."""

    # Stats row
    stats_row = Stats(children=[
        Stat(
            label="Total Videos",
            value=str(len(videos)),
            icon="film",
        ),
        Stat(
            label="Completed",
            value=str(len(completed)),
            icon="check-circle",
            trend="up" if len(completed) > 0 else "",
        ),
        Stat(
            label="Processing",
            value=str(len(processing)),
            icon="loader",
        ),
        Stat(
            label="Failed",
            value=str(len(failed)),
            icon="alert-triangle",
            trend="down" if len(failed) > 0 else "",
        ),
    ])

    # Video table data -- enrich for display
    table_rows = []
    for v in videos[:50]:
        status = v.get("status", "unknown")
        table_rows.append({
            "video_id": v.get("video_id", ""),
            "thumbnail": v.get("thumbnail_url", ""),
            "title": v.get("title", v.get("video_id", "Untitled")[:40]),
            "status": status,
            "duration": _format_duration(v.get("duration", 0)),
            "created": v.get("created_at", v.get("created", "")),
        })

    videos_table = DataTable(
        rows=table_rows,
        columns=[
            DataColumn(key="thumbnail", label="", width="80"),
            DataColumn(key="title", label="Title"),
            DataColumn(key="status", label="Status"),
            DataColumn(key="duration", label="Duration"),
            DataColumn(key="created", label="Created"),
        ],
    )

    # Performance chart (if we have metrics)
    performance_section = Section(
        title="Performance Overview",
        children=[
            Chart(
                type="line",
                data={
                    "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                    "datasets": [
                        {
                            "label": "Videos Created",
                            "data": [0, 0, 0, 0, 0, 0, 0],
                            "color": "#6c5ce7",
                        },
                    ],
                },
                height=200,
            ),
        ],
    )

    # Recent activity timeline
    activity_items = []
    for act in (recent_activity or [])[:8]:
        activity_items.append({
            "label": act.get("label", "Activity"),
            "description": act.get("description", ""),
            "status": act.get("status", "completed"),
            "time": act.get("time", ""),
        })
    if not activity_items:
        activity_items = [{"label": "No activity yet", "status": "pending"}]

    activity_section = Section(
        title="Recent Activity",
        children=[
            Timeline(items=activity_items),
        ],
    )

    return Stack(children=[
        stats_row,
        Divider(),
        Section(
            title="My Videos",
            children=[
                Row(children=[
                    Button(
                        label="New Video",
                        variant="primary",
                        icon="plus",
                        on_click=Call(function="create_video", params={"tier": 1}),
                    ),
                    Button(
                        label="Refresh",
                        variant="secondary",
                        icon="refresh-cw",
                        on_click=Call(function="list_avatars", params={"limit": 1}),
                    ),
                ]),
                videos_table,
            ],
        ),
        Divider(),
        Row(children=[
            Column(children=[performance_section]),
            Column(children=[activity_section]),
        ]),
    ])


# =====================================================
# TAB 2: EDITOR
# =====================================================

def _build_editor_tab(ideas_bank, scripts):
    """Editor tab -- create scripts, generate ideas, render videos."""

    # --- Brief + Topic input section ---
    input_section = Section(
        title="Create Content",
        children=[
            Form(
                action="editor_submit",
                submit_label="Submit",
                children=[
                    TextArea(
                        placeholder="What is this video about? Give context, key points, audience...",
                        param_name="brief",
                        rows=4,
                    ),
                    Row(children=[
                        Column(children=[
                            Input(
                                placeholder="e.g., Why NVMe hosting is 10x faster",
                                param_name="topic",
                            ),
                        ]),
                        Column(children=[
                            Select(
                                options=[
                                    {"value": "1", "label": "Tier 1 -- Simple (hook-body-CTA)"},
                                    {"value": "2", "label": "Tier 2 -- Advanced (setup-stress-payoff)"},
                                    {"value": "3", "label": "Tier 3 -- Pro (multi-act narrative)"},
                                ],
                                value="1",
                                param_name="tier",
                            ),
                        ]),
                    ]),
                    Row(children=[
                        Column(children=[
                            Select(
                                options=[
                                    {"value": "en", "label": "English"},
                                    {"value": "es", "label": "Spanish"},
                                    {"value": "ru", "label": "Russian"},
                                    {"value": "pt", "label": "Portuguese"},
                                    {"value": "de", "label": "German"},
                                    {"value": "fr", "label": "French"},
                                ],
                                value="en",
                                param_name="language",
                            ),
                        ]),
                        Column(children=[
                            Select(
                                options=[
                                    {"value": "viral", "label": "Viral"},
                                    {"value": "pitch", "label": "Pitch"},
                                    {"value": "false_statement", "label": "False Statement"},
                                ],
                                value="viral",
                                param_name="format_type",
                            ),
                        ]),
                        Column(children=[
                            Select(
                                options=[
                                    {"value": "short", "label": "Short (60s)"},
                                    {"value": "medium", "label": "Medium (3-5 min)"},
                                    {"value": "long", "label": "Long (10+ min)"},
                                ],
                                value="short",
                                param_name="duration",
                            ),
                        ]),
                    ]),
                ],
            ),
        ],
    )

    # --- Video format buttons ---
    format_section = Section(
        title="Aspect Ratio",
        children=[
            Row(children=[
                Button(label="9:16 Portrait", variant="secondary", icon="smartphone"),
                Button(label="16:9 Landscape", variant="secondary", icon="monitor"),
                Button(label="1:1 Square", variant="secondary", icon="square"),
            ]),
        ],
    )

    # --- Montage presets ---
    montage_section = Section(
        title="Montage Preset",
        children=[
            Grid(
                columns=3,
                gap=12,
                children=[
                    Card(
                        title="TikTok Viral",
                        content=Stack(children=[
                            Icon(name="zap", size=24),
                            Text(content="Fast cuts, trending hooks, vertical format"),
                        ]),
                    ),
                    Card(
                        title="ADHD",
                        content=Stack(children=[
                            Icon(name="activity", size=24),
                            Text(content="Rapid transitions, multi-layer engagement"),
                        ]),
                    ),
                    Card(
                        title="Promo",
                        content=Stack(children=[
                            Icon(name="megaphone", size=24),
                            Text(content="Product showcase, clean CTA"),
                        ]),
                    ),
                    Card(
                        title="YouTube Pro",
                        content=Stack(children=[
                            Icon(name="youtube", size=24),
                            Text(content="Professional pacing, retention-optimized"),
                        ]),
                    ),
                    Card(
                        title="LinkedIn",
                        content=Stack(children=[
                            Icon(name="briefcase", size=24),
                            Text(content="Thought leadership, B2B tone"),
                        ]),
                    ),
                    Card(
                        title="Custom",
                        content=Stack(children=[
                            Icon(name="settings", size=24),
                            Text(content="Your own style and pacing rules"),
                        ]),
                    ),
                ],
            ),
        ],
    )

    # --- Action buttons ---
    actions_section = Section(
        children=[
            Row(children=[
                Button(
                    label="Generate Ideas",
                    variant="secondary",
                    icon="lightbulb",
                    on_click=Call(function="generate_ideas", params={"count": 10, "method": "mixed"}),
                ),
                Button(
                    label="Generate Hooks",
                    variant="secondary",
                    icon="anchor",
                    on_click=Call(function="generate_hooks", params={"count": 5}),
                ),
                Button(
                    label="Write Script",
                    variant="primary",
                    icon="file-text",
                    on_click=Call(function="write_script", params={"tier": 1, "format_type": "viral"}),
                ),
                Button(
                    label="Full Pipeline",
                    variant="primary",
                    icon="play",
                    on_click=Call(function="create_video", params={"tier": 1}),
                ),
            ]),
        ],
    )

    # --- Script output area ---
    script_section = Section(
        title="Script Output",
        children=[
            Card(
                title="Script Preview",
                content=Stack(children=[
                    Markdown(content="_No script generated yet. Use the actions above to create one._"),
                ]),
            ),
            Divider(),
            Row(children=[
                Input(
                    placeholder="e.g., Make it more casual, add humor, shorten the intro...",
                    param_name="rewrite_prompt",
                ),
                Button(
                    label="Rewrite",
                    variant="secondary",
                    icon="refresh-cw",
                    on_click=Call(function="write_script", params={"tier": 1}),
                ),
            ]),
        ],
    )

    # --- Video generation ---
    video_section = Section(
        title="Video Generation",
        children=[
            Row(children=[
                Column(children=[
                    Select(
                        options=[
                            {"value": "portrait", "label": "Portrait (9:16)"},
                            {"value": "landscape", "label": "Landscape (16:9)"},
                            {"value": "square", "label": "Square (1:1)"},
                        ],
                        value="portrait",
                        param_name="dimension",
                        placeholder="Video Dimension",
                    ),
                ]),
                Column(children=[
                    Select(
                        options=[
                            {"value": "en", "label": "English"},
                            {"value": "es", "label": "Spanish"},
                            {"value": "ru", "label": "Russian"},
                        ],
                        value="en",
                        param_name="voice_language",
                        placeholder="Voice Language",
                    ),
                ]),
            ]),
            Row(children=[
                Button(
                    label="Generate Video",
                    variant="primary",
                    icon="video",
                    on_click=Call(function="create_video_heygen", params={"dimension": "portrait"}),
                ),
                Button(
                    label="List Avatars",
                    variant="secondary",
                    icon="users",
                    on_click=Call(function="list_avatars", params={"limit": 20}),
                ),
                Button(
                    label="List Voices",
                    variant="secondary",
                    icon="mic",
                    on_click=Call(function="list_voices", params={"language": "en"}),
                ),
            ]),
            Progress(
                value=0,
                label="Waiting for generation...",
                variant="bar",
            ),
        ],
    )

    # --- Ideas bank preview ---
    ideas_section = Section(
        title=f"Ideas Bank ({len(ideas_bank)})",
        children=[
            DataTable(
                rows=ideas_bank[:10],
                columns=[
                    DataColumn(key="title", label="Idea"),
                    DataColumn(key="classification", label="Zone"),
                    DataColumn(key="hook_potential", label="Hook Type"),
                ],
            ),
        ],
    )

    return Stack(children=[
        input_section,
        format_section,
        montage_section,
        Divider(),
        actions_section,
        script_section,
        Divider(),
        video_section,
        Divider(),
        ideas_section,
    ])


# =====================================================
# TAB 3: DESIGNER
# =====================================================

def _build_designer_tab():
    """Designer tab -- Figma components, exported assets."""

    search_section = Section(
        title="Figma Components",
        children=[
            Row(children=[
                Input(
                    placeholder="Paste your Figma file key...",
                    param_name="figma_file_key",
                ),
                Input(
                    placeholder="e.g., thumbnail, avatar, CTA button...",
                    param_name="figma_search",
                ),
            ]),
            Button(
                label="Search Components",
                variant="primary",
                icon="search",
                on_click=Call(function="list_avatars", params={"limit": 1}),
            ),
        ],
    )

    # Component grid placeholder
    components_section = Section(
        title="Components",
        children=[
            Grid(
                columns=4,
                gap=16,
                children=[
                    Card(
                        title="No components loaded",
                        content=Stack(children=[
                            Icon(name="image", size=48),
                            Text(content="Enter a Figma file key and search to load components"),
                        ]),
                    ),
                ],
            ),
        ],
    )

    # Exported assets
    assets_section = Section(
        title="Exported Assets",
        children=[
            Grid(
                columns=4,
                gap=16,
                children=[
                    Card(
                        title="No exports yet",
                        content=Stack(children=[
                            Icon(name="download", size=48),
                            Text(content="Export Figma components to see them here"),
                        ]),
                    ),
                ],
            ),
        ],
    )

    # Brand assets from local folder
    brand_assets_section = Section(
        title="Brand Assets",
        children=[
            Grid(
                columns=4,
                gap=16,
                children=[
                    Card(
                        title="Assets Folder",
                        content=Stack(children=[
                            Icon(name="folder", size=24),
                            Text(content="Brand logos, thumbnails, and media files"),
                        ]),
                    ),
                ],
            ),
        ],
    )

    return Stack(children=[
        search_section,
        Divider(),
        components_section,
        Divider(),
        assets_section,
        Divider(),
        brand_assets_section,
    ])


# =====================================================
# HELPERS
# =====================================================

def _format_duration(seconds) -> str:
    """Format seconds into human-readable duration."""
    if not seconds:
        return "--"
    try:
        seconds = int(float(seconds))
    except (ValueError, TypeError):
        return "--"
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"
