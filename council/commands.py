"""
Council CLI Commands

Slash commands for the council mode:
- /council — Show council status
- /council add — Add a new member
- /council remove — Remove a member
- /council enable — Enable a member
- /council disable — Disable a member
- /council list — List all members
- /council mode — Change interaction mode
"""

from __future__ import annotations

from council.config import (
    CouncilConfig,
    CouncilMember,
    DEFAULT_MEMBERS,
    ensure_member_dirs,
    load_council_config,
    save_council_config,
)


def council_status() -> str:
    """Show council status."""
    config = load_council_config()

    if not config.enabled:
        return (
            "🎯 Council mode is disabled.\n"
            "Run `council setup` to configure your AI Council."
        )

    lines = [
        f"🎯 Poke Council — {config.mode.upper()} mode",
        f"   Stagger delay: {config.stagger_delay}s",
        f"   Members: {len(config.get_enabled_members())}/{len(config.members)} enabled",
        "",
    ]

    for member in config.members:
        status = "✅" if member.enabled else "❌"
        token_status = "🔗" if member.bot_token else "⚠️ no token"
        lines.append(f"  {status} {member.emoji} {member.name} ({member.id}) {token_status}")

    return "\n".join(lines)


def council_list() -> str:
    """List all council members."""
    config = load_council_config()

    if not config.members:
        return "No council members configured. Run `council setup` to get started."

    lines = ["🎯 Council Members:", ""]
    for i, member in enumerate(config.members, 1):
        status = "enabled" if member.enabled else "disabled"
        lines.append(f"  {i}. {member.emoji} {member.name} [{status}]")
        lines.append(f"     {member.bio}")
        lines.append("")

    return "\n".join(lines)


def council_add_member(
    name: str,
    emoji: str = "🤖",
    bio: str = "",
    personality: str = "",
    bot_token: str = "",
    template_id: str = "",
) -> str:
    """Add a new council member."""
    config = load_council_config()

    # Check if member already exists
    if config.get_member(name.lower().replace(" ", "_")):
        return f"❌ Member '{name}' already exists. Use `council remove` first."

    if template_id:
        template = None
        for t in DEFAULT_MEMBERS:
            if t.id == template_id:
                template = t
                break
        if template:
            member = CouncilMember(
                id=template.id,
                name=template.name,
                bot_token=bot_token,
                emoji=template.emoji,
                bio=template.bio,
                personality=template.personality,
                enabled=True,
            )
        else:
            return f"❌ Unknown template: {template_id}"
    else:
        member_id = name.lower().replace(" ", "_").replace("the_", "")
        member = CouncilMember(
            id=member_id,
            name=name,
            bot_token=bot_token,
            emoji=emoji,
            bio=bio,
            personality=personality or bio,
            enabled=True,
        )

    ensure_member_dirs(member)
    config.members.append(member)
    save_council_config(config)

    return f"✅ Added {member.emoji} {member.name} to the council!"


def council_remove_member(member_id: str) -> str:
    """Remove a council member."""
    config = load_council_config()

    member = config.get_member(member_id)
    if not member:
        return f"❌ Member '{member_id}' not found."

    config.members.remove(member)
    save_council_config(config)

    return f"✅ Removed {member.emoji} {member.name} from the council."


def council_toggle_member(member_id: str, enabled: bool) -> str:
    """Enable or disable a council member."""
    config = load_council_config()

    member = config.get_member(member_id)
    if not member:
        return f"❌ Member '{member_id}' not found."

    member.enabled = enabled
    save_council_config(config)

    status = "enabled" if enabled else "disabled"
    return f"{'✅' if enabled else '❌'} {member.emoji} {member.name} {status}."


def council_set_mode(mode: str) -> str:
    """Set the council interaction mode."""
    valid_modes = ["full", "pitch", "debate", "solo"]
    if mode not in valid_modes:
        return f"❌ Invalid mode. Choose from: {', '.join(valid_modes)}"

    config = load_council_config()
    config.mode = mode
    save_council_config(config)

    return f"✅ Council mode set to: {mode}"
