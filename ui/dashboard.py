"""
Dashboard Panel — main overview of content pipeline status.
Shows: active scripts, ideas bank, performance stats, recent activity.
"""
from __future__ import annotations
from imperal_sdk.ui import (
    Page, Section, Row, Column, Stack,
    Header, Text, Stat, Stats, Badge, Divider,
    DataTable, DataColumn, Button, Card,
    Timeline, Progress, Alert,
    Call,
)


def register_dashboard(ext):
    """Register the dashboard panel on the extension."""

    @ext.panel("dashboard", slot="main")
    async def dashboard_panel(ctx):
        # Load data
        ideas_bank = await ctx.store.get("ideation/ideas_bank") or []
        scripts = await ctx.store.list("scripting/scripts/")
        metrics = await ctx.store.list("iteration/metrics/")

        return Page(
            title="Video Creator",
            children=[
                # --- Stats overview ---
                Section(
                    title="Overview",
                    children=[
                        Stats(children=[
                            Stat(label="Ideas in Bank", value=str(len(ideas_bank))),
                            Stat(label="Scripts Created", value=str(len(scripts))),
                            Stat(label="Content Tracked", value=str(len(metrics))),
                        ]),
                    ],
                ),

                Divider(),

                # --- Quick Actions ---
                Section(
                    title="Quick Actions",
                    children=[
                        Row(children=[
                            Button(
                                label="Generate Ideas",
                                variant="primary",
                                action=Call(function="generate_ideas", params={"count": 10}),
                            ),
                            Button(
                                label="Quick Script",
                                variant="secondary",
                                action=Call(function="quick_script", params={"format_type": "viral"}),
                            ),
                            Button(
                                label="Full Pipeline",
                                variant="secondary",
                                action=Call(function="create_video", params={"tier": 1}),
                            ),
                        ]),
                    ],
                ),

                Divider(),

                # --- Ideas Bank ---
                Section(
                    title="Ideas Bank",
                    children=[
                        DataTable(
                            data=ideas_bank[:10],
                            columns=[
                                DataColumn(key="title", label="Idea"),
                                DataColumn(key="classification", label="Status"),
                                DataColumn(key="hook_potential", label="Hook Type"),
                            ],
                            empty_message="No ideas yet. Generate some!",
                        ),
                    ],
                ),

                Divider(),

                # --- Recent Scripts ---
                Section(
                    title="Recent Scripts",
                    children=[
                        DataTable(
                            data=[{"id": s} for s in scripts[:10]],
                            columns=[
                                DataColumn(key="id", label="Script"),
                            ],
                            empty_message="No scripts yet.",
                        ),
                    ],
                ),

                # --- Module Status ---
                Section(
                    title="Modules",
                    children=[
                        _module_status_cards(ctx),
                    ],
                ),
            ],
        )

    return dashboard_panel


def _module_status_cards(ctx):
    """Build module status cards."""
    modules_cfg = ctx.config.get("modules", {})
    cards = []
    for name in ["ideation", "framing", "packaging", "hooks", "scripting",
                  "pcm", "captions", "cta", "publishing", "iteration"]:
        enabled = modules_cfg.get(name, True)
        cards.append(
            Card(
                title=name.capitalize(),
                children=[
                    Badge(
                        text="Active" if enabled else "Disabled",
                        color="green" if enabled else "gray",
                    ),
                ],
            )
        )
    return Row(children=cards)
