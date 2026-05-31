"""
Stub module for poke_subscription.

This module was referenced during the rebrand from Hermes to Council but
the original implementation was not included in the fork. These are no-op
stubs so imports don't fail.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PokeSubscriptionFeatures:
    """Stub for Poke subscription features."""
    poke_auth_present: bool = False
    managed_tools_available: bool = False
    tool_gateway_available: bool = False
    managed_browser_available: bool = False
    modal_available: bool = False
    fall_available: bool = False
    tier: str = "free"


def get_poke_subscription_features(config: Any = None, force_fresh: bool = False) -> PokeSubscriptionFeatures:
    """Return stub subscription features."""
    return PokeSubscriptionFeatures()


def apply_poke_managed_defaults(config: Any = None) -> None:
    """No-op stub for applying managed defaults."""
    pass


def prompt_enable_tool_gateway(config: Any = None) -> Optional[str]:
    """No-op stub for enabling tool gateway."""
    return None


def managed_poke_tools_enabled(config: Any = None) -> bool:
    """Return False — managed tools not available in stub."""
    return False
