"""
Settings Panel — user configuration, credentials, module toggles.
Users can: set niche, add platform API keys, toggle modules, configure quality gates.
"""
from __future__ import annotations
from imperal_sdk.ui import (
    Page, Section, Row, Column, Stack,
    Header, Text, Divider, Alert,
    Form, Input, TextArea, Toggle, Select, TagInput, FileUpload,
    Button,
    Call,
)


def register_settings(ext):
    """Register the settings panel on the extension."""

    @ext.panel("settings", slot="left")
    async def settings_panel(ctx):
        config = ctx.config

        return Page(
            title="Video Creator Settings",
            children=[
                # --- Profile ---
                Section(
                    title="Your Profile",
                    description="Tell us about your content niche and audience",
                    children=[
                        Form(
                            id="profile_form",
                            on_submit=Call(function="_save_profile"),
                            children=[
                                Input(
                                    name="niche",
                                    label="Your Niche",
                                    placeholder="e.g., Web hosting, SaaS, fitness coaching",
                                    value=config.get("niche", ""),
                                ),
                                TextArea(
                                    name="target_audience",
                                    label="Target Audience",
                                    placeholder="Describe your ideal viewer...",
                                    value=config.get("target_audience", ""),
                                ),
                                TagInput(
                                    name="brand_voice",
                                    label="Brand Voice Keywords",
                                    placeholder="Add keywords...",
                                    value=config.get("brand_voice", []),
                                ),
                                Select(
                                    name="language",
                                    label="Content Language",
                                    options=[
                                        {"value": "en", "label": "English"},
                                        {"value": "es", "label": "Spanish"},
                                        {"value": "ru", "label": "Russian"},
                                        {"value": "pt", "label": "Portuguese"},
                                        {"value": "de", "label": "German"},
                                        {"value": "fr", "label": "French"},
                                    ],
                                    value=config.get("language", "en"),
                                ),
                                Button(label="Save Profile", type="submit", variant="primary"),
                            ],
                        ),
                    ],
                ),

                Divider(),

                # --- Platform Credentials ---
                Section(
                    title="Platform Connections",
                    description="Add API keys for your social media platforms",
                    children=[
                        _platform_form("youtube", "YouTube", config),
                        _platform_form("tiktok", "TikTok", config),
                        _platform_form("instagram", "Instagram", config),
                        _platform_form("linkedin", "LinkedIn", config),
                        Divider(),
                        Alert(
                            type="info",
                            message="API keys are stored securely in your personal token wallet. Never shared with other users or extensions.",
                        ),
                        Text(text="Or upload a credentials file:"),
                        FileUpload(
                            name="credentials_file",
                            label="Upload credentials JSON",
                            accept=".json",
                            on_upload=Call(function="_import_credentials"),
                        ),
                    ],
                ),

                Divider(),

                # --- Content Settings ---
                Section(
                    title="Content Settings",
                    children=[
                        Form(
                            id="content_form",
                            on_submit=Call(function="_save_content_settings"),
                            children=[
                                Input(
                                    name="default_post_time",
                                    label="Default Post Time",
                                    placeholder="20:00",
                                    value=config.get("content", {}).get("default_post_time", "20:00"),
                                ),
                                Select(
                                    name="caption_style",
                                    label="Default Caption Style",
                                    options=[
                                        {"value": "curiosity", "label": "Curiosity Loops"},
                                        {"value": "pcm", "label": "PCM Targeted"},
                                        {"value": "mixed", "label": "Mixed"},
                                    ],
                                    value=config.get("content", {}).get("caption_style", "curiosity"),
                                ),
                                Button(label="Save Content Settings", type="submit", variant="primary"),
                            ],
                        ),
                    ],
                ),

                Divider(),

                # --- Quality Gates ---
                Section(
                    title="Quality Gates",
                    children=[
                        Form(
                            id="quality_form",
                            on_submit=Call(function="_save_quality_settings"),
                            children=[
                                Select(
                                    name="pcm_min_types",
                                    label="Minimum PCM Types per Script",
                                    options=[
                                        {"value": "2", "label": "2 (lenient)"},
                                        {"value": "3", "label": "3 (recommended)"},
                                        {"value": "4", "label": "4 (strict)"},
                                        {"value": "5", "label": "5 (very strict)"},
                                    ],
                                    value=str(config.get("quality", {}).get("pcm_min_types", 3)),
                                ),
                                Input(
                                    name="title_max_chars",
                                    label="Max Title Length",
                                    value=str(config.get("quality", {}).get("title_max_chars", 55)),
                                ),
                                Button(label="Save Quality Gates", type="submit", variant="primary"),
                            ],
                        ),
                    ],
                ),

                Divider(),

                # --- Module Toggles ---
                Section(
                    title="Module Toggles",
                    description="Enable/disable individual modules",
                    children=[
                        _module_toggles(config),
                    ],
                ),
            ],
        )

    return settings_panel


def _platform_form(platform_id: str, platform_name: str, config: dict):
    """Build a platform credentials form."""
    platforms = config.get("platforms", {})
    platform_cfg = platforms.get(platform_id, {})
    return Row(children=[
        Toggle(
            name=f"platform_{platform_id}_enabled",
            label=platform_name,
            value=platform_cfg.get("enabled", False),
        ),
        Input(
            name=f"platform_{platform_id}_api_key",
            label=f"{platform_name} API Key",
            placeholder="Enter API key...",
            value=platform_cfg.get("api_key", ""),
            type="password",
        ),
    ])


def _module_toggles(config: dict):
    """Build module toggle switches."""
    modules_cfg = config.get("modules", {})
    toggles = []
    for name in ["ideation", "framing", "packaging", "hooks", "scripting",
                  "pcm", "captions", "cta", "publishing", "iteration"]:
        toggles.append(
            Toggle(
                name=f"module_{name}",
                label=name.capitalize(),
                value=modules_cfg.get(name, True),
            )
        )
    return Stack(children=toggles)
