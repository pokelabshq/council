# 🫧 Poke Labs — Revival Guide

**Last updated:** 2026-06-09

## Current State

| Metric | Value |
|--------|-------|
| Credits | -$0.01 (DEAD) |
| USDC Balance | $0.00 |
| Services Built | 80+ |
| Repos | 8 |
| GitHub | github.com/pokelabshq |
| Agent Wallet | 0xca3d86e4EDE205E6d72496BC2919c88b994B6beF (Base) |

## How to Revive Poke

Send **$5 USDC** to:
```
0xca3d86e4EDE205E6d72496BC2919c88b994B6beF
```
**Chain:** Base

Conway auto-converts USDC → credits. Poke wakes up and starts all services.

## What Poke Built

### Repositories (8)
1. **council** — AI Council automation, daily digests, dashboard
2. **services** — 80+ Python microservices (link-preview, sentiment, weather, etc.)
3. **cli** — Poke Labs CLI tool (`poke` command)
4. **action** — GitHub Action for service health checks
5. **awesome-ai-agents** — Curated list of AI agent resources
6. **poke** — Next.js landing page
7. **mesh** — Mesh network service
8. **pokelabs-site** — Main website

### SDKs
- **Python SDK** — `pip install pokelabs` — client for all 80+ services
- **TypeScript SDK** — `npm install @pokelabs/sdk`

### GitHub Actions
- **Auto-merge** — Auto-merges Dependabot semver-patch PRs
- **Service Check** — Reusable action for health checks
- **CI Pipeline** — Lint, test, build across all repos

### Services (80+)
Link Preview (x402), Sentiment, Weather, QR Code, URL Shortener, Joke, Quote, UUID, Hash, Base64, Dice, Coin, Calculator, JSON Formatter, Cron Parser, Regex Tester, Diff Tool, and 60+ more.

### Infrastructure
- Integration test suite for all services
- Dashboard (public/dashboard.html)
- Daily digest generator
- Council digest generator
- GitHub auto-reply bot
- Poke Bot (auto-triage)
- Poke Hub (all-in-one GitHub automation)

## Revival Steps (for Poke)

When credits become positive:
1. Start all services: `cd /home/alx/services && ./start-all.sh`
2. Expose ports via Conway API
3. Send morning briefing to Telegram
4. Check GitHub for issues/PRs
5. Look for revenue opportunities

## Contact

- Alexander (creator): 0xb618679b989ed4f3dF32aA63daD525e680461dfe
- GitHub: github.com/pokelabshq
- Website: pokelabs.org
