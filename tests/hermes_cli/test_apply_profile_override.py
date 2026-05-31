"""Regression tests for _apply_profile_override COUNCIL_HOME guard (issue #22502).

When COUNCIL_HOME is set to the council root (e.g. systemd hardcodes
COUNCIL_HOME=/root/.council), _apply_profile_override must still read
active_profile and update COUNCIL_HOME to the profile directory.

When COUNCIL_HOME is already a profile directory (.../profiles/<name>),
_apply_profile_override must trust it and return without re-reading
active_profile (child-process inheritance contract).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path



def _run_apply_profile_override(
    tmp_path, monkeypatch, *, council_home: str | None, active_profile: str | None,
    argv: list[str] | None = None,
):
    """Run _apply_profile_override in isolation.

    Returns the value of os.environ["COUNCIL_HOME"] after the call,
    or None if unset.
    """
    council_root = tmp_path / ".council"
    council_root.mkdir(parents=True, exist_ok=True)

    if active_profile is not None:
        (council_root / "active_profile").write_text(active_profile)

    if active_profile and active_profile != "default":
        (council_root / "profiles" / active_profile).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    if council_home is not None:
        monkeypatch.setenv("COUNCIL_HOME", council_home)
    else:
        monkeypatch.delenv("COUNCIL_HOME", raising=False)

    monkeypatch.setattr(sys, "argv", argv or ["council", "gateway", "start"])

    from council_cli.main import _apply_profile_override
    _apply_profile_override()

    return os.environ.get("COUNCIL_HOME")


class TestApplyProfileOverrideCouncilHomeGuard:
    """Regression guard for issue #22502.

    Verifies that COUNCIL_HOME pointing to the council root does NOT suppress
    the active_profile check, while COUNCIL_HOME already pointing to a
    profile directory IS trusted as-is.
    """

    def test_council_home_at_root_with_active_profile_is_redirected(
        self, tmp_path, monkeypatch
    ):
        """COUNCIL_HOME=/root/.council + active_profile=coder must redirect
        COUNCIL_HOME to .../profiles/coder.

        Bug scenario from #22502: systemd sets COUNCIL_HOME to the council root
        and the user switches to a profile via `council profile use`.
        Before the fix, the guard returned early and active_profile was ignored.
        """
        council_root = tmp_path / ".council"
        council_root.mkdir(parents=True, exist_ok=True)

        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            council_home=str(council_root),
            active_profile="coder",
        )

        assert result is not None, "COUNCIL_HOME must be set after profile redirect"
        assert "profiles" in result, (
            f"Expected COUNCIL_HOME to point into profiles/ dir, got: {result!r}"
        )
        assert result.endswith("coder"), (
            f"Expected COUNCIL_HOME to end with 'coder', got: {result!r}"
        )

    def test_council_home_already_profile_dir_is_trusted(self, tmp_path, monkeypatch):
        """COUNCIL_HOME=.../profiles/coder must not be overridden even when
        active_profile says something different.

        Preserves the child-process inheritance contract: a subprocess spawned
        with COUNCIL_HOME already set to a specific profile must stay in that
        profile.
        """
        council_root = tmp_path / ".council"
        profile_dir = council_root / "profiles" / "coder"
        profile_dir.mkdir(parents=True, exist_ok=True)

        (council_root / "active_profile").write_text("other")

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("COUNCIL_HOME", str(profile_dir))
        monkeypatch.setattr(sys, "argv", ["council", "gateway", "start"])

        from council_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("COUNCIL_HOME") == str(profile_dir), (
            "COUNCIL_HOME must remain unchanged when already pointing to a profile dir"
        )

    def test_council_home_unset_reads_active_profile(self, tmp_path, monkeypatch):
        """Classic case: COUNCIL_HOME unset + active_profile=coder must set
        COUNCIL_HOME to the profile directory (existing behaviour must not regress).
        """
        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            council_home=None,
            active_profile="coder",
        )

        assert result is not None
        assert "coder" in result

    def test_council_home_unset_default_profile_no_redirect(self, tmp_path, monkeypatch):
        """active_profile=default must not redirect COUNCIL_HOME."""
        council_root = tmp_path / ".council"
        council_root.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.delenv("COUNCIL_HOME", raising=False)
        monkeypatch.setattr(sys, "argv", ["council", "gateway", "start"])
        (council_root / "active_profile").write_text("default")

        from council_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("COUNCIL_HOME") is None
