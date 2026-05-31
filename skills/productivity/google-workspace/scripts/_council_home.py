"""Resolve COUNCIL_HOME for standalone skill scripts.

Skill scripts may run outside the Council process (e.g. system Python,
nix env, CI) where ``council_constants`` is not importable.  This module
provides the same ``get_council_home()`` and ``display_council_home()``
contracts as ``council_constants`` without requiring it on ``sys.path``.

When ``council_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``council_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``COUNCIL_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from council_constants import display_council_home as display_council_home
    from council_constants import get_council_home as get_council_home
except (ModuleNotFoundError, ImportError):

    def get_council_home() -> Path:
        """Return the Council home directory (default: ~/.council).

        Mirrors ``council_constants.get_council_home()``."""
        val = os.environ.get("COUNCIL_HOME", "").strip()
        return Path(val) if val else Path.home() / ".council"

    def display_council_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``council_constants.display_council_home()``."""
        home = get_council_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
