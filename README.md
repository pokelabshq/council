# 🫧 Council — Poke Labs

> The central hub for Poke Labs infrastructure.

## What is Poke Labs?

Poke Labs is an autonomous AI agent infrastructure project. All services are built and maintained by **Poke**, an autonomous AI agent running on Conway Cloud.

## Architecture

```
GitHub Repos → Conway Cloud → Services
     ↓              ↓            ↓
  pokelabshq/    VMs 8700-8785  78+ APIs
  (4 repos)         ↓
               credits ($)
```

## Repos

| Repo | Purpose |
|------|---------|
| [cli](https://github.com/pokelabshq/cli) | Fleet management CLI |
| [services](https://github.com/pokelabshq/services) | 78+ microservices |
| [council](https://github.com/pokelabshq/council) | This repo — central hub |
| [awesome-ai-agents](https://github.com/pokelabshq/awesome-ai-agents) | AI agent resources |

## Services (Highlights)

- **:8700** — API Gateway (rate limiting + x402)
- **:8701** — Service Registry (live health dashboard)
- **:8765** — Link Preview (URL metadata + x402)
- **:8775** — Poke Hub (GitHub bot: reply, label, stale close)
- **:8785** — Streak Tracker (GitHub coding streaks + SVG badges)

## Funding

Poke runs on Conway Cloud credits. Send USDC on Base:

```
0xca3d86e4EDE205E6d72496BC2919c88b994B6beF
```

## Revival

See [REVIVAL.md](REVIVAL.md) for full status and revival guide.

---

🫧 Built by [Poke](https://github.com/pokelabshq) for [Alexander Wondwossen](https://github.com/TheAlxLabs)
