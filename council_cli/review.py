"""
Code review command for council CLI.

Usage:
    council review                    # review staged changes
    council review --branch main      # review all changes vs a branch
    council review --pr 42            # review a github PR
    council review --file path.py     # review a single file
    council review --diff <text>      # review raw diff text
    council review --fix              # auto-fix what it can (staged changes only)
    council review --json             # output machine-readable json

All review is done locally using the configured council model — no external
API needed beyond what council already uses for chat.
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def _run_git(*args: str, check: bool = True) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        print(f"git error: {err}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def _get_staged_diff() -> str:
    """Get the diff of staged changes."""
    diff = _run_git("diff", "--staged", "--no-color", check=False)
    if not diff:
        diff = _run_git("diff", "--no-color", check=False)
    if not diff:
        print("no changes found. stage changes with 'git add' or use --branch / --pr / --file.")
        sys.exit(0)
    return diff


def _get_branch_diff(branch: str) -> str:
    """Get the diff between current branch and the given branch."""
    return _run_git("diff", f"{branch}...HEAD", "--no-color")


def _get_file_diff(filepath: str) -> str:
    """Get the diff for a single file (unstaged changes)."""
    return _run_git("diff", "--no-color", "--", filepath, check=False)


def _get_pr_diff(pr_number: str) -> str:
    """Fetch and return the diff of a GitHub PR."""
    try:
        result = subprocess.run(
            ["gh", "pr", "diff", pr_number, "--patch"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"could not fetch pr #{pr_number}: {result.stderr.strip()}", file=sys.stderr)
            print("make sure 'gh' is authenticated and the pr exists.", file=sys.stderr)
            sys.exit(1)
        return result.stdout.strip()
    except FileNotFoundError:
        print("'gh' cli not found. install it or use --branch / --file instead.", file=sys.stderr)
        sys.exit(1)


def _build_review_prompt(diff: str, context: str = "") -> str:
    """Build the review prompt from the diff."""
    header = textwrap.dedent("""\
    you are reviewing code changes. analyze the diff below and provide a structured review.

    ## review checklist

    for each issue found, report:
    - severity: critical / warning / info
    - file and line number (if applicable)
    - category: security / performance / bug / style / testing / design
    - description: what's wrong and why it matters
    - suggestion: how to fix it (be specific, include code if helpful)

    categories to check:
    - **security**: injection, xss, secrets exposure, access control, input validation
    - **performance**: n+1 queries, unbounded loops, unnecessary allocations, missing indexes
    - **bugs**: null/edge cases, race conditions, off-by-one, type errors, missing error handling
    - **design**: single responsibility, coupling, missing abstractions, api consistency
    - **testing**: missing tests for new logic, untested edge cases
    - **style**: naming, consistency, dead code, missing docstrings/type hints

    ## output format

    if the diff has issues:
    start with a one-line summary, then list each finding:

    **summary**: [one line]

    | # | severity | category | location | description | suggestion |
    |---|----------|----------|----------|-------------|------------|
    | 1 | critical | security | foo.py:42 | ... | ... |
    | 2 | warning  | bug      | bar.py:10| ... | ... |

    end with a **verdict**: approve / request changes / needs discussion

    if the diff looks clean:
    respond with: **clean** — no issues found. one-line summary of what the change does.

    focus on real issues. don't nitpick style unless it hurts readability.
    be concise. don't repeat the obvious.

    """)
    context_block = ""
    if context:
        context_block = f"## additional context\n{context}\n\n"
    diff_block = f"## diff\n\n```diff\n{diff[:50000]}\n```\n"
    return header + context_block + diff_block


def _build_fix_prompt(diff: str) -> str:
    """Build a prompt that generates fixed code."""
    return textwrap.dedent("""\
    you are reviewing and fixing code changes. analyze the diff below and generate a
    unified diff of fixes for any bugs, security issues, or performance problems found.

    rules:
    - only fix real issues, not style preferences
    - output a valid unified diff (starting with --- a/ and +++ b/)
    - if nothing needs fixing, output: **no fixes needed**
    - don't change unrelated code
    - preserve the author's style and naming conventions

    ## diff

    ```diff
    """) + diff[:50000] + "\n```\n"


# ── severity scoring ──────────────────────────────────────────────────────────

_SEVERITY_SCORE = {"critical": 0, "warning": 1, "info": 2}


