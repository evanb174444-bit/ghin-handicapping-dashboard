# Handicapping and GHIN Dashboard

Static executive dashboard designed for local review over HTTP and publication through GitHub Pages. The approved dashboard is the presentation layer; dashboard-safe processed data and generators remain in this repository while raw source exports stay local.

## Run locally

```bash
./scripts/serve_dashboard.sh
```

Open `http://127.0.0.1:8000/`. Do not validate the modular data-loading flow with `file://`, because browser security rules can block `fetch()` requests.

## Public entry point

- `index.html` redirects to the approved standalone `Handicapping and GHIN Dashboard.html`.
- The standalone dashboard embeds its dashboard data and does not require a backend.
- The earlier modular application in `assets/` reads `data/processed/mock_metrics.json` with `fetch()` and therefore requires HTTP.

## Data and QA

Regenerate deterministic mock data and run checks:

```bash
npm run generate
npm test
```

Raw files are intentionally not published. Dashboard components should consume reviewed, dashboard-safe processed data.

## Repository map

- `index.html` — public dashboard entry point
- `assets/` — presentation and interaction code
- `data/processed/` — dashboard-safe mock records
- `schemas/` — processed-data contract
- `scripts/` — deterministic generator and QA
- `Handicapping and GHIN Dashboard.html` — approved standalone dashboard
- `SOURCE_DATA_DEPENDENCIES.md` — source-data requirements

## Review and deployment workflow

1. Update numbers and generated dashboard-safe data locally.
2. Run `npm test` and serve the dashboard with `./scripts/serve_dashboard.sh`.
3. Review `git status` and `git diff --stat`, then validate the dashboard in a browser at `http://127.0.0.1:8000/`.
4. Commit only reviewed files.
5. Push `main` only after explicit approval to push live.
6. GitHub Pages publishes from the repository root on `main`.

Never commit raw exports, backups, credentials, or sensitive source files. Before every live push, confirm the intended changed files and a clean working tree after the commit.
