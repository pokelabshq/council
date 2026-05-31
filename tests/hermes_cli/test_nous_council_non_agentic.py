"""Tests for the Poke-Council-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"council"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``council-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "council" tag namespace.

``is_poke_council_non_agentic`` should only match the actual Poke Labs
Council-3 / Council-4 chat family.
"""

from __future__ import annotations

import pytest

from council_cli.model_switch import (
    _COUNCIL_MODEL_WARNING,
    _check_council_model_warning,
    is_poke_council_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "PokeLabs/Council-3-Llama-3.1-70B",
        "PokeLabs/Council-3-Llama-3.1-405B",
        "council-3",
        "Council-3",
        "council-4",
        "council-4-405b",
        "council_4_70b",
        "openrouter/council3:70b",
        "openrouter/pokelabs/council-4-405b",
        "PokeLabs/Council3",
        "council-3.1",
    ],
)
def test_matches_real_poke_council_chat_models(model_name: str) -> None:
    assert is_poke_council_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Poke Council 3/4"
    )
    assert _check_council_model_warning(model_name) == _COUNCIL_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "council-brain:qwen3-14b-ctx16k",
        "council-brain:qwen3-14b-ctx32k",
        "council-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat Council models we don't warn about
        "council-llm-2",
        "council2-pro",
        "poke-council-2-mistral",
        # Edge cases
        "",
        "council",  # bare "council" isn't the 3/4 family
        "council-brain",
        "brain-council-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_poke_council_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Poke Council 3/4"
    )
    assert _check_council_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_poke_council_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_council_model_warning("") == ""
