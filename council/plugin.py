"""
Council Fan-Out Plugin for Poke Council.

Enables multi-agent "council" mode where incoming messages are fanned out
to all enabled council members via the pre_gateway_dispatch hook.

Also registers /council command handlers for gateway and CLI.

Usage:
    Enable by adding to ~/.council/config.yaml:
        council:
          enabled: true
          members:
            - id: strategist
              name: "The Strategist"
              bot_token: "YOUR_BOT_TOKEN"
              ...
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _load_council_config():
    """Load council config, returning None if unavailable."""
    try:
        import sys
        project_root = Path(__file__).resolve().parents[2]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from council import load_council_config
        return load_council_config()
    except Exception as e:
        logger.debug("Council plugin: could not load config: %s", e)
        return None


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

def _build_member_system_prompt(member, all_members: list) -> str:
    parts = []

    # SOUL.md
    soul_path = Path.home() / ".council" / "members" / member.id / "SOUL.md"
    if soul_path.exists():
        try:
            parts.append(soul_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    elif member.personality:
        parts.append(member.personality)

    # Council context
    others = ", ".join(
        f"{m.emoji} {m.name}" for m in all_members if m.id != member.id
    )
    parts.append(
        f"\n\n## Council Context\n"
        f"You are a member of the AI Council. Other members: {others}.\n"
        f"Respond with your unique perspective. Be honest, constructive, stay in character.\n"
        f"Keep responses focused — 2-4 paragraphs max.\n"
        f"Begin with: {member.emoji} **{member.name}**:"
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Per-member agent runner
# ---------------------------------------------------------------------------

async def _run_member(
    member,
    all_members: list,
    gateway_runner,
    event,
    runtime_kwargs: dict,
    stagger_delay: float,
    member_index: int,
):
    source = event.source
    member_key = f"council:{member.id}:{source.chat_id}"

    if member_index > 0 and stagger_delay > 0:
        await asyncio.sleep(stagger_delay)

    system_prompt = _build_member_system_prompt(member, all_members)

    try:
        from run_agent import AIAgent
        model = member.model or runtime_kwargs.get("model", "")
        kw = {k: v for k, v in runtime_kwargs.items() if k != "model"}
        agent = AIAgent(
            model=model, **kw,
            max_iterations=90, quiet_mode=True, verbose_logging=False,
            session_id=member_key, platform="telegram",
            user_id=source.user_id, user_name=source.user_name,
            chat_id=source.chat_id,
        )
    except Exception as e:
        logger.error("Council: build agent failed for %s: %s", member.id, e, exc_info=True)
        return

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: agent.chat(event.text or "", system_message=system_prompt),
        )
        if response:
            adapter = gateway_runner.adapters.get(source.platform)
            if adapter:
                await adapter.send(source.chat_id, response)
    except Exception as e:
        logger.error("Council: agent error for %s: %s", member.id, e, exc_info=True)


# ---------------------------------------------------------------------------
# Fan-out orchestrator
# ---------------------------------------------------------------------------

async def _council_fanout(gateway_runner, event, config, stagger_delay: float):
    try:
        from gateway.run import _resolve_runtime_agent_kwargs
        runtime_kwargs = _resolve_runtime_agent_kwargs()
    except Exception as e:
        logger.warning("Council: runtime kwargs failed: %s", e)
        runtime_kwargs = {}

    members = config.get_enabled_members()
    if not members:
        return

    logger.info("Council: fan-out to %d members", len(members))
    tasks = [
        asyncio.create_task(
            _run_member(m, members, gateway_runner, event, runtime_kwargs,
                        stagger_delay, i)
        )
        for i, m in enumerate(members)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            logger.error("Council: %s failed: %s", members[i].id, r)


# ---------------------------------------------------------------------------
# pre_gateway_dispatch hook
# ---------------------------------------------------------------------------

async def on_pre_gateway_dispatch(event, gateway, session_store, **kwargs):
    config = _load_council_config()
    if not config or not config.enabled:
        return None

    members = config.get_enabled_members()
    if not members:
        return None

    # Skip council sessions (already fanned-out)
    source = event.source
    try:
        sk = gateway._session_key_for_source(source)
        if sk and sk.startswith("council:"):
            return None
    except Exception:
        pass

    # Don't fan-out command messages (those are handled separately)
    text = event.text or ""
    if text.startswith("/"):
        return None

    asyncio.ensure_future(
        _council_fanout(gateway, event, config, config.stagger_delay)
    )
    return {"action": "skip", "reason": "council_fanout"}


# ---------------------------------------------------------------------------
# Council CLI command handler (for /council in gateway)
# ---------------------------------------------------------------------------

async def _handle_council_command(event) -> str:
    """Handle /council command in gateway/CLI."""
    from council.commands import (
        council_status, council_list, council_add_member,
        council_remove_member, council_toggle_member, council_set_mode,
        DEFAULT_MEMBERS,
    )

    args = (event.text or "").replace("/council", "", 1).strip().split()
    sub = args[0].lower() if args else "status"

    if sub == "status":
        return council_status()
    elif sub == "list":
        return council_list()
    elif sub == "add":
        template_id = args[1] if len(args) > 1 else ""
        # Find template
        tmpl = None
        for t in DEFAULT_MEMBERS:
            if t.id == template_id:
                tmpl = t
                break
        if not tmpl:
            available = ", ".join(f"`{t.id}`" for t in DEFAULT_MEMBERS)
            return f"Usage: /council add <template_id> <bot_token>\nAvailable: {available}"
        return council_add_member(
            name=tmpl.name, emoji=tmpl.emoji, bio=tmpl.bio,
            personality=tmpl.personality, bot_token=args[2] if len(args) > 2 else "",
            template_id=template_id,
        )
    elif sub == "remove":
        if len(args) < 2:
            return "Usage: /council remove <member_id>"
        return council_remove_member(args[1])
    elif sub == "enable":
        if len(args) < 2:
            return "Usage: /council enable <member_id>"
        return council_toggle_member(args[1], True)
    elif sub == "disable":
        if len(args) < 2:
            return "Usage: /council disable <member_id>"
        return council_toggle_member(args[1], False)
    elif sub == "mode":
        valid = "full, pitch, debate, solo"
        if len(args) < 2:
            config = _load_council_config()
            return f"Current mode: {config.mode if config else 'full'}\nValid: {valid}"
        return council_set_mode(args[1])
    elif sub == "setup":
        return (
            "🎯 **Poke Council Setup**\n\n"
            "Run `council setup` in your terminal for the interactive wizard.\n"
            "Or configure manually in `~/.council/config.yaml`.\n\n"
            "Quick start:\n"
            "1. Create bots via @BotFather on Telegram\n"
            f"2. `/council add strategist <BOT_TOKEN>`\n"
            f"3. Repeat for each member\n"
            "4. `/council status` to verify\n"
            "5. Start the gateway: `council gateway`"
        )
    else:
        return (
            "🎯 **Council Commands**\n"
            "/council status — Show status\n"
            "/council list — List members\n"
            "/council add <id> <token> — Add member\n"
            "/council remove <id> — Remove member\n"
            "/council enable <id> — Enable member\n"
            "/council disable <id> — Disable member\n"
            "/council mode <mode> — Set mode\n"
            "/council setup — Setup guide"
        )


# ---------------------------------------------------------------------------
# post_session_end hook (cleanup)
# ---------------------------------------------------------------------------

async def on_session_end(event=None, session_store=None, session_key=None, **kwargs):
    """Clean up council sessions when they end."""
    if session_key and session_key.startswith("council:"):
        logger.debug("Council session ended: %s", session_key)


# ---------------------------------------------------------------------------
# Plugin register
# ---------------------------------------------------------------------------

def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", on_pre_gateway_dispatch)
    ctx.register_hook("on_session_end", on_session_end)

    # Also register council commands via the command registry plugin hook if available
    try:
        project_root = Path(__file__).resolve().parents[2]
        if str(project_root) not in __import__("sys").path:
            __import__("sys").path.insert(0, str(project_root))
        from council_cli import commands as cmd_mod
        # Check if COMMAND_REGISTRY exists
        if hasattr(cmd_mod, "COMMAND_REGISTRY"):
            # Council commands are subcommands of /council, so we register
            # them as a group
            pass  # The /council command is handled in the gateway directly
    except Exception:
        pass

    logger.info("Council fan-out plugin registered")
