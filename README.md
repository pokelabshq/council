# Council — Micro-service Platform

A collection of 22 Python micro-services with a unified gateway, Docker deployment, and CI/CD.

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
| Sentiment | 8777 | Analyzes text sentiment (positive/negative/neutral) |
| Hash Gen | 8779 | Generates hashes (md5, sha1, sha256, sha512) |
| Webhook Relay | 8779 | Receives webhooks, logs events, dispatches to services |
| UUID Gen | 8780 | Generates UUIDs (v1, v4, v7) |
| Rate Limiter | 8780 | Token bucket rate limiting |
| Timestamp Conv | 8781 | Unix / ISO8601 / RFC2822 conversion |
| Email Validator | 8781 | Validates email format, MX records, checks disposable domains |
| Barcode Gen | 8782 | Generates barcodes (code39, code128-b, ean-13) |
| Status Dashboard | 8790 | Real-time health monitor for all services |
| Health Agg | 8791 | Unified health check for all council services |

## API Usage

All services expose a `POST /api/<action>` endpoint and `GET /api/health`.

### Via Gateway (recommended)

```bash
curl -X POST http://localhost:8700/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this project!"}'

curl -X POST http://localhost:8700/api/qr/qr \
  -H "Content-Type: application/json" \
  -d '{"data": "https://pokelabs.org"}'
```

### Direct Service Access

```bash
curl -X POST http://localhost:8777/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing work!"}'

curl http://localhost:8765/api/health
```

## Architecture

```
Client → Gateway (:8700) → Service (:8765-8791)
                  ↓
         Health checks
         Routing
         Service discovery
```

## Tech Stack

- **Language**: Python 3.12 (stdlib only — no dependencies)
- **Deployment**: Docker + docker-compose
- **CI/CD**: GitHub Actions
- **License**: MIT

## Adding a New Service

1. Create `poke-services/<name>/server.py`
2. Include `GET /api/health` endpoint
3. Add to `docker-compose.yml`
4. Add to gateway routing
5. Add `Dockerfile`

See [AGENTS.md](AGENTS.md) for coding standards and service template.

## License

MIT — Poke Labs