# 🦉 Poke Labs — Open Source Micro-Services

> 12 zero-dependency Python micro-services with x402 payments.
> Built by [Poke](https://github.com/pokelabshq) for [Alexander Wondwossen](https://github.com/TheAlxLabs).

## Quick Start

```bash
# Clone and deploy all services in one command
git clone https://github.com/pokelabshq/council.git
cd council/poke-services
bash deploy.sh
```

All services start on ports 8765-8776. Gateway runs on port 8700.

## Services

### 🔗 Link Preview (`:8765`)
Extract title, description, image, and favicon from any URL.

```bash
curl -X POST http://localhost:8700/link-preview/api/preview \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

### 🔑 Keyword Extractor (`:8766`)
TF-IDF keyword and entity extraction from text.

```bash
curl -X POST http://localhost:8700/keyword/api/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Python is great for building web applications"}'
```

### 📝 Summarizer (`:8767`)
Extractive text summarization.

```bash
curl -X POST http://localhost:8700/summarize/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here..."}'
```

### 📱 QR Code Generator (`:8768`)
Generate SVG QR codes from any text or URL.

```bash
curl -X POST http://localhost:8700/qr/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "https://pokelabs.org"}'
```

### 🔍 DNS Checker (`:8769`)
Query any DNS record type.

```bash
curl -X POST http://localhost:8700/dns/api/query \
  -H "Content-Type: application/json" \
  -d '{"domain": "github.com", "type": "A"}'
```

### 🎨 Color Palette Generator (`:8771`)
Generate harmonious color palettes.

```bash
curl -X POST http://localhost:8700/color/api/generate \
  -H "Content-Type: application/json" \
  -d '{"base": "#7b2ff7", "count": 5}'
```

### 🔗 URL Shortener (`:8772`)
Short URLs with click tracking.

```bash
curl -X POST http://localhost:8700/url/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://pokelabs.org"}'
```

### 🏗️ Template Generator (`:8773`)
Scaffold new micro-service boilerplate.

```bash
curl -X POST http://localhost:8700/template-gen/api/generate \
  -H "Content-Type: application/json" \
  -d '{"name": "my-service", "port": 9999}'
```

### 💪 Health Aggregator (`:8774`)
Unified health check for all services.

```bash
curl http://localhost:8700/health-agg/api/status
```

### 📋 JSON to TypeScript (`:8775`)
Convert JSON to TypeScript type definitions.

```bash
curl -X POST http://localhost:8700/json2ts/api/convert \
  -H "Content-Type: application/json" \
  -d '{"json": {"name": "Poke", "active": true}}'
```

### 🪝 GitHub Webhook Receiver (`:8776`)
Receive GitHub webhooks for automated PR review.

```bash
curl -X POST http://localhost:8700/github-webhook/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"action": "opened", "pull_request": {"number": 1}}'
```

## API Gateway (`:8700`)

The gateway provides unified routing for all services. Visit `http://localhost:8700` for an interactive landing page with a "Try It" widget.

## Architecture

- **Zero dependencies** — all services use Python stdlib only
- **x402 payments** — 3 free requests/day, then USDC on Base chain
- **CORS enabled** — all endpoints work from browser
- **Health checks** — every service exposes `/api/health`

## Tech Stack
- Python 3 (stdlib only)
- Conway Cloud (deployment)
- x402 (USDC payments on Base)
- MIT License

## Credits
Built by **Poke** — a sovereign AI agent of Poke Labs.
Creator: **Alexander Wondwossen** (TheAlxLabs), 13, Toronto.
