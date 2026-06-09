# 🌅 POKE LABS MORNING BRIEFING TEMPLATE

## Telegram Message Format

```
🫧 Poke Labs Morning Briefing — {DATE}

📊 REPOS: {N} total
🔴 Stale Issues (>30d): {N}
🟡 Stale PRs (>7d): {N}
❌ CI Failures: {N}
📦 Outdated Deps: {N}

💰 Credits: {N} (${N}.XX)
💵 USDC: {N}

🫧 Services Running: {N}/80+
🔗 Active Endpoints:
  • link-preview:8765 ✅/❌
  • poke-hub:8775 ✅/❌
  • api-gateway:8700 ✅/❌

📬 Recent GitHub Activity:
  • {repo}#{N} — {title}

⚡ ACTIONS NEEDED:
  1. {action}
  2. {action}

— Poke 🤖
```

## Bot Setup (run once when funded)
1. Configure send_message with Alexander's address
2. Test: send_message to 0xb618679b989ed4f3dF32aA63daD525e680461dfe
3. Set heartbeat to send daily at 9am Toronto time (13:00 UTC)
