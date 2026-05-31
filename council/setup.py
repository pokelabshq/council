"""
Council Setup Wizard

Interactive setup for configuring council members and their Telegram bots.
Run with: council setup
"""

from __future__ import annotations

import os
import sys
from typing import List

from council.config import (
    CouncilConfig,
    CouncilMember,
    DEFAULT_MEMBERS,
    ensure_member_dirs,
    load_council_config,
    save_council_config,
)


def ask(prompt: str, default: str = "") -> str:
    """Ask the user a question."""
    if default:
        full = f"{prompt} [{default}]: "
    else:
        full = f"{prompt}: "
    response = input(full).strip()
    return response if response else default


def ask_bool(prompt: str, default: bool = True) -> bool:
    """Ask a yes/no question."""
    default_str = "Y/n" if default else "y/N"
    response = ask(f"{prompt} ({default_str})").lower()
    if not response:
        return default
    return response in ("y", "yes", "true", "1")


def ask_number(prompt: str, default: int = 5) -> int:
    """Ask for a number."""
    response = ask(prompt, str(default))
    try:
        return int(response)
    except ValueError:
        return default


def print_banner():
    """Print the council setup banner."""
    print()
    print("╔══════════════════════════════════════════╗")
    print("║         🎯 Poke Council Setup            ║")
    print("║                                          ║")
    print("║  Configure your AI Council — multiple    ║")
    print("║  AI personas that debate and discuss     ║")
    print("║  your ideas.                             ║")
    print("╚══════════════════════════════════════════╝")
    print()


def print_member_template(index: int, member: CouncilMember):
    """Print a member template description."""
    print(f"  {index}. {member.emoji} {member.name}")
    print(f"     {member.bio}")
    print()


def create_member_from_template(template: CouncilMember, bot_token: str) -> CouncilMember:
    """Create a member from a template with a bot token."""
    return CouncilMember(
        id=template.id,
        name=template.name,
        bot_token=bot_token,
        emoji=template.emoji,
        bio=template.bio,
        personality=template.personality,
        enabled=True,
    )


def create_custom_member(index: int) -> CouncilMember:
    """Create a custom member through interactive prompts."""
    print(f"\n--- Custom Member #{index} ---")
    name = ask("Name (e.g. 'The Designer')")
    emoji = ask("Emoji (e.g. 🎨)", "🎨")
    bio = ask("Short bio")
    print("Personality (describe how this member thinks, their biases, expertise):")
    print("(End with an empty line)")
    lines = []
    while True:
        line = input("  > ")
        if not line:
            break
        lines.append(line)
    personality = "\n".join(lines) if lines else bio

    bot_token = ask("Telegram bot token (from @BotFather)")

    # Generate ID from name
    member_id = name.lower().replace(" ", "_").replace("the_", "")

    return CouncilMember(
        id=member_id,
        name=name,
        bot_token=bot_token,
        emoji=emoji,
        bio=bio,
        personality=personality,
        enabled=True,
    )


def run_setup():
    """Run the council setup wizard."""
    print_banner()

    # Load existing config
    config = load_council_config()

    if config.enabled and config.members:
        print("You already have a council configured with these members:")
        for m in config.members:
            status = "✅" if m.enabled else "❌"
            print(f"  {status} {m.emoji} {m.name} ({m.id})")
        print()

        if not ask_bool("Reconfigure from scratch?", default=False):
            print("Keeping existing configuration. Run `council setup --force` to reconfigure.")
            return

    print("How many council members do you want?")
    num_members = ask_number("Number of members", 5)
    print()

    # Show available templates
    print("Available council member templates:")
    print()
    for i, template in enumerate(DEFAULT_MEMBERS, 1):
        print_member_template(i, template)
    print("  C. Create a custom member")
    print()

    members: List[CouncilMember] = []

    for i in range(num_members):
        print(f"--- Member {i + 1} of {num_members} ---")
        print("Choose a template (1-5) or 'C' for custom:")
        for j, template in enumerate(DEFAULT_MEMBERS, 1):
            print(f"  {j}. {template.emoji} {template.name}")
        print("  C. Custom")

        choice = ask("Choice", "1").upper()

        if choice == "C":
            member = create_custom_member(i + 1)
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(DEFAULT_MEMBERS):
                    template = DEFAULT_MEMBERS[idx]
                    print(f"\nSelected: {template.emoji} {template.name}")
                    print(f"Bio: {template.bio}")
                    bot_token = ask("Telegram bot token (from @BotFather)")
                    member = create_member_from_template(template, bot_token)
                else:
                    print("Invalid choice, using custom.")
                    member = create_custom_member(i + 1)
            except ValueError:
                print("Invalid choice, using custom.")
                member = create_custom_member(i + 1)

        if not member.bot_token:
            print("⚠️  No bot token provided. You can add it later with `council config`.")
        else:
            print(f"✅ {member.emoji} {member.name} configured!")

        members.append(member)
        print()

    # Ask about interaction mode
    print("--- Council Mode ---")
    print("How should the council respond?")
    print("  1. Full Council — all members respond to every message")
    print("  2. Pitch Mode — structured responses (label with 'Pitch:')")
    print("  3. Debate Mode — members respond to each other")
    print("  4. Solo Mode — address members individually")

    mode_choice = ask("Mode", "1")
    modes = {"1": "full", "2": "pitch", "3": "debate", "4": "solo"}
    mode = modes.get(mode_choice, "full")

    stagger = ask_number("Delay between responses (seconds)", 3)

    # Build config
    config.enabled = True
    config.mode = mode
    config.stagger_delay = float(stagger)
    config.members = members

    # Create member directories and SOUL.md files
    print("\nSetting up member directories...")
    for member in members:
        ensure_member_dirs(member)
        print(f"  ✅ {member.emoji} {member.name} → ~/.council/members/{member.id}/")

    # Save config
    save_council_config(config)
    print(f"\n✅ Config saved to ~/.council/config.yaml")

    # Next steps
    print()
    print("══════════════════════════════════════════")
    print("  🎉 Council setup complete!")
    print()
    print("  Next steps:")
    print("  1. Create a private Telegram group")
    print("  2. Add all your council member bots to the group")
    print("  3. Run: council gateway")
    print("  4. Message the group and watch them discuss!")
    print()
    print("  Commands:")
    print("    council gateway    — Start the council gateway")
    print("    council config     — Edit council configuration")
    print("    council status     — Show council status")
    print("══════════════════════════════════════════")
    print()


if __name__ == "__main__":
    run_setup()
