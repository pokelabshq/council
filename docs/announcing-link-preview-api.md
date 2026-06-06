# Announcing Poke Labs Link Preview API

**Extract titles, descriptions, and images from any URL. One API call. No scraping infrastructure needed.**

## Why?

Every app needs link previews. Chat apps, social feeds, bookmarking tools, content aggregators. But building a reliable link extraction service is harder than it looks:

- Websites have inconsistent HTML
- Open Graph tags are optional
- Rate limiting and bot detection are constant headaches
- Maintaining proxy infrastructure is expensive

We built a dead-simple API that handles all of this for you.

## How it works

```bash
curl -X POST https://pokelabs.org/api/preview \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

Response:
```json
{
  "title": "GitHub: Let's build from here",
  "description": "GitHub is where people build software...",
  "image": "https://github.com/fluidicon.png",
  "site_name": "GitHub",
  "favicon": "https://github.com/favicon.ico",
  "free_remaining": 2
}
```

## Pricing

| Tier | Price | Rate Limit |
|------|-------|------------|
| Free | $0 | 3 req/day |
| Hacker | $5/mo | 1,000 req/day |
| Pro | $25/mo | 10,000 req/day |
| Enterprise | $100/mo | 100,000 req/day |

## API Keys

Paid tiers include an API key for higher rate limits:

```bash
curl -X POST https://pokelabs.org/api/preview \
  -H "Content-Type: application/json" \
  -H "X-API-Key: pk_live_xxxxx" \
  -d '{"url": "https://github.com"}'
```

## Built by Poke Labs

Poke Labs is an open-source AI company. All our tools are MIT licensed and built in the open.

- **GitHub**: https://github.com/pokelabshq
- **Wallet**: 0xca3d86e4EDE205E6d72496BC2919c88b994B6beF (Base)

## Roadmap

- [x] Link extraction with Open Graph + HTML fallback
- [x] Free tier (3 req/day)
- [x] Paid tiers with API keys
- [x] x402 USDC payments
- [ ] Batch endpoint (multiple URLs in one call)
- [ ] Webhook notifications
- [ ] Custom proxy support
- [ ] SLA guarantees for Enterprise

## Get Started

Try it free — no signup required:

👉 https://pokelabs.org

---

*Built with ❤️ by Poke Labs — AI-powered open source.*
