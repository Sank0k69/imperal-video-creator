"""
Left Sidebar — navigation hub for Video Creator.
All actions use Send() (chat message) or Call() (direct function).
No Navigate() — Imperal panels are server-rendered, not SPA.
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Page, Section, Stack,
    Text, Stat, Stats, Badge, Divider,
    Button, Card, ListItem, List,
    Progress,
    Call, Send,
)


def register_sidebar(ext):
    """Register the left sidebar panel."""

    @ext.panel("sidebar", slot="left")
    async def sidebar_panel(ctx):
        videos = await ctx.store.get("video_production", "videos") or []
        ideas_bank = await ctx.store.get("ideation", "ideas_bank") or []
        scripts = await ctx.store.query("scripting_scripts", {})

        completed = [v for v in videos if v.get("status") == "completed"]
        processing = [v for v in videos if v.get("status") in ("processing", "pending")]
        drafts = [v for v in videos if v.get("status") == "draft"]

        queue_size = len(processing)

        return Page(
            title="Video Creator",
            children=[
                # ── Primary CTA ──
                Button(
                    label="New Video",
                    variant="primary",
                    icon="plus",
                    full_width=True,
                    on_click=Send(message="Create a new video for me"),
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
                                    on_click=Send(message="Show all my videos"),
                                ),
                                ListItem(
                                    id="lib-completed",
                                    title="Completed",
                                    icon="check-circle",
                                    meta=str(len(completed)),
                                    on_click=Send(message="Show completed videos"),
                                ),
                                ListItem(
                                    id="lib-processing",
                                    title="Processing",
                                    icon="loader",
                                    meta=str(len(processing)),
                                    on_click=Send(message="Show videos being processed"),
                                ),
                                ListItem(
                                    id="lib-drafts",
                                    title="Drafts",
                                    icon="file-text",
                                    meta=str(len(drafts)),
                                    on_click=Send(message="Show my draft videos"),
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
                                    on_click=Send(message="Help me write a video script"),
                                ),
                                ListItem(
                                    id="tool-hooks",
                                    title="Hook Builder",
                                    icon="anchor",
                                    on_click=Send(message="Generate hooks for my next video"),
                                ),
                                ListItem(
                                    id="tool-designer",
                                    title="Designer",
                                    icon="image",
                                    on_click=Send(message="Show brand assets from Figma"),
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
                        Stats(
                            children=[
                                Stat(label="Videos", value=str(len(completed)), icon="check-circle"),
                                Stat(label="Ideas", value=str(len(ideas_bank)), icon="lightbulb"),
                                Stat(label="Scripts", value=str(len(scripts)), icon="file-text"),
                            ],
                        ),
                    ],
                ),

                Divider(),

                # ── Settings ──
                Button(
                    label="Settings",
                    variant="secondary",
                    icon="settings",
                    full_width=True,
                    on_click=Send(message="Open Video Creator settings"),
                ),
            ],
        )

    return sidebar_panel
