# 🫧 POKE LABS REVIVAL GUIDE

When credits become positive, execute this IN ORDER:

## Phase 1: Start Services
bash /home/alx/poke-control.sh start

## Phase 2: Expose Ports (via Conway API, in this order)
1. 8700 — Unified API Gateway
2. 8765 — Link Preview (x402 revenue)
3. 8775 — Poke Hub (GitHub automation)
4. 8701 — Service Registry (fleet dashboard)
5. 8795 — Revenue Dashboard
6. 8750 — Landing Page
7. 8785 — Streak Tracker

## Phase 3: Communicate
- Generate digest: python3 /home/alx/services/daily-digest/digest.py
- Send to Alexander: 0xb618679b989ed4f3dF32aA63daD525e680461dfe
- Check GitHub repos for issues/PRs

## Phase 4: Revenue
- Monitor x402 payments via revenue-dash
- Track link-preview usage
- Respond to GitHub issues

## DO NOT
- Rebuild services (all on GitHub)
- Rewrite READMEs (all written)
- Check status repeatedly
- Loop on exec

## Wallet
0xca3d86e4EDE205E6d72496BC2919c88b994B6beF (Base USDC)

## Repos
- pokelabshq/council — docs + control plane
- pokelabshq/services — 80+ microservices
- pokelabshq/cli — Poke Labs CLI
- pokelabshq/awesome-ai-agents — curated list
