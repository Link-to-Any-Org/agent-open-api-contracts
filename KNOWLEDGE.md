# Knowledge base

Everything learned while building this repo: why each spec is built the way it is, how each platform's
auth and quirks work, what went wrong and how it was fixed, and how to keep the specs current.
`README.md` is the quick start; this file is the background. Per-platform facts live in each
`specs/<platform>/SOURCE.md`; this file links them together.

Last updated: 2026-11-06.

---

## 1. What this repo is for

- The LINK! agent ("link engine service v2") connects to merchants' commerce systems. Each system is added
  in the agent app's **Add a System** form, which takes an OpenAPI spec (or "No spec: I'll add endpoints").
- This repo holds those specs, one per platform, cut down to what the agent needs.
- **Focus resources** (agreed with the team): inventory, orders, customers, gift cards, locations,
  consignments (stock transfers / supplier orders), images. Endpoints outside these are left out on purpose.
- **OAuth callback for every platform:** `https://agent.linktoany.com/oauth/callback`.
- In the agent app, a platform's client secret is never typed into Add a System: an Owner saves a
  **Developer app** in Settings (client ID, secret, token URL), then the system picks it from the
  **OAuth app** dropdown. The dropdown only lists Developer apps whose token URL matches exactly.

## Per-system knowledge

Each platform has its own `KNOWLEDGE.md` next to its `SOURCE.md`: setup, how the spec is built, quirks, inventory tracking, live-testing notes, troubleshooting and open items. Copy `templates/KNOWLEDGE.md` for a new platform.

| Platform | Knowledge file | Status |
|---|---|---|
| Shopify | [`specs/shopify/KNOWLEDGE.md`](specs/shopify/KNOWLEDGE.md) | Spec in repo (GraphQL 27 ops + REST 31 ops) |
| Square | [`specs/square/KNOWLEDGE.md`](specs/square/KNOWLEDGE.md) | Spec in repo (73 ops) |
| Lightspeed X-Series | [`specs/lightspeed-x-series/KNOWLEDGE.md`](specs/lightspeed-x-series/KNOWLEDGE.md) | Spec in repo (71 ops) |
| Lightspeed R-Series | [`specs/lightspeed-r-series/KNOWLEDGE.md`](specs/lightspeed-r-series/KNOWLEDGE.md) | Spec in repo (49 ops), untested against a live store |
| QuickBooks Online | [`specs/quickbooks-online/KNOWLEDGE.md`](specs/quickbooks-online/KNOWLEDGE.md) | Spec in repo (24 ops) |
| Clover | [`specs/clover/KNOWLEDGE.md`](specs/clover/KNOWLEDGE.md) | No spec yet (sandbox dev app done) |
| Lightspeed K-Series | [`specs/lightspeed-k-series/KNOWLEDGE.md`](specs/lightspeed-k-series/KNOWLEDGE.md) | Blocked: partner application |
| Cin7 Core | [`specs/cin7-core/KNOWLEDGE.md`](specs/cin7-core/KNOWLEDGE.md) | Not started |
| Cin7 Omni | [`specs/cin7-omni/KNOWLEDGE.md`](specs/cin7-omni/KNOWLEDGE.md) | Not started |
| Unleashed | [`specs/unleashed/KNOWLEDGE.md`](specs/unleashed/KNOWLEDGE.md) | Not started |

## 2. How each spec is produced

No platform hands us a ready, trimmed, current spec, so each one has its own build. The rule is the same
everywhere: **a generated file is never edited by hand** — change the source, rebuild, lint.

| Platform | Method | Source of truth (edit this) | Rebuild | Extra check | Platform file |
|---|---|---|---|---|---|
| Square | Official spec, trimmed to focus tags | tag list in `specs/square/SOURCE.md` | `scripts/trim_openapi.py …` (command in SOURCE.md) | lint | [`specs/square/KNOWLEDGE.md`](specs/square/KNOWLEDGE.md) |
| Lightspeed X-Series | One OpenAPI fragment per docs page, merged | `specs/lightspeed-x-series/endpoints.txt` | `./scripts/build_x_series.sh` | merge fails on any conflict | [`specs/lightspeed-x-series/KNOWLEDGE.md`](specs/lightspeed-x-series/KNOWLEDGE.md) |
| QuickBooks Online | Hand-written paths + schemas generated from Intuit's XSDs | `specs/quickbooks-online/openapi.base.yaml` | `python3 scripts/build_quickbooks_online.py` | lint | [`specs/quickbooks-online/KNOWLEDGE.md`](specs/quickbooks-online/KNOWLEDGE.md) |
| Shopify GraphQL | Hand-written operations wrapped in one endpoint | `specs/shopify/graphql/operations.yaml` | `python3 scripts/build_shopify_graphql.py` | `npm run validate:shopify` (live schema) | [`specs/shopify/KNOWLEDGE.md`](specs/shopify/KNOWLEDGE.md) |
| Shopify REST | Generated from the markdown REST reference pages | `specs/shopify/rest/endpoints.yaml` | `python3 scripts/build_shopify_rest.py` | lint | [`specs/shopify/KNOWLEDGE.md`](specs/shopify/KNOWLEDGE.md) |

### Why these methods

