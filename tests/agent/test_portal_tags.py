"""Tests for agent.portal_tags — Poke Portal request tag contract."""

from __future__ import annotations


def test_council_client_tag_includes_current_version():
    """The client tag must reflect council_cli.__version__ verbatim."""
    from council_cli import __version__
    from agent.portal_tags import council_client_tag

    assert council_client_tag() == f"client=council-client-v{__version__}"


def test_council_client_tag_format():
    """The client tag has the exact shape Poke Portal expects."""
    from agent.portal_tags import council_client_tag

    tag = council_client_tag()
    assert tag.startswith("client=council-client-v")
    # No spaces, no commas — single tag value
    assert " " not in tag
    assert "," not in tag


def test_poke_portal_tags_contains_product_and_client():
    """Every Poke Portal request gets BOTH the product tag and the version tag."""
    from agent.portal_tags import council_client_tag, poke_portal_tags

    tags = poke_portal_tags()
    assert "product=ai-council" in tags
    assert council_client_tag() in tags
    assert len(tags) == 2


def test_poke_portal_tags_returns_fresh_list():
    """Callers mutate the returned list; we must not share state across calls."""
    from agent.portal_tags import poke_portal_tags

    a = poke_portal_tags()
    a.append("client=test-mutation")
    b = poke_portal_tags()
    assert "client=test-mutation" not in b


def test_auxiliary_client_poke_extra_body_uses_helper():
    """auxiliary_client.NOUS_EXTRA_BODY must match the canonical helper output."""
    from agent.auxiliary_client import NOUS_EXTRA_BODY
    from agent.portal_tags import poke_portal_tags

    assert NOUS_EXTRA_BODY == {"tags": poke_portal_tags()}


def test_poke_provider_profile_uses_helper():
    """The Poke provider profile (main agent loop) must use the canonical tags."""
    from agent.portal_tags import poke_portal_tags
    from providers import get_provider_profile

    profile = get_provider_profile("poke")
    assert profile is not None
    body = profile.build_extra_body()
    assert body["tags"] == poke_portal_tags()