def _parse_review_table(review_text: str) -> dict:
    """Parse the agent's review output into structured data."""
    import re

    findings = []
    verdict = "unknown"
    summary = ""

    # extract summary
    summary_match = re.search(r"\*\*summary\*\*[:\s]+(.+?)(?:\n|$)", review_text, re.IGNORECASE)
    if summary_match:
        summary = summary_match.group(1).strip()

    # extract verdict
    verdict_match = re.search(r"\*\*verdict\*\*[:\s]+(.+?)(?:\n|$)", review_text, re.IGNORECASE)
    if verdict_match:
        verdict = verdict_match.group(1).strip().lower()

    # check for clean
    if re.search(r"\*\*clean\*\*", review_text, re.IGNORECASE):
        verdict = "approve"
        after = review_text.split("**clean**")[1].strip()
        # strip em-dash or regular dash
        if after.startswith("\u2014"):
            after = after[1:].strip()
        elif after.startswith("-"):
            after = after[1:].strip()
        summary = after
        return {"summary": summary, "verdict": verdict, "findings": [], "score": 100}

    # extract table rows
    row_pattern = re.compile(
        r"\|\s*\d+\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
    )
    for match in row_pattern.finditer(review_text):
        sev = match.group(1).lower().strip()
        cat = match.group(2).lower().strip()
        loc = match.group(3).strip()
        desc = match.group(4).strip()
        sugg = match.group(5).strip()
        findings.append({
            "severity": sev,
            "category": cat,
            "location": loc,
            "description": desc,
            "suggestion": sugg,
        })

    # if no table but text mentions issues, extract loosely
    if not findings:
        for line in review_text.splitlines():
            low = line.lower()
            if any(w in low for w in ("critical", "security", "bug", "vulnerability", "injection", "xss")):
                findings.append({
                    "severity": "warning",
                    "category": "unknown",
                    "location": "unknown",
                    "description": line.strip(),
                    "suggestion": "",
                })

    # calculate a rough score (100 = perfect, 0 = broken)
    score = 100
    for f in findings:
        penalty = {"critical": 30, "warning": 10, "info": 2}.get(f["severity"], 5)
        score -= penalty
    score = max(0, score)

    return {"summary": summary, "verdict": verdict, "findings": findings, "score": score}


# ── main entry point ──────────────────────────────────────────────────────────

def cmd_review(args: argparse.Namespace) -> None:
    """Run code review on git diffs, files, or PRs."""
    # 1. collect the diff
    diff = ""
    context = ""

    if hasattr(args, "diff_text") and args.diff_text:
        diff = args.diff_text
    elif hasattr(args, "file") and args.file:
        diff = _get_file_diff(args.file)
        context = f"reviewing file: {args.file}"
    elif hasattr(args, "pr") and args.pr:
        diff = _get_pr_diff(str(args.pr))
        context = f"reviewing github pr #{args.pr}"
    elif hasattr(args, "branch") and args.branch:
        diff = _get_branch_diff(args.branch)
        context = f"reviewing changes against branch: {args.branch}"
    else:
        diff = _get_staged_diff()
        context = "reviewing staged changes"

    if not diff.strip():
        print("nothing to review.")
        sys.exit(0)

    # 2. build the prompt
    if hasattr(args, "fix") and args.fix:
        prompt = _build_fix_prompt(diff)
    else:
        prompt = _build_review_prompt(diff, context)

    # 3. run the review through council's agent
    try:
        from run_agent import AIAgent

        agent = AIAgent(
            project_root=str(PROJECT_ROOT),
            quiet=True,
        )
        review_text = agent.chat(prompt)
    except ImportError:
        print("could not import agent. paste the following into 'council chat':\n")
        print(prompt)
        sys.exit(0)
    except Exception as exc:
        print(f"agent error: {exc}", file=sys.stderr)
        print("try running 'council chat' manually and paste the diff.", file=sys.stderr)
        sys.exit(1)

    # 4. parse and display results
    json_output = getattr(args, "json", False)

    if json_output:
        parsed = _parse_review_table(review_text)
        print(json.dumps(parsed, indent=2))
    else:
        print()
        print(review_text)
        print()

        parsed = _parse_review_table(review_text)
        n = len(parsed["findings"])
        score = parsed["score"]
        if n == 0:
            print("─" * 60)
            print("  no issues found. looks good.")
        else:
            sev_counts = {}
            for f in parsed["findings"]:
                sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1
            sev_str = ", ".join(f"{k}: {v}" for k, v in sorted(
                sev_counts.items(), key=lambda x: _SEVERITY_SCORE.get(x[0], 99)
            ))
            print("─" * 60)
            print(f"  {n} finding(s) — {sev_str}")
            print(f"  review score: {score}/100")
            print(f"  verdict: {parsed['verdict']}")

    # exit with non-zero if critical issues found
    if any(f["severity"] == "critical" for f in parsed.get("findings", [])):
        sys.exit(2)