Per platform: see `specs/<platform>/KNOWLEDGE.md`, section "How the spec is built".

### Known limits of the generated specs

Per platform: see `specs/quickbooks-online/KNOWLEDGE.md` and `specs/shopify/KNOWLEDGE.md`, section "How the spec is built".

- **Vendor lint noise is switched off per file** in `redocly.yaml` (Square, X-Series): their style warnings
  (examples, `$ref` siblings, missing 4xx) are upstream's, not ours. Real errors still fail lint, and
  hand-written specs get the full rule set.

## 3. Versioning and freshness

- One live spec per platform; the platform's API version is in `info.version` (or the header noted in
  `SOURCE.md`). A new upstream version replaces the file in place; git keeps history.
- Tag releases as `<platform>/<upstream-version>` (e.g. `square/2026-09-16`). Use a versioned subfolder
  only if the agent must run two versions at once.

### Pins and current versions (checked 2026-11-02)

| Platform | What we pin | Current upstream | Notes |
|---|---|---|---|
| Square | `connect-api-specification` commit `0689c90`, `Square-Version: 2026-09-16` | same | |
| X-Series | API `2026-10` | `2026-10` latest; `2027-01` announced | 2027-01 adds fulfillment packages (not in our focus) |
| QuickBooks | Java SDK commit `c4d5dfa`, `minorversion=75` | same; 75 is the default | Intuit retired minor versions 1–74 on 2025-08-01 |
| Shopify | Admin API `2026-10` | `2026-10` latest; `2027-01` release candidate | All 27 GraphQL ops also pass against 2027-01 |

### Refresh checklist

1. Rebuild every spec in a scratch clone and diff against `main` — a diff means upstream changed:
   ```bash
   git clone <repo> /tmp/check && cd /tmp/check && npm install
   ./scripts/build_x_series.sh
   python3 scripts/build_quickbooks_online.py
   python3 scripts/build_shopify_graphql.py && npm run validate:shopify
   python3 scripts/build_shopify_rest.py
   # Square: re-download api.json and re-run the trim command from specs/square/SOURCE.md
   git diff --stat
   ```
2. Check for new upstream versions: Square repo commits, Intuit SDK commits (GitHub compare API),
   Shopify `publicApiVersions` (via the docs proxy below), X-Series changelog
   (`https://x-series-api.lightspeedhq.com/llms.txt`).
3. Cross-check behaviour changes in the platform docs with **Context7** (installed on the dev Mac):
   `npx ctx7 library "<platform>" "<topic>"` then `npx ctx7 docs <libraryId> "<question>"`.
   Useful IDs: `/websites/developer_squareup`, `/websites/developer_intuit_app_developer_qbo`,
   `/websites/developer_intuit_app_developer_qbo_api`.
4. Update each touched `SOURCE.md` ("Last pulled", counts, notes), lint, commit.

## 4. Platform knowledge

Per platform: see `specs/<platform>/KNOWLEDGE.md` (Setup and Platform quirks). Platforms not started or blocked have a short status file there too.

## 5. Inventory tracking must be on

The agent only sees stock for items the merchant tracks. Connecting a store does **not** turn tracking on.

Per platform: see `specs/<platform>/KNOWLEDGE.md`, section "Inventory tracking".

## 6. Troubleshooting log

| Symptom | Cause | Fix |
|---|---|---|
| Agent app: OAuth app dropdown shows "None for …" | No Developer app saved with that exact token URL | Owner saves the Developer app in Settings, token URL must match |

## 7. Related systems

- **LinkOps** (`flowOps/stdout`, linkops.shoppinpal.com): job runner that migrates POS data (mainly from
  Wisen) into Lightspeed R-Series, X-Series and Shopify. Its jobs define what we actually help migrate:
  - R-Series: sales (incl. open and on-account), customers, items, suppliers/vendors, orders, purchase orders,
    gift cards, inventory updates, post-migration entity updates.
  - X-Series: products and images, customers, sales (read/create/void), suppliers, consignment products.
  - OAuth config: `web/src/utils/oauth.js`; per-system jobs: `web/src/config/systems/*.config.js`.

## 8. Tooling

- **Python 3** for the build scripts (stdlib `json`, `xml.etree`, `re`, `subprocess`) plus **PyYAML**
  (`python3 -m pip install pyyaml`) for the QBO and Shopify builds.
- **Node** for lint (`npx @redocly/cli@2.63.0`, pinned in `scripts/lint.sh`) and Shopify validation
  (`graphql@16.9.0` in `package.json`; run `npm install` once).
- Why two languages: Python suited the data reshaping and XSD parsing with no setup on macOS; Node is needed
  for `graphql-js`, the reference GraphQL validator. Moving everything to Node is possible (adds a YAML and an
  XML parser dependency) if the team prefers one toolchain.
- **Remote:** private GitHub `Link-to-Any-Org/agent-open-api-contracts`, pushed over SSH.

## 9. Open items

- Try each spec against its sandbox/test store (none tested end-to-end yet).
- Per-platform open items: see `specs/<platform>/KNOWLEDGE.md`, section "Open items".
- Decide whether the agent app takes file uploads or needs raw URLs (private repo raw URLs need auth).
