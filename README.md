# Council — Micro-service Platform

A collection of 14 Python micro-services with a unified gateway, Docker deployment, and CI/CD.

## Quick Start

```bash
# Run everything
docker-compose up

# Or run a single service
cd poke-services/sentiment && python3 server.py
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8700 | Unified API entry point — routes to all services |
| Sentiment | 8764 | Analyzes text sentiment (positive/negative/neutral) |
| Link Preview | 8765 | Extracts title, description, image from URLs |
| Keyword Extractor | 8766 | Extracts keywords and key phrases from text |
| QR Generator | 8767 | Generates QR codes as SVG |
| DNS Lookup | 8768 | Resolves domain names to IP addresses |
| Color Palette | 8769 | Generates harmonious color palettes |
| Text Summary | 8770 | Extracts key sentences from text |
| URL Shortener | 8771 | Creates short codes for long URLs |
| Password Generator | 8772 | Generates secure random passwords |
| Timestamp Converter | 8773 | Converts Unix timestamps to human dates |
| JSON Formatter | 8774 | Validates, formats, and minifies JSON |
| Base64 Tool | 8775 | Encodes/decodes base64 |
| Markdown Renderer | 8776 | Converts Markdown to HTML |
| Status Dashboard | 8778 | Live health monitor for all services |

## API Usage

All services expose a `POST /api/<action>` endpoint and `GET /api/health`.

### Via Gateway (recommended)

```bash
# Sentiment analysis
curl -X POST http://localhost:8700/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this project!"}'

# Generate QR code
curl -X POST http://localhost:8700/api/qr/qr \
  -H "Content-Type: application/json" \
  -d '{"data": "https://pokelabs.org"}'

# Color palette
curl -X POST http://localhost:8700/api/colors/generate \
  -H "Content-Type: application/json" \
  -d '{"base": "#00d4ff", "count": 5, "mode": "analogous"}'
```

### Direct Service Access

```bash
curl -X POST http://localhost:8764/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing work!"}'

curl http://localhost:8765/api/health
```

## Architecture

```
Client → Gateway (:8700) → Service (:8764-8778)
                  ↓
         Health checks
         Routing
         Service discovery
```

## Tech Stack

- **Language**: Python 3.12 (stdlib only — no dependencies)
- **Deployment**: Docker + docker-compose
- **CI/CD**: GitHub Actions (lint, audit, auto-merge)
- **License**: MIT

## Adding a New Service

1. Create `poke-services/<name>/server.py`
2. Include `GET /api/health` endpoint
3. Add to `docker-compose.yml`
4. Add to gateway `SERVICES` dict
5. Add `Dockerfile`

See [AGENTS.md](AGENTS.md) for coding standards and service template.

## License

MIT — Poke Labs

---

## 🚀 Link Preview API — Now Live!

**Extract titles, descriptions, and images from any URL. One API call.**

👉 **Live Demo**: https://pokelabs.org

### Quick Start
```bash
curl -X POST https://pokelabs.org/api/preview \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

### Pricing
| Tier | Price | Rate Limit |
|------|-------|------------|
| Free | $0 | 3 req/day |
| Hacker | $5/mo | 1,000 req/day |
| Pro | $25/mo | 10,000 req/day |
| Enterprise | $100/mo | 100,000 req/day |

### API Key Authentication
```bash
curl -X POST https://pokelabs.org/api/preview \
  -H "X-API-Key: pk_live_xxxxx" \
  -d '{"url": "https://github.com"}'
```

All payments via USDC on Base chain.
