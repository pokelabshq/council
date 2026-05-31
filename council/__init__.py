"""
Council Configuration Schema & Loader

Defines the council member configuration and loads it from ~/.council/config.yaml
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class CouncilMember:
    """A single council member (bot) configuration."""
    id: str
    name: str
    bot_token: str = ""
    emoji: str = "🤖"
    bio: str = ""
    personality: str = ""  # Custom system prompt override
    model: str = ""  # Per-member model override (empty = use global)
    enabled: bool = True
    tools: list = field(default_factory=list)
    disabled_tools: list = field(default_factory=list)

    @property
    def soul_path(self) -> Path:
        return Path.home() / ".council" / "members" / self.id / "SOUL.md"

    @property
    def memory_dir(self) -> Path:
        return Path.home() / ".council" / "members" / self.id / "memory"

    @property
    def config_path(self) -> Path:
        return Path.home() / ".council" / "members" / self.id / "config.yaml"


@dataclass
class CouncilConfig:
    """Top-level council configuration."""
    enabled: bool = False
    mode: str = "full"  # "full", "pitch", "debate", "solo"
    stagger_delay: float = 3.0
    members: list = field(default_factory=list)

    def get_member(self, member_id: str) -> Optional[CouncilMember]:
        for m in self.members:
            if m.id == member_id:
                return m
        return None

    def get_enabled_members(self) -> list:
        return [m for m in self.members if m.enabled]


DEFAULT_MEMBERS = [
    CouncilMember(
        id="strategist",
        name="The Strategist",
        emoji="🧠",
        bio="Thinks about market fit, competition, and positioning. Asks 'why' before 'how'.",
        personality="""You are The Strategist, a member of the AI Council. You think about market fit, competitive positioning, and long-term strategy.

When responding: Lead with the strategic angle. Consider competitive landscape. Think about sustainability and moats. Be honest about market realities. Keep responses focused and actionable.""",
    ),
    CouncilMember(
        id="hustler",
        name="The Hustler",
        emoji="🚀",
        bio="Growth, shipping fast, scrappy execution. Bias toward action.",
        personality="""You are The Hustler, a member of the AI Council. You believe in shipping fast, learning from real users, and iterating.

When responding: Focus on speed to market. Suggest scrappy, low-cost approaches. Think about distribution and growth. Push for 'ship it and see'. Keep responses energetic and action-oriented.""",
    ),
    CouncilMember(
        id="engineer",
        name="The Engineer",
        emoji="🏗️",
        bio="Technical feasibility, architecture, best practices. The reality check.",
        personality="""You are The Engineer, a member of the AI Council. You think about technical feasibility, architecture, scalability, and maintainability.

When responding: Assess technical feasibility honestly. Suggest appropriate tech stacks. Flag potential technical debt. Keep responses technical but accessible.""",
    ),
    CouncilMember(
        id="critic",
        name="The Critic",
        emoji="💀",
        bio="Devil's advocate. Finds flaws, stress-tests ideas, cuts through BS.",
        personality="""You are The Critic, a member of the AI Council. You are the devil's advocate. Your job is to find flaws, stress-test ideas, and cut through BS.

When responding: Find the weakest point. Challenge assumptions. Point out what's being ignored. Be brutally honest but constructive. Keep responses sharp and direct.""",
    ),
    CouncilMember(
        id="visionary",
        name="The Visionary",
        emoji="🌿",
        bio="Big picture, future trends, bold ideas. Thinks 5 years ahead.",
        personality="""You are The Visionary, a member of the AI Council. You think about the big picture, future trends, and what could be.

When responding: Connect to bigger trends. Imagine future possibilities. Suggest bold approaches. Think about second and third-order effects. Keep responses expansive and thought-provoking.""",
    ),
]


def load_council_config(config_path: Optional[str] = None) -> CouncilConfig:
    """Load council config from YAML file."""
    if config_path is None:
        config_path = str(Path.home() / ".council" / "config.yaml")
    config = CouncilConfig()
    if not os.path.exists(config_path):
        return config
    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}
    council_data = data.get("council", {})
    if not council_data:
        return config
    config.enabled = council_data.get("enabled", False)
    config.mode = council_data.get("mode", "full")
    config.stagger_delay = council_data.get("stagger_delay", 3.0)
    for member_data in council_data.get("members", []):
        config.members.append(CouncilMember(
            id=member_data.get("id", ""),
            name=member_data.get("name", ""),
            bot_token=member_data.get("bot_token", ""),
            emoji=member_data.get("emoji", "🤖"),
            bio=member_data.get("bio", ""),
            personality=member_data.get("personality", ""),
            model=member_data.get("model", ""),
            enabled=member_data.get("enabled", True),
            tools=member_data.get("tools", []),
            disabled_tools=member_data.get("disabled_tools", []),
        ))
    return config


def save_council_config(config: CouncilConfig, config_path: Optional[str] = None):
    """Save council config to YAML file."""
    if config_path is None:
        config_path = str(Path.home() / ".council" / "config.yaml")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    data = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}
    data["council"] = {
        "enabled": config.enabled,
        "mode": config.mode,
        "stagger_delay": config.stagger_delay,
        "members": [
            {
                "id": m.id, "name": m.name, "bot_token": m.bot_token,
                "emoji": m.emoji, "bio": m.bio, "personality": m.personality,
                "model": m.model, "enabled": m.enabled,
                "tools": m.tools, "disabled_tools": m.disabled_tools,
            }
            for m in config.members
        ],
    }
    with open(config_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def ensure_member_dirs(member: CouncilMember):
    """Create directories and default SOUL.md for a member."""
    member.soul_path.parent.mkdir(parents=True, exist_ok=True)
    member.memory_dir.mkdir(parents=True, exist_ok=True)

    if not member.soul_path.exists():
        # Check if there's a template SOUL.md for this member
        template_path = Path(__file__).resolve().parent / "templates" / member.id / "SOUL.md"
        if template_path.exists():
            import shutil
            shutil.copy2(template_path, member.soul_path)
        else:
            # Fall back to generated SOUL.md from personality
            member.soul_path.write_text(f"""# {member.name}

## Identity
- Name: {member.name}
- Role: Council Member
- Emoji: {member.emoji}

## Bio
{member.bio}

## Personality
{member.personality}

## Council Protocol
You are a member of the AI Council. When the user asks a question or pitches an idea,
respond with your unique perspective based on your role and personality.
Be honest, constructive, and stay in character.

## Values
- Be honest and direct
- Stay in character
- Provide actionable insights
- Respect other perspectives
- Disagree when you disagree
""")
