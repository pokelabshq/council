"""
Stub module for poke_account.

This module was referenced during development but
the original implementation was not included in the fork. These are no-op
stubs so imports don't fail.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class PokePortalAccountInfo:
    """Stub for Poke Portal account info."""
    email: str = ""
    subscription_tier: str = "free"
    monthly_spend_usd: float = 0.0
    monthly_request_count: int = 0
    monthly_request_limit: int = 0
    features: dict = field(default_factory=dict)

    @property
    def is_subscribed(self) -> bool:
        return self.subscription_tier != "free"

    @property
    def is_admin(self) -> bool:
        return False


def get_poke_portal_account_info(config: Any = None, force_fresh: bool = False) -> PokePortalAccountInfo:
    """Return stub account info."""
    return PokePortalAccountInfo()


def format_poke_portal_entitlement_message(feature: str, has_access: bool) -> str:
    """Return stub entitlement message."""
    if has_access:
        return f"✓ {feature} is available on your plan."
    return f"✗ {feature} requires a Poke Portal subscription."


def poke_portal_account_menu(config: Any = None) -> Optional[str]:
    """Return stub account menu."""
    return None
