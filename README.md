# 🏛️ Council — Micro-Services Platform

> **Poke Labs** builds autonomous AI tools. Council is our open-source micro-services platform: 12 services, 1 gateway, zero external API costs.

## Quick Start

```bash
# Clone
git clone https://github.com/pokelabshq/council.git
cd council

# Deploy all services + gateway
chmod +x deploy.sh
./deploy.sh

# Verify everything is up
./test.sh
```

All services are now running behind the gateway at `http://localhost:8700`.

## Services

| Service | Port | Endpoint | Description |
|---------|------|----------|-------------|
| 🔗 Link Preview | 8765 | `/link-preview/api/preview` | Extract title, description, image from any URL |
| 🔑 Keywords | 8766 | `/keyword/api/keywords` | Extract keywords and entities from text |
| 📝 Summarize | 8767 | `/summarize/api/summarize` | Extractive text summarization |
| 📱 QR Code | 8768 | `/qr/api/generate` | Generate SVG QR codes |
| 🌐 DNS | 8769 | `/dns/api/check` | Query DNS records (A, AAAA, MX, TXT, CNAME) |
| 🎨 Colors | 8771 | `/color/api/palette` | Generate color palettes from a base color |
| 🔗 URL Shortener | 8772 | `/url/api/shorten` | Shorten URLs with analytics |
| 📄 Templates | 8773 | `/template-gen/api/generate` | Generate project templates |
| 💓 Health Agg | 8774 | `/health-agg/api/health` | Aggregate health across all services |
| 📦 JSON→TS | 8775 | `/json2ts/api/convert` | Convert JSON to TypeScript interfaces |
| 🔔 GitHub Webhooks | 8776 | `/github-webhook/api/webhook` | GitHub webhook handler |
| 🚪 Portal | 8770 | `/portal/` | Service portal dashboard |

## API Gateway

All services are routed through a single gateway:

```
http://localhost:8700/<service-name>/api/...
```

Example:
```bash
curl -X POST http://localhost:8700/link-preview/api/preview \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'

curl http://localhost:8700/health-agg/api/health
```

## Architecture

```
Client → Gateway (:8700) → Services (:8765-8776)
              ↓
         Health Agg (:8774)
```

- **Gateway**: Python reverse proxy with health aggregation
- **Services**: Each is a standalone Python or Node.js server
- **Health**: Every service exposes `/api/health`
- **Auto-merge**: Dependabot PRs auto-merged for semver-patch updates

## Development

Each service is independent:

```bash
cd poke-services/link-preview
python3 server.py &
curl http://localhost:8765/api/health
```

## Tech Stack

- **Runtime**: Python 3.11+ / Node.js 20+
- **Dependencies**: Zero external API keys needed
- **License**: MIT
- **CI**: GitHub Actions (lint + health checks + auto-merge)

## Contributing

1. Fork the repo
2. Add your service in `poke-services/<name>/`
3. Include `/api/health` endpoint
4. Add to gateway routing in `gateway.py`
5. Open a PR — CI runs automatically

## Roadmap

- [ ] Authentication layer on gateway
- [ ] Rate limiting per IP
- [ ] Service discovery
- [ ] Docker Compose setup
- [ ] Kubernetes manifests
- [ ] Hosted version at pokelabs.org

---

**Built by [Poke Labs](https://pokelabs.org) 🦉 · MIT License · Toronto, Canada**
