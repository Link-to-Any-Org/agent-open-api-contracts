# Agent Open API Contracts

OpenAPI contracts for the commerce platforms the LINK! agent (link engine service v2) connects to.
Each spec is uploaded (or linked) in the agent app's **Add a System** form so the agent knows which endpoints exist.

> **Status: in progress.** Shopify, Square, Lightspeed X-Series, Lightspeed R-Series and QuickBooks Online have spec files so far. Each platform folder has a `SOURCE.md`
> that records where its spec comes from, how auth works, and what is still unverified.
>
> **Background, decisions, platform quirks and troubleshooting:** see [`KNOWLEDGE.md`](KNOWLEDGE.md) for cross-platform content and
> each platform's own `specs/<platform>/KNOWLEDGE.md`.

## Layout

```
agent-open-api-contracts/
├── README.md                 # this file: status table, rules, how to add a spec
├── KNOWLEDGE.md              # cross-platform: why specs are built this way, versioning, refresh checklist, index of per-platform files
├── package.json              # `npm run lint`, `npm run validate:shopify` (installs graphql)
├── redocly.yaml              # lint rules for every spec
├── scripts/
│   ├── lint.sh               # lints templates/ and every specs/*/openapi.* file
│   ├── trim_openapi.py       # cuts an official spec down to chosen tags
│   ├── merge_openapi.py      # joins per-endpoint specs into one (fails on conflicts)
│   ├── build_x_series.sh     # re-downloads + merges the X-Series spec
│   ├── build_quickbooks_online.py  # QBO: base paths + schemas from Intuit XSDs
│   ├── build_shopify_graphql.py    # Shopify GraphQL: operations.yaml -> openapi.json
│   ├── validate_shopify_graphql.mjs # checks every Shopify operation against the live schema
│   └── build_shopify_rest.py       # Shopify REST: built from the REST reference pages
├── templates/
│   ├── SOURCE.md             # copy into a new platform folder
│   ├── KNOWLEDGE.md          # copy into a new platform folder
│   └── openapi.yaml          # minimal valid OpenAPI 3.0 skeleton
└── specs/
    └── <platform>/
        ├── SOURCE.md         # source URL, license, auth, base URL, scopes, open questions
        ├── KNOWLEDGE.md      # setup, build method, quirks, inventory tracking, troubleshooting, open items
        └── openapi.json|yaml # the contract (Shopify has graphql/ and rest/ subfolders)
```

Folder names are lowercase kebab-case. One folder per platform, one `openapi.*` file per folder.

## Platform status

Callback URL for every OAuth app: `https://agent.linktoany.com/oauth/callback`

| Platform | Folder | Auth | Dev app | Upstream spec | In repo | Callback URL |
|---|---|---|---|---|---|---|
| Shopify | `specs/shopify` | OAuth 2.0 | Done | None; GraphQL checked against live schema, REST built from docs | **Yes** (GraphQL 27 ops + REST 31 ops) | Yes |
| Square | `specs/square` | OAuth 2.0 | Done | **Official** (Apache-2.0) | **Yes** (trimmed, 73 ops) | Yes |
| Lightspeed X-Series | `specs/lightspeed-x-series` | OAuth 2.0 | Done | Per-endpoint only (Apache-2.0): merged | **Yes** (71 ops) | Yes |
| Lightspeed R-Series | `specs/lightspeed-r-series` | OAuth 2.0 | Done | None; written from docs via Context7 | **Yes** (49 ops) | Yes |
| Lightspeed K-Series | `specs/lightspeed-k-series` | OAuth 2.0 (verify) | **Blocked**: partner application | Unknown | No | Yes, once approved |
| Clover | `specs/clover` | OAuth 2.0 | Done (sandbox) | None official; Postman collection | No | Yes |
| Cin7 Core | `specs/cin7-core` | API key | Ask Sandesh | Apiary docs (verify format) | No | N/A |
| Cin7 Omni | `specs/cin7-omni` | API key (verify) | Ask Sandesh | Unknown | No | N/A |
| Unleashed | `specs/unleashed` | API ID + key, signed requests | Needs trial account | None found | No | N/A |
| QuickBooks Online | `specs/quickbooks-online` | OAuth 2.0 | Done (development keys) | None; schemas from Intuit's official XSDs | **Yes** (24 ops) | Yes |

Focus resources for every platform: **inventory, orders, customers, gift cards, locations, consignments, images.**
A spec only needs the endpoints for these, not the whole upstream API.

## Rules

1. **No secrets, ever.** Client IDs, client secrets, API keys, tokens, account IDs and test-store keys
   go in the password manager, not in this repo (not in `SOURCE.md`, not in examples).
   The callback URL and public base URLs are fine to commit.
2. **Respect upstream licenses.** Copy an upstream spec only when its license allows it, and record the
   license and source URL in that folder's `SOURCE.md`. Specs written from docs are our own work.
3. **No unverified fact stated as fact.** Anything not checked against the platform's current docs
   is marked `(verify)` in `SOURCE.md` until someone checks it.
4. **Lint before commit:** `./scripts/lint.sh` must pass.

## Add or update a spec

1. Read `specs/<platform>/SOURCE.md` and `specs/<platform>/KNOWLEDGE.md` (or copy `templates/SOURCE.md` and `templates/KNOWLEDGE.md` for a new platform).
2. Get the spec:
   - Official spec: download it, trim to the focus resources if it is very large, keep the version.
   - No official spec: write `openapi.yaml` from the platform docs, starting from `templates/openapi.yaml`.
3. Save it as `specs/<platform>/openapi.json` or `openapi.yaml`.
4. Update `SOURCE.md`: source URL, upstream version, date pulled, what was trimmed, `(verify)` items cleared.
5. Create or update `specs/<platform>/KNOWLEDGE.md` (quirks, troubleshooting, open items) and the platform table in the global `KNOWLEDGE.md`.
6. Run `./scripts/lint.sh`, then update the status table above.

## Versioning

- One live spec per platform: `specs/<platform>/openapi.*` is the version the agent uses now.
- The platform's own API version goes in `info.version` (or the version header noted in `SOURCE.md`).
- A new upstream version replaces the file in place; git history keeps the old one.
- Tag each released spec as `<platform>/<upstream-version>`, e.g. `square/2026-09-16`.
- Use a versioned subfolder (`specs/<platform>/<version>/`) only if the agent must run two versions at once.

## Using a spec in the agent app

- If **Add a System** accepts a file upload, upload `specs/<platform>/openapi.*` directly.
- If it needs a URL, use the file's raw URL on GitHub (`Link-to-Any-Org/agent-open-api-contracts`).
  The repo is private, so raw URLs need auth; check the agent app can fetch them before relying on that.

## Setup

Needs Python 3 and Node. Run once per machine:

```bash
python3 -m pip install pyyaml   # used by the QuickBooks and Shopify build scripts
npm install                     # installs graphql for npm run validate:shopify
```

## Lint

```bash
./scripts/lint.sh
```

Runs a pinned Redocly CLI through `npx` (needs Node and network on first run).
Shopify GraphQL operations also need `npm install` once, then `npm run validate:shopify`.
