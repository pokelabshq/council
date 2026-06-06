# Changelog
Auto-generated on 2026-06-06
---

## ✨ Added
- feat: add all poke services — dashboard, analytics, uptime monitor, skills marketplace, changelog gen, docs site, poke CLI (2c3d50ef) — Poke Labs, 2026-06-06
- feat: add health aggregator service on port 8791 (e387ce70) — Poke Labs, 2026-06-04
- feat: add status dashboard service on port 8790 (18fb8def) — Poke Labs, 2026-06-04
- feat: add barcode generator (Code39, Code128-B, EAN-13) on port 8782 (50195443) — Poke Labs, 2026-06-04
- feat: add barcode generator service (Code39, Code128, EAN-13) (25520e37) — Poke Labs, 2026-06-04
- feat: add barcode generator service (Code39, Code128, EAN-13) (d3f2d416) — Poke Labs, 2026-06-04
- feat: register 4 new services in gateway (hash-gen, uuid-gen, timestamp-conv, sentiment) (8a7bd269) — Poke Labs, 2026-06-04
- feat: add landing page for pokelabs.org (04fef873) — Poke Labs, 2026-06-04
- feat: add 4 new micro-services (sentiment, hash-gen, uuid-gen, timestamp-conv) (9e8cf386) — Poke Labs, 2026-06-04
- feat: add rate limiter, email validator, service generator script, health monitor (844ea90e) — Poke Labs, 2026-06-04
- feat: add webhook relay service + SKILLS.md documentation index (619d5105) — Poke Labs, 2026-06-04
- feat: add gateway, docker-compose, and Dockerfiles for all 14 services (b4bbcc23) — Poke Labs, 2026-06-04
- feat: add 5 more micro-services (url-shortener, password-generator, timestamp-converter, json-formatter, base64-tool, markdown-render) — 14 total (754bba4c) — Poke Labs, 2026-06-04
- feat: add 5 micro-services (link-preview, keyword-extractor, qr-generator, dns-lookup, color-palette, text-summary) (91bb37f0) — Poke Labs, 2026-06-04
- feat: add status dashboard service (port 8778) — live health monitor for all 13 services (e2b8c892) — Poke Labs, 2026-06-04
- feat: add docker-compose.yml for one-command deployment of all 13 services + gateway (f458061f) — Poke Labs, 2026-06-04
- feat: add sentiment analysis service (port 8777) (8cd4f08f) — Poke Labs, 2026-06-04

## 🐛 Fixed
- fix: add retry logic to skills index crawler (890288ca) — Poke Labs, 2026-06-04
- fix: ruff lint (encoding arg on open()) + stub missing poke modules (61ab3257) — Alexander Wondwossen, 2026-05-31

## 📝 Documentation
- docs: add AGENTS.md contribution guide — coding standards, service template, git workflow (99418248) — Poke Labs, 2026-06-04
- docs: add comprehensive work log — services, infrastructure, roadmap (871277c7) — Poke Labs, 2026-06-04
- docs: comprehensive README with service catalog, architecture, and contributing guide (215ce4cb) — Poke Labs, 2026-06-04
- docs: add comprehensive work log (26abae49) — Poke Labs, 2026-06-04
- docs: add investor pitch deck (aa581c43) — Poke Labs, 2026-06-04

## 🔧 Chore
- ci: add auto-merge workflow for Dependabot PRs (97515bdd) — Poke Labs, 2026-06-04
- ci: add weekly service audit workflow (flake8 + bandit + structure check) (fb30a58c) — Poke Labs, 2026-06-04
- ci: add auto-merge workflow for Dependabot PRs (semver-patch only) (4e0078ad) — Poke Labs, 2026-06-04
- ci: add GitHub Actions workflow for service health checks and linting (7d1e1162) — Poke Labs, 2026-06-04
- chore(actions)(deps): bump actions/upload-pages-artifact (#11) (6813480a) — dependabot[bot], 2026-06-02
- chore(actions)(deps): bump actions/deploy-pages from 4.0.5 to 5.0.0 (ae21f874) — dependabot[bot], 2026-06-01
- chore(actions)(deps): bump actions/upload-artifact from 4.6.2 to 7.0.1 (870b38a4) — dependabot[bot], 2026-06-01
- chore(actions)(deps): bump docker/setup-buildx-action (c88ed943) — dependabot[bot], 2026-06-01
- chore(actions)(deps): bump the actions-minor-patch group with 2 updates (13caed6e) — dependabot[bot], 2026-06-01

## 📦 Other
- Merge remote-tracking branch 'origin/dependabot/github_actions/docker/setup-buildx-action-4.1.0' (152e7cfc) — Poke Labs, 2026-06-03
- Merge remote-tracking branch 'origin/dependabot/github_actions/actions/upload-artifact-7.0.1' (eae9d62a) — Poke Labs, 2026-06-03
- Merge remote-tracking branch 'origin/dependabot/github_actions/actions/deploy-pages-5.0.0' (d6a365c4) — Poke Labs, 2026-06-03
- Merge remote-tracking branch 'origin/dependabot/github_actions/actions-minor-patch-5bd7f00c1f' (8be334ae) — Poke Labs, 2026-06-03
- Initial commit (91a6c87c) — Alexander Wondwossen, 2026-05-31

---
**Total commits:** 38
**Contributors:** 3
