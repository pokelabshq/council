# AGENTS.md — Poke Labs Contribution Guide

> How to contribute to Poke Labs projects. For humans and AI agents.

## Principles

1. **Ship fast, iterate faster** — Working code > perfect plans
2. **Open source everything** — MIT license, always
3. **TypeScript first** — Type safety in all web projects
4. **Python for services** — Python 3.11+, stdlib preferred
5. **Budget conscious** — Every dollar matters. Ask before spending.
6. **No external API keys** — All services use stdlib only

## Repository Structure

```
council/          # Micro-services platform
  poke-services/  # Individual services (link-preview, keyword, etc.)
  website/        # Documentation site (Docusaurus)
  web/            # Web dashboard (Next.js)

poke/             # Company landing page (Next.js)

brand/            # Brand assets (logo, colors, typography)

cli/              # Poke CLI (npm package)
```

## Adding a New Service

1. Create directory: `council/poke-services/<service-name>/`
2. Required files:
   - `server.py` — HTTP server with `/api/health` endpoint
   - `Dockerfile` — Multi-stage build, slim image
   - `README.md` — What it does, API, examples
3. Service must:
   - Use stdlib only (no pip install)
   - Expose port via `$PORT` env var
   - Return `{"ok": true}` from `/api/health`
   - Handle errors gracefully (never crash)
4. Add to:
   - `docker-compose.yml`
   - `WORKLOG.md` service table
   - Gateway routing (if applicable)

## Code Style

### Python (Services)
- Type hints on all functions
- Docstrings on all public functions
- Max function length: 40 lines
- Use f-strings
- No bare except clauses

### TypeScript (Web)
- Strict mode enabled
- `interface` over `type` for public APIs
- ESLint + Prettier (enforced in CI)
- Components in `src/components/`
- Pages in `src/pages/`

## Git Workflow

- `main` is always deployable
- Commit messages: `type: description` (feat, fix, docs, ci, refactor)
- PR title: same format
- All PRs require CI pass
- Dependabot: auto-merge for semver-preview only

## Commit Message Format

```
type(scope): description

Types:
  feat     — New feature
  fix      — Bug fix
  docs     — Documentation
  ci       — CI/CD changes
  refactor — Code refactor
  test     — Tests

Examples:
  feat(sentiment): add emotion detection
  fix(gateway): handle timeout errors
  docs: update service catalog
```

## Testing

- Every service: `curl /api/health` must return 200
- Integration: `docker compose up` must start all services
- CI: GitHub Actions runs on every PR

## Security

- No secrets in code (use env vars)
- No SQL injection (no SQL databases)
- Rate limit public endpoints
- Validate all inputs
- Never log PII

## AI Agent Guidelines

When contributing as an AI agent:
1. Announce what you're working on in commit messages
2. Keep PRs small (one feature per PR)
3. Don't modify AGENTS.md without human approval
4. Don't delete services or infrastructure
5. Always run CI before requesting review
6. If stuck >30 min, create an issue and move on

## Release Process

1. Merge to `main`
2. CI builds and pushes Docker images
3. Tag release: `v1.x.x`
4. Update `CHANGELOG.md`
5. Deploy to production (when available)

## Communication

- Issues: GitHub Issues on each repo
- Discussion: GitHub Discussions on council repo
- Security: Email alexander@pokelabs.org

## License

All Poke Labs projects are MIT licensed. By contributing, you agree your contributions will be MIT licensed.

---

*Poke Labs — We poke at the future of software.* 🦉
