# review service

ai-powered code review micro-service for council.

## what it does

provides a `POST /api/review` endpoint that accepts a diff and returns
a structured code review with findings for security, bugs, and style issues.

two modes:
- **fast static analysis** (this service): deterministic rules, no ai model needed
- **deep review** (`council` cli): full agent review for complex issues

## usage

```bash
python3 server.py
# or
docker build -t review . && docker run -p 8792:8792 review

# health check
curl http://localhost:8792/api/health

# review a diff
curl -X POST http://localhost:8792/api/review \
  -H "Content-Type: application/json" \
  -d '{"diff": "+++ b/test.py\n@@ -1 +1 @@\n-old\n+new", "language": "python"}'
```

## api

### POST /api/review

request body:
```json
{
  "diff": "string (unified diff text)",
  "language": "python | javascript | typescript"
}
```

response:
```json
{
  "verdict": "clean | approve | needs discussion | request changes",
  "score": 30,
  "findings_count": 3,
  "findings": [
    {
      "severity": "critical",
      "category": "security",
      "file": "test.py",
      "line": 42,
      "message": "sql injection risk: f-string in cursor.execute()",
      "suggestion": "use parameterized queries",
      "code": "cursor.execute(f\"...\")"
    }
  ]
}
```

## tech stack

python 3.12, stdlib only.
