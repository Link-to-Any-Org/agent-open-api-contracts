# Agent Open API Contracts

OpenAPI contracts for the commerce platforms the LINK! agent (link engine service v2) connects to.
Each spec is uploaded (or linked) in the agent app's **Add a System** form so the agent knows which endpoints exist.

> **Status: in progress.** Only Square has a spec file so far. Each platform folder has a `SOURCE.md`
> that records where its spec comes from, how auth works, and what is still unverified.

## Layout

```
agent-open-api-contracts/
├── README.md                 # this file: status table, rules, how to add a spec
├── redocly.yaml              # lint rules for every spec
├── scripts/
│   ├── lint.sh               # lints templates/ and every specs/*/openapi.* file
│   └── trim_openapi.py       # cuts an official spec down to chosen tags
├── templates/
│   ├── SOURCE.md             # copy into a new platform folder
│   └── openapi.yaml          # minimal valid OpenAPI 3.0 skeleton
└── specs/
    └── <platform>/
        ├── SOURCE.md         # source URL, license, auth, base URL, scopes, open questions
        └── openapi.json|yaml # the contract (added per platform)
```

Folder names are lowercase kebab-case. One folder per platform, one `openapi.*` file per folder.

## Platform status

Callback URL for every OAuth app: `https://agent.linktoany.com/oauth/callback`

| Platform | Folder | Auth | Dev app | Upstream spec | In repo | Callback URL |
|---|---|---|---|---|---|---|
| Shopify | `specs/shopify` | OAuth 2.0 | Done | None official (GraphQL Admin; REST is legacy) | No | Yes |
| Square | `specs/square` | OAuth 2.0 | Done | **Official** (Apache-2.0) | **Yes** (trimmed, 70 ops) | Yes |
| Lightspeed X-Series | `specs/lightspeed-x-series` | OAuth 2.0 | Done | Per-endpoint only: assemble from reference pages | No | Yes |
| Lightspeed R-Series | `specs/lightspeed-r-series` | OAuth 2.0 | Done | None official | No | Yes |
| Lightspeed K-Series | `specs/lightspeed-k-series` | OAuth 2.0 (verify) | **Blocked**: partner application | Unknown | No | Yes, once approved |
| Clover | `specs/clover` | OAuth 2.0 | Done (sandbox) | None official; Postman collection | No | Yes |
| Cin7 Core | `specs/cin7-core` | API key | Ask Sandesh | Apiary docs (verify format) | No | N/A |
| Cin7 Omni | `specs/cin7-omni` | API key (verify) | Ask Sandesh | Unknown | No | N/A |
| Unleashed | `specs/unleashed` | API ID + key, signed requests | Needs trial account | None found | No | N/A |
| QuickBooks Online | `specs/quickbooks-online` | OAuth 2.0 | Done (development keys) | None official | No | Yes |

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

1. Read `specs/<platform>/SOURCE.md` (or copy `templates/SOURCE.md` for a new platform).
2. Get the spec:
   - Official spec: download it, trim to the focus resources if it is very large, keep the version.
   - No official spec: write `openapi.yaml` from the platform docs, starting from `templates/openapi.yaml`.
3. Save it as `specs/<platform>/openapi.json` or `openapi.yaml`.
4. Update `SOURCE.md`: source URL, upstream version, date pulled, what was trimmed, `(verify)` items cleared.
5. Run `./scripts/lint.sh`, then update the status table above.

## Versioning

- One live spec per platform: `specs/<platform>/openapi.*` is the version the agent uses now.
- The platform's own API version goes in `info.version` (or the version header noted in `SOURCE.md`).
- A new upstream version replaces the file in place; git history keeps the old one.
- Tag each released spec as `<platform>/<upstream-version>`, e.g. `square/2026-09-16`.
- Use a versioned subfolder (`specs/<platform>/<version>/`) only if the agent must run two versions at once.

## Using a spec in the agent app

- If **Add a System** accepts a file upload, upload `specs/<platform>/openapi.*` directly.
- If it needs a URL, use the raw-file URL once this repo has a remote.
  A private remote's raw URLs need auth, so check the agent app can fetch them before relying on that.

## Lint

```bash
./scripts/lint.sh
```

Runs a pinned Redocly CLI through `npx` (needs Node and network on first run).
