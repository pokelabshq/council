# Council Skills Index

Available skills for the Council platform.

## Built-in Services

### Sentiment Analysis
```bash
curl -X POST http://localhost:8700/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'
```

### Link Preview
```bash
curl -X POST http://localhost:8700/api/link-preview/preview \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Keyword Extraction
```bash
curl -X POST http://localhost:8700/api/keyword-extract/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here", "top_n": 10}'
```

### QR Code Generation
```bash
curl -X POST http://localhost:8700/api/qr/qr \
  -H "Content-Type: application/json" \
  -d '{"data": "https://pokelabs.org", "size": 256}'
```

### DNS Lookup
```bash
curl -X POST http://localhost:8700/api/dns/resolve \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

### Color Palette
```bash
curl -X POST http://localhost:8700/api/colors/generate \
  -H "Content-Type: application/json" \
  -d '{"base": "#00d4ff", "count": 5, "mode": "analogous"}'
```

### Text Summary
```bash
curl -X POST http://localhost:8700/api/summary/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Long article text...", "sentences": 3}'
```

### URL Shortener
```bash
curl -X POST http://localhost:8700/api/shorten/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://very-long-url.com/path"}'
```

### Password Generator
```bash
curl -X POST http://localhost:8700/api/password/generate \
  -H "Content-Type: application/json" \
  -d '{"length": 20, "symbols": true}'
```

### Timestamp Converter
```bash
curl -X POST http://localhost:8700/api/timestamp/convert \
  -H "Content-Type: application/json" \
  -d '{"timestamp": 1717459200}'
```

### JSON Formatter
```bash
curl -X POST http://localhost:8700/api/json/format \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "value"}, "indent": 2}'
```

### Base64 Tool
```bash
curl -X POST http://localhost:8700/api/base64/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}'
```

### Markdown Renderer
```bash
curl -X POST http://localhost:8700/api/markdown/render \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\n\nThis is **bold**."}'
```

### Webhook Relay
```bash
curl -X POST http://localhost:8779/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"repository": {"full_name": "user/repo"}, "ref": "main"}'
```

### Status Dashboard
```bash
curl http://localhost:8778/api/health
curl http://localhost:8700/api/services
```

## GitHub Actions Skills

### Auto-merge Dependabot PRs
Automatically approves and squash-merges semver-patch Dependabot PRs.
- Workflow: `.github/workflows/auto-merge.yml`
- Only merges patch updates
- Waits for CI to pass

### Service Audit
Weekly audit of all services (flake8 + bandit + structure check).
- Workflow: `.github/workflows/audit.yml`
- Runs every Monday at 9am UTC
