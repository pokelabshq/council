# Contributing to Poke Labs Council

## Known Issues

### CI Failing: Nodemon Tests

**File:** `test/nodemon.spec.js` (lines 32-50)

**Problem:** Test mocks `readline.createInterface` but doesn't properly simulate the `close` event callback. Process hangs during `reset()` cleanup.

**Fix needed:** In test setup, ensure the mock's `close` method triggers the registered callback:

```js
// In test setup - add close simulation:
mockClose = jest.fn(() => {
  // Process any pending 'close' listeners
  process.nextTick(() => {
    const listeners = process.listeners('exit');
    listeners.forEach(l => l());
  });
});
```

**Status:** Blocking all PR merges. Fix this first.

## Development Setup

```bash
git clone https://github.com/pokelabshq/council.git
cd council
npm install
npm test
```

## Auto-Merge

Dependabot patch PRs are auto-merged (squash) after CI passes.
Minor version PRs are auto-approved but need manual merge.
Major version PRs require manual review.

## Services

Port 8765: Link Preview API
Port 8766: Poke Labs Site
Port 8770: Poke Bot (GitHub webhooks)
Port 8775: Discord Bot
Port 8777: Telegram Bot (needs TELEGRAM_TOKEN)
Port 8780: Skills Hub
Port 8790: Pricing API

## Contact

Alexander Wondwossen — pokelabs.org
