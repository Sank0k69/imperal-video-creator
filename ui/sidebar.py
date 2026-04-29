"""
Left Sidebar — navigation hub for Video Creator.
All actions use Call() (direct function call) or Open() (new tab).
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Page, Section, Stack,
    Text, Stat, Stats, Badge, Divider,
    Form, ListItem, List,
    Progress,
    Call, Open,
)


def register_sidebar(ext):
    """Register the left sidebar panel."""

    @ext.panel("sidebar", slot="left", title="Video Creator", icon="film")
    async def sidebar_panel(ctx):
        try:
            videos = await ctx.store.get("video_production", "videos") or []
        except Exception:
            videos = []
        try:
            ideas_bank = await ctx.store.get("ideation", "ideas_bank") or []
        except Exception:
            ideas_bank = []
        try:
            scripts = await ctx.store.get("scripting", "scripts") or []
        except Exception:
            scripts = []

        completed = [v for v in videos if v.get("status") == "completed"]
        processing = [v for v in videos if v.get("status") in ("processing", "pending")]
        drafts = [v for v in videos if v.get("status") == "draft"]
        queue_size = len(processing)

        return Page(
            title="Video Creator",
            children=[
                # ── Primary CTA ──
                Form(
                    action="write_script",
                    submit_label="New Video",
                    children=[],
                    defaults={"topic": "", "tier": 1},
                ),

                Divider(),

                # ── LIBRARY ──
                Section(
                    title="Library",
                    collapsible=True,
                    children=[
                        List(
                            items=[
                                ListItem(
                                    id="lib-all",
                                    title="All Videos",
                                    icon="film",
                                    meta=str(len(videos)),
                                    on_click=Call(function="video_status", video_id="all"),
                                ),
                                ListItem(
                                    id="lib-completed",
                                    title="Completed",
                                    icon="check-circle",
                                    meta=str(len(completed)),
                                    on_click=Call(function="video_status", video_id="completed"),
                                ),
                                ListItem(
                                    id="lib-processing",
                                    title="Processing",
                                    icon="loader",
                                    meta=str(len(processing)),
                                    on_click=Call(function="video_status", video_id="processing"),
                                ),
                                ListItem(
                                    id="lib-drafts",
                                    title="Drafts",
                                    icon="file-text",
                                    meta=str(len(drafts)),
                                    on_click=Call(function="video_status", video_id="drafts"),
                                ),
                            ],
                        ),
                    ],
                ),

                # ── TOOLS ──
                Section(
                    title="Tools",
                    collapsible=True,
                    children=[
                        List(
                            items=[
                                ListItem(
                                    id="tool-ideas",
                                    title="Idea Generator",
                                    icon="lightbulb",
                                    on_click=Call(function="generate_ideas", count=5, method="mixed"),
                                ),
                                ListItem(
                                    id="tool-scripts",
                                    title="Script Writer",
                                    icon="file-text",
                                    on_click=Call(function="write_script", topic="", tier=1),
                                ),
                                ListItem(
                                    id="tool-hooks",
                                    title="Hook Builder",
                                    icon="anchor",
                                    on_click=Call(function="generate_hooks", topic="", count=5),
                                ),
                                ListItem(
                                    id="tool-avatars",
                                    title="Avatars",
                                    icon="user",
                                    on_click=Call(function="list_avatars", limit=20),
                                ),
                            ],
                        ),
                    ],
                ),

                Divider(),

                # ── QUEUE STATUS ──
                *(
                    [
                        Section(
                            title="Queue",
                            children=[
                                Progress(
                                    value=50,
                                    label=f"{queue_size} video{'s' if queue_size != 1 else ''} generating",
                                    variant="bar",
                                ),
                            ],
                        ),
                        Divider(),
                    ]
                    if queue_size > 0 else []
                ),

                # ── QUICK STATS ──
                Section(
                    title="Stats",
                    collapsible=True,
                    children=[
                        Stats(children=[
                            Stat(label="Videos", value=str(len(completed)), icon="check-circle"),
                            Stat(label="Ideas", value=str(len(ideas_bank)), icon="lightbulb"),
                            Stat(label="Scripts", value=str(len(scripts)), icon="file-text"),
                        ]),
                    ],
                ),
            ],
        )

    return sidebar_panel
