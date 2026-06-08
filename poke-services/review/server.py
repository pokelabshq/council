"""ai code review micro-service for council.

provides a POST /api/review endpoint that accepts a diff and returns
a structured code review using sed/regex-based static analysis.

no ai model needed — this is a fast, deterministic review for common patterns.
for deep reviews, use `council review` which runs the full agent.

usage:
    curl -X POST http://localhost:8792/api/review \\
      -H "Content-Type: application/json" \\
      -d '{"diff": "...", "language": "python"}'
"""

import json
import os
import re
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = int(os.environ.get("PORT", 8792))

# ── review rules ──────────────────────────────────────────

_RULES = {
    "python": [
        {
            "pattern": r"cursor\.execute\s*\(\s*f[\"']",
            "severity": "critical",
            "category": "security",
            "message": "sql injection risk: f-string in cursor.execute()",
            "suggestion": "use parameterized queries: cursor.execute('...', [param])",
        },
        {
            "pattern": r"\.execute\s*\(\s*.*\+",
            "severity": "critical",
            "category": "security",
            "message": "possible sql injection: string concatenation in .execute()",
            "suggestion": "use parameterized queries instead of string concatenation",
        },
        {
            "pattern": r"eval\s*\(",
            "severity": "critical",
            "category": "security",
            "message": "eval() is dangerous and should be avoided",
            "suggestion": "use ast.literal_eval() or json.loads() for safe evaluation",
        },
        {
            "pattern": r"exec\s*\(",
            "severity": "critical",
            "category": "security",
            "message": "exec() is dangerous and should be avoided",
            "suggestion": "avoid dynamic code execution; refactor to use functions",
        },
        {
            "pattern": r"password\s*=\s*['\"]",
            "severity": "warning",
            "category": "security",
            "message": "hardcoded password detected",
            "suggestion": "use environment variables or a secrets manager",
        },
        {
            "pattern": r"secret\s*=\s*['\"]",
            "severity": "warning",
            "category": "security",
            "message": "hardcoded secret detected",
            "suggestion": "use environment variables or a secrets manager",
        },
        {
            "pattern": r"api[_-]?key\s*=\s*['\"]",
            "severity": "warning",
            "category": "security",
            "message": "hardcoded api key detected",
            "suggestion": "use environment variables or a secrets manager",
        },
        {
            "pattern": r"print\s*\(",
            "severity": "info",
            "category": "style",
            "message": "print statement found (use logging in production code)",
            "suggestion": "replace print() with a proper logger",
        },
        {
            "pattern": r"except\s*:",
            "severity": "warning",
            "category": "bug",
            "message": "bare except clause — catches everything including KeyboardInterrupt",
            "suggestion": "use 'except Exception:' or a more specific exception type",
        },
        {
            "pattern": r"import\s+\*",
            "severity": "info",
            "category": "style",
            "message": "wildcard import — pollutes namespace",
            "suggestion": "import specific names: from x import y",
        },
        {
            "pattern": r"\.format\s*\(",
            "severity": "info",
            "category": "style",
            "message": ".format() found (f-strings are preferred in python 3.6+)",
            "suggestion": "consider using f-strings for readability",
        },
    ],
    "javascript": [
        {
            "pattern": r"eval\s*\(",
            "severity": "critical",
            "category": "security",
            "message": "eval() is dangerous and should be avoided",
            "suggestion": "use JSON.parse() for json data; avoid dynamic code execution",
        },
        {
            "pattern": r"innerHTML\s*=",
            "severity": "warning",
            "category": "security",
            "message": "innerHTML assignment — potential xss vector",
            "suggestion": "use textContent or sanitize with DOMPurify",
        },
        {
            "pattern": r"document\.write\s*\(",
            "severity": "warning",
            "category": "security",
            "message": "document.write() can be exploited for xss",
            "suggestion": "use DOM manipulation methods instead",
        },
        {
            "pattern": r"var\s+",
            "severity": "info",
            "category": "style",
            "message": "var declaration (use let or const)",
            "suggestion": "replace var with let (mutable) or const (immutable)",
        },
    ],
    "typescript": [
        {
            "pattern": r":\s*any\b",
            "severity": "info",
            "category": "style",
            "message": ": any type annotation defeats type safety",
            "suggestion": "use a specific type or unknown instead of any",
        },
        {
            "pattern": r"as\s+any\b",
            "severity": "warning",
            "category": "style",
            "message": "'as any' type assertion defeats type safety",
            "suggestion": "use a proper type guard or assertion",
        },
    ],
}


def run_review(diff: str, language: str = "python") -> dict:
    """Run static analysis rules against a diff."""
    rules = _RULES.get(language, _RULES["python"])
    findings = []

    # extract added lines (lines starting with + in the diff)
    added_lines = []
    current_file = "unknown"
    line_num = 0

    for line in diff.splitlines():
        # track file
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            continue
        # track line number
        if line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            if match:
                line_num = int(match.group(1)) - 1
            continue
        # added line
        if line.startswith("+") and not line.startswith("+++"):
            line_num += 1
            content = line[1:]  # strip the + prefix
            for rule in rules:
                if re.search(rule["pattern"], content):
                    findings.append({
                        "severity": rule["severity"],
                        "category": rule["category"],
                        "file": current_file,
                        "line": line_num,
                        "message": rule["message"],
                        "suggestion": rule["suggestion"],
                        "code": content.strip()[:120],
                    })

    # calculate score
    score = 100
    for f in findings:
        if f["severity"] == "critical":
            score -= 30
        elif f["severity"] == "warning":
            score -= 10
        elif f["severity"] == "info":
            score -= 2
    score = max(0, score)

    if not findings:
        verdict = "clean"
    elif any(f["severity"] == "critical" for f in findings):
        verdict = "request changes"
    elif any(f["severity"] == "warning" for f in findings):
        verdict = "needs discussion"
    else:
        verdict = "approve"

    return {
        "verdict": verdict,
        "score": score,
        "findings_count": len(findings),
        "findings": findings,
    }


# ── http handler ──────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    """handle review requests."""

    def do_GET(self):
        if self.path == "/api/health":
            self._respond(200, {"ok": True, "service": "review", "port": PORT})
        elif self.path == "/":
            self._respond(200, {
                "service": "review",
                "version": "1.0.0",
                "endpoints": {
                    "POST /api/review": "submit a diff for review",
                    "GET /api/health": "health check",
                },
            })
        else:
            self._respond(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/api/review":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._respond(400, {"error": "invalid json"})
                return

            diff = data.get("diff", "")
            language = data.get("language", "python")

            if not diff:
                self._respond(400, {"error": "missing 'diff' field"})
                return

            result = run_review(diff, language)
            self._respond(200, result)
        else:
            self._respond(404, {"error": "not found"})

    def _respond(self, status: int, body: dict):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        """suppress default logging to keep output clean."""
        pass


# ── entry point ───────────────────────────────────────────

def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"review service running on port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
