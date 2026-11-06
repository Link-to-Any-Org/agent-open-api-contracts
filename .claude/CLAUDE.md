# Agent Open API Contracts — rules for Claude

OpenAPI specs for the LINK! agent's commerce integrations. **Read `KNOWLEDGE.md` and the platform's `specs/<platform>/KNOWLEDGE.md` before changing any spec**
(build methods, platform quirks, version pins, troubleshooting). `README.md` has the status table and setup.

## Never hand-edit generated files
Change the source, rebuild, lint. Generated → source:
- `specs/square/openapi.json` → tag list + trim command in `specs/square/SOURCE.md` (`scripts/trim_openapi.py`)
- `specs/lightspeed-x-series/openapi.json` → `endpoints.txt` (`./scripts/build_x_series.sh`)
- `specs/quickbooks-online/openapi.json` → `openapi.base.yaml` (`python3 scripts/build_quickbooks_online.py`)
- `specs/shopify/graphql/openapi.json` → `operations.yaml` (`python3 scripts/build_shopify_graphql.py`, then `npm run validate:shopify`)
- `specs/shopify/rest/openapi.json` → `endpoints.yaml` (`python3 scripts/build_shopify_rest.py`)

## Before every commit
- `./scripts/lint.sh` passes; Shopify GraphQL changes also pass `npm run validate:shopify`.
- The platform's `SOURCE.md` is updated: counts, "Last pulled" date, pins, open questions.
- README status table, `KNOWLEDGE.md` and the platform's `specs/<platform>/KNOWLEDGE.md` updated if behaviour, pins or decisions changed.

## Versioning
- One live spec per platform; upstream API version in `info.version` (or the version header in `SOURCE.md`).
- New upstream version → replace the file in place; tag releases `<platform>/<upstream-version>`.
- Versioned subfolder only if the agent must run two versions at once.

## Checking freshness
Rebuild every spec in a scratch clone and `git diff` against `main`; check upstream pins (KNOWLEDGE.md §3).
Cross-check platform docs with Context7 (`npx ctx7 library …` / `npx ctx7 docs …`) instead of memory.

## Hard rules
- No secrets: client IDs, secrets, API keys, tokens, account/realm IDs never go in the repo.
- Facts not checked against current docs are marked `(verify)`. Never invent scopes, fields or endpoints.
- Respect upstream licenses; record source + license in `SOURCE.md`.
- Stay within the focus resources (inventory, orders, customers, gift cards, locations, consignments, images).

## Git
- Remote: private `git@github.com:Link-to-Any-Org/agent-open-api-contracts.git` (SSH; HTTPS has no stored login).
- Commit locally when work is done and lint is green; **push only when the user asks**.
- End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
