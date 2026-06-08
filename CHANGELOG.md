# changelog

all notable changes to this project.

format based on [keep a changelog](https://keepachangelog.com/en/1.1.0/).
project adheres to [semantic versioning](https://semver.org/).

## [unreleased]

### added
- add all poke labs services (5e64973) — 2026-06-06
- add all poke services — dashboard, analytics, uptime monitor, skills marketplace, changelog gen, docs site, poke cli (9ba39fa) — 2026-06-06
- add skills directory ci — auto-generates html index from skill.md files, publishes to github pages (f5de847) — 2026-06-05
- add skills marketplace v1 — searchable catalog, install api, web ui (9ea5c70) — 2026-06-05
- add daily briefing generator — github health, service status, credits (819c71c) — 2026-06-05
- add barcode generator on port 8782 (5019544) — 2026-06-04
- register 4 new services in gateway (8a7bd26) — 2026-06-04
- add webhook relay service + skills.md documentation index (619d510) — 2026-06-04
- add gateway, docker-compose, and dockerfiles for all 14 services (b4bbcc2) — 2026-06-04
- add 5 more micro-services — 14 total (754bba4) — 2026-06-04
- add 5 micro-services (91bb37f) — 2026-06-04
- add status dashboard service — live health monitor for all 13 services (e2b8c89) — 2026-06-04
- add docker-compose.yml for one-command deployment of all 13 services + gateway (f458061) — 2026-06-04
- add rate limiter, email validator, service generator script, health monitor (844ea90) — 2026-06-04
- add 4 new micro-services: sentiment, hash-gen, uuid-gen, timestamp-conv (9e8cf38) — 2026-06-04
- add landing page for pokelabs.org (04fef87) — 2026-06-04
- add health aggregator service on port 8791 (e387ce7) — 2026-06-04

### fixed
- auto-deploy site when skills-index.json changes (22e30f1) — 2026-06-06
- generate skills-index.json to resolve watchdog issue (c44f588) — 2026-06-05
- repair markdown-render server (0f3106a) — 2026-06-04
- trigger deploy on skill changes + commit index to repo (bc045a6) — 2026-06-04
- make auto-merge resilient to missing metadata (41fe287) — 2026-06-04
- add retry logic to skills index crawler (890288c) — 2026-06-04
- recover skills index from cache when sources fail (5d14914) — 2026-06-04
- add retry with exponential backoff to _guarded_http_get (75a5a25) — 2026-06-04

### docs
- add og image generator and seo checker guides (0ec6a77) — 2026-06-06
- add link preview api section with pricing and quick start (254f97f) — 2026-06-06
- announce link preview api with pricing tiers and usage examples (ee8c82c) — 2026-06-06
- add contributing.md with known ci issues and dev setup (b06c5bc) — 2026-06-05
- add agents.md contribution guide — coding standards, service template, git workflow (9941824) — 2026-06-04
- add comprehensive work log — services, infrastructure, roadmap (871277c) — 2026-06-04

### ci
- add github actions ci workflow for automated testing (a6fb3d4) — 2026-06-05
- add auto-merge workflow for dependabot patch prs (d73d55e) — 2026-06-05
- add weekly service audit workflow (fb30a58) — 2026-06-04
- add auto-merge workflow for dependabot prs (97515bd) — 2026-06-04

### changed
- rebrand: pokelabs council — full rebrand from hermes agent (a2e7c96) — 2026-06-04
