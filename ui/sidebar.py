"""
Sidebar Widget -- compact status view for Video Creator.
Shows: active generations, queue size, recent activity, quick actions.
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Stack, Row, Column,
    Header, Text, Stat, Stats, Badge, Divider, Icon,
    Button, Card,
    Timeline, Progress,
    Call,
)


def register_sidebar(ext):
    """Register the sidebar widget on the extension."""

    @ext.widget("video_status")
    async def sidebar_widget(ctx):
        # Load data
        videos = await ctx.store.get("video_production", "videos") or []
        recent_activity = await ctx.store.get("activity", "recent") or []
        ideas_bank = await ctx.store.get("ideation", "ideas_bank") or []
        scripts = await ctx.store.query("scripting_scripts", {})

        # Calculate stats
        active = [v for v in videos if v.get("status") in ("processing", "pending")]
        queue_size = len(active)
        total_completed = len([v for v in videos if v.get("status") == "completed"])

        # Recent activity (last 5)
        activity_items = []
        for act in (recent_activity or [])[:5]:
            activity_items.append({
                "label": act.get("label", "Activity"),
                "description": act.get("description", ""),
                "status": act.get("status", "completed"),
                "time": act.get("time", ""),
            })
        if not activity_items:
            activity_items = [{"label": "No recent activity", "status": "pending"}]

        return Stack(children=[
            # Title
            Row(children=[
                Icon(name="video", size=18),
                Header(text="Video Creator", level=4),
            ]),

            Divider(),

            # Quick stats
            Stats(children=[
                Stat(
                    label="Active",
                    value=str(queue_size),
                    icon="loader",
                ),
                Stat(
                    label="Done",
                    value=str(total_completed),
                    icon="check-circle",
                ),
            ]),

            # Queue progress (if anything is processing)
            *(
                [Progress(
                    value=50,
                    label=f"{queue_size} video{'s' if queue_size != 1 else ''} generating...",
                    variant="bar",
                )]
                if queue_size > 0 else []
            ),

            Divider(),

            # Bank counts
            Row(children=[
                Card(
                    title=str(len(ideas_bank)),
                    content=Text(content="Ideas"),
                ),
                Card(
                    title=str(len(scripts)),
                    content=Text(content="Scripts"),
                ),
            ]),

            Divider(),

            # Recent activity
            Header(text="Recent", level=5),
            Timeline(items=activity_items),

            Divider(),

            # Quick actions
            Stack(children=[
                Button(
                    label="New Video",
                    variant="primary",
                    icon="plus",
                    on_click=Call(function="create_video", params={"tier": 1}),
                ),
                Button(
                    label="Generate Ideas",
                    variant="secondary",
                    icon="lightbulb",
                    on_click=Call(function="generate_ideas", params={"count": 10, "method": "mixed"}),
                ),
                Button(
                    label="Quick Script",
                    variant="secondary",
                    icon="zap",
                    on_click=Call(function="quick_script", params={"format_type": "viral"}),
                ),
            ]),
        ])

    return sidebar_widget
