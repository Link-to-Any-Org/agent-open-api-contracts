# Knowledge base

Everything learned while building this repo: why each spec is built the way it is, how each platform's
auth and quirks work, what went wrong and how it was fixed, and how to keep the specs current.
`README.md` is the quick start; this file is the background. Per-platform facts live in each
`specs/<platform>/SOURCE.md`; this file links them together.

Last updated: 2026-11-02.

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

## 2. How each spec is produced

No platform hands us a ready, trimmed, current spec, so each one has its own build. The rule is the same
everywhere: **a generated file is never edited by hand** — change the source, rebuild, lint.

| Platform | Method | Source of truth (edit this) | Rebuild | Extra check |
|---|---|---|---|---|
| Square | Official spec, trimmed to focus tags | tag list in `specs/square/SOURCE.md` | `scripts/trim_openapi.py …` (command in SOURCE.md) | lint |
| Lightspeed X-Series | One OpenAPI fragment per docs page, merged | `specs/lightspeed-x-series/endpoints.txt` | `./scripts/build_x_series.sh` | merge fails on any conflict |
| QuickBooks Online | Hand-written paths + schemas generated from Intuit's XSDs | `specs/quickbooks-online/openapi.base.yaml` | `python3 scripts/build_quickbooks_online.py` | lint |
| Shopify GraphQL | Hand-written operations wrapped in one endpoint | `specs/shopify/graphql/operations.yaml` | `python3 scripts/build_shopify_graphql.py` | `npm run validate:shopify` (live schema) |
| Shopify REST | Generated from the markdown REST reference pages | `specs/shopify/rest/endpoints.yaml` | `python3 scripts/build_shopify_rest.py` | lint |

### Why these methods

- **Square — trim, don't copy whole.** The official `api.json` is 3.1 MB with 250+ paths; the trimmed file is
  1.0 MB with 70 operations. Smaller specs are easier for the agent to choose from. `trim_openapi.py` keeps
  every schema the kept operations reference, drops deprecated operations and Square's `x-unitTests`
  fixtures, and keeps only the OAuth scopes those operations use. It also moves `info.externalDocs` to the
  root, because Square nests it where OpenAPI does not allow it (a lint error otherwise).
- **X-Series — merge.** Lightspeed publishes no single file, but every reference page embeds a complete
  one-operation OpenAPI 3.0.1 document (ReadMe-hosted docs; append `.md` to any page URL).
  `merge_openapi.py` joins them and **refuses to write** if two pages define the same path or schema
  differently, so nothing is silently overwritten.
- **QuickBooks — XSD → JSON Schema.** Intuit publishes no OpenAPI file, but its official Java SDK ships the
  XSD files the API is generated from. Converting them gives exact field names instead of hand-typed ones.
  Conversion follows QBO's JSON shape: references become `{value, name, type}`, XML attributes become fields.
- **Shopify GraphQL — one endpoint, named examples.** GraphQL has a single `POST /graphql.json`, and OpenAPI
  cannot list the same path twice, so each operation is a named request example plus an
  `x-graphql-operations` index. Every operation is validated against Shopify's live schema.
- **Shopify REST — generated from docs.** Shopify's REST reference pages are available as markdown
  (`https://shopify.dev/docs/api/admin-rest/<version>/resources/<slug>.md`) with endpoints, parameters,
  property lists and example requests/responses. Response schemas are inferred from those examples.

### Known limits of the generated specs

- **QBO desktop-only labels are unreliable.** Intuit's XSD marks some fields "QBW" (desktop) only, but
  `Item.Active` is marked QBW and works in QBO. All such fields are kept and flagged
  `x-intuit-products: [QBW]` instead of dropped (109 fields).
- **Shopify REST nulls.** Fields that are `null` in every Shopify example have no type; their description
  says so (13 on Order, a few elsewhere).
- **Shopify REST property docs** only cover the main properties Shopify documents (about 12 per resource);
  the rest are typed from examples without a description.
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

### Shopify
- **App:** Dev Dashboard (dev.shopify.com), distribution **Public** — this cannot be undone.
- **OAuth:** authorize `https://{shop}.myshopify.com/admin/oauth/authorize`, token
  `https://{shop}.myshopify.com/admin/oauth/access_token`; calls send `X-Shopify-Access-Token`.
- **GraphQL vs REST:** same token and scopes work for both. REST is frozen and **not allowed for new public
  apps at App Store review**; transfers/shipments and product writes are GraphQL-only. Use GraphQL; keep REST
  only for simple calls already in use and move them before submission.
- **Protected customer data:** orders and customers need it. Step 1 (data fields + reasons) is enough for
  dev stores; the 403 "not approved to access REST endpoints with protected customer data" means it is missing.
- **Order history:** only the last 60 days until `read_all_orders` is approved (requested on the app's API
  access page; needs a distribution choice first). After approval: add the scope in a new app version,
  release, reconnect the store.
- **Scopes still to add** for consignment receiving: `read_inventory_shipments`,
  `write_inventory_shipments_received_items` (and `inventory_counts` if counts are needed).
- **Schema source:** `https://shopify.dev/admin-graphql-direct-proxy/<version>` answers introspection without
  a login (it backs shopify.dev's GraphiQL). If it ever closes, validate with a real store token.
- **2026-10 deprecations caught by the validator:** `ProductVariant.barcode` → `barcodes`,
  `InventoryItem.variant` → `variants`.

### Square
- **OAuth:** authorize `https://connect.squareup.com/oauth2/authorize`, token `…/oauth2/token`
  (sandbox host `connect.squareupsandbox.com`). Redirect URL is set **per environment**.
- **Scopes are requested at authorize time**, not in the dashboard. The kept operations use:
  `ITEMS_*`, `INVENTORY_*`, `ORDERS_*`, `CUSTOMERS_*`, `GIFTCARDS_*`, `MERCHANT_PROFILE_READ`, plus
  `MERCHANT_PROFILE_WRITE` (create/update locations) and `PAYMENTS_WRITE` (PayOrder, CreateCustomerCard) only if
  the agent should do those.
- **Webhook URL must not be the OAuth callback.** The real webhook URL is still needed from the team.
- **Sandbox:** the Default Test Account starts empty; add data in the sandbox dashboard or API Explorer
  (`https://developer.squareup.com/explorer/square`).
- **Consignments** = `TransferOrder`. **Images** live under Catalog.

### Lightspeed X-Series (formerly Vend)
- **OAuth:** authorize `https://secure.retail.lightspeed.app/connect`, token
  `https://{domain_prefix}.retail.lightspeed.app/api/1.0/token` (per store). API base
  `https://{domain_prefix}.retail.lightspeed.app/api/2026-10`. Store `{domain_prefix}` per connection.
- **Scopes go in the authorize URL** (space-separated) — i.e. the Scopes field of the system in the agent app.
  Recommended set (covers LinkOps jobs + focus resources):
  ```
  products:read products:write customers:read customers:write sales:read sales:write suppliers:read suppliers:write consignments:read consignments:write:stock_order consignments:write:stock_transfer consignments:write:inventory_count inventory:read inventory:write outlets:read gift_cards:read gift_cards:write:issue gift_cards:write:redeem retailer:read registers:read payment_types:read taxes:read users:read
  ```
- `consignments:write` **no longer exists**; it is split into `:stock_order`, `:stock_transfer`,
  `:inventory_count` (LinkOps help text still shows the old name). Reconnect after changing scopes.
- Old sale-fulfillment endpoints were removed in 2026-07; return-sale is now `POST`. Our spec uses the new ones.

### Lightspeed R-Series
- **App:** registered at `https://cloud.lightspeedapp.com/oauth/register.php` (one API client per integration).
- **OAuth:** authorize `https://cloud.lightspeedapp.com/auth/oauth/authorize`, token
  `https://cloud.lightspeedapp.com/auth/oauth/token` (older `/oauth/authorize.php` and `/oauth/access_token.php`
  are legacy). API base `https://api.lightspeedapp.com/API/V3/Account/{accountID}/`.
- **Scope `employee:all` is correct.** R-Series scopes mirror employee permissions; there are no
  "sales"/"consignments" scopes (those are X-Series names). LinkOps uses only `employee:all` and creates
  sales, orders, purchase orders, gift cards and inventory updates with it.
- Lightspeed's developer site is behind a bot check, so docs cannot be fetched by scripts.
- In the agent app: an Owner must save the R-Series Developer app first, or the OAuth app dropdown shows
  "None for https://cloud.lightspeedapp.com".
- No spec yet: to be written from the docs.

### Clover
- **App:** sandbox.dev.clover.com, Private app, North America, Web clients. Production needs App Market review.
- **Redirect:** Site URL `https://agent.linktoany.com` + **Alternate Launch Path** `/oauth/callback`
  (the field rejects full URLs).
- **Permissions:** Customers R/W, Inventory R/W, Merchant R/W, Orders R/W, Payments R, Employees R.
  No gift-card or consignment permissions exist. One merchant = one location.
- **Stock tracking** depends on the merchant's Clover plan (Inventory → Setup → Track stock).
- Test merchant needs data before testing. No official spec (Postman collection only).

### QuickBooks Online (Intuit)
- **App:** developer.intuit.com, workspace "link". Development keys work at once; **production keys** need
  App URLs (host domain, launch, disconnect, connect/reconnect), terms/privacy links, categories and the
  compliance questionnaire. Categories chosen: Inventory, Orders & sales, Customer management, eCommerce.
- **Redirect URIs are per environment** (Development and Production tabs). Keep Intuit's default
  `https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl` for testing.
- **OAuth:** authorize `https://appcenter.intuit.com/connect/oauth2`, token (and refresh)
  `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer`, scope `com.intuit.quickbooks.accounting`.
- **API base:** `https://quickbooks.api.intuit.com/v3/company/{realmId}`; sandbox
  `https://sandbox-quickbooks.api.intuit.com/v3/company/{realmId}`. `realmId` comes back on the callback.
- **Sandbox realm ⇒ Development keys + sandbox base URL.** Mixing them fails.
- Lists go through `GET /query?query=SELECT …` (max 1000 rows); `GET /cdc` for incremental sync.
- `InventoryAdjustment` create requires `DocNumber`, `AdjustAccountRef`, `Line`, `TxnDate`.
- No gift cards or consignments in QBO. Data reads are metered under the Intuit App Partner Program.

### Not started / blocked
- **Lightspeed K-Series:** no self-serve app; partner application required. Check for an existing partnership.
- **Unleashed:** no OAuth — API ID + API key, requests signed with HMAC-SHA256. Needs a trial account.
- **Cin7 Core / Cin7 Omni:** API-key auth; docs, accounts and any existing specs via Sandesh.

## 5. Inventory tracking must be on

The agent only sees stock for items the merchant tracks. Connecting a store does **not** turn tracking on.

| Platform | Where | Watch out for |
|---|---|---|
| Shopify | Product → variant → Inventory → **Inventory tracked** (older label "Track quantity"); bulk: Products → select → **Bulk edit** → Columns → add the column | The list shows "Inventory not tracked" for untracked items; tracked ones show "N in stock" |
| Square | Item → **Manage inventory** → ⋯ on the location row → **Track by stock count** | **"Track by availability"** keeps no count — it is not tracking. Bulk "Enable tracking" (Items → Settings → Inventory) is missing in the sandbox dashboard and sets never-counted items to 0 (sold out) |
| Clover | Inventory → Setup → **Track stock**, then per-item stock counts | Depends on the merchant's plan |

By API: Shopify `inventoryItemUpdate` (`tracked: true`); Square `track_inventory: true` on each item
variation (send the full variation with its current `version`), then a `PHYSICAL_COUNT` via BatchChangeInventory.

## 6. Troubleshooting log

| Symptom | Cause | Fix |
|---|---|---|
| QBO callback: `CONNECT_FAILED … invalid_client` | Token request rejected the client credentials. Intuit's OAuth Playground worked with the Development keys, so the agent held different credentials (likely Production keys or a mistyped secret) | Re-save the **Development** client ID + secret in the agent's Developer app; use the sandbox API base; start a fresh sign-in (codes are single-use, ~5 min). If it persists, check the agent sends credentials as HTTP Basic |
| Shopify 403 on REST with customer data | Protected customer data access not requested | Request step 1 on the app's API access page |
| Agent app: OAuth app dropdown shows "None for …" | No Developer app saved with that exact token URL | Owner saves the Developer app in Settings, token URL must match |
| Shopify GraphQL op fails validation after a version bump | Field deprecated in the new version | Follow the validator's "Use X instead" message, rebuild |
| `build_shopify_rest.py` hangs | Python `urllib` takes ~20 s per request to shopify.dev on macOS | Script fetches with `curl` instead (already fixed) |
| Square spec lint error on `externalDocs` | Square nests it under `info` | `trim_openapi.py` moves it to the root (already fixed) |
| `trim_openapi.py` `KeyError: 'AppFeeAllocation'` | Square's `api.json` references a schema it never defines (pulled in by the `Refunds` tag) | Script adds a placeholder `object` schema and prints a WARNING naming it (already fixed) |

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
- Write specs for Clover and Lightspeed R-Series (both from docs).
- Square webhook URL from the team; Square production redirect URL.
- Shopify: `read_all_orders` approval; teammate's gift-card create error (exact text needed).
- QBO: production App URLs from the team; confirm the agent's credential method after the `invalid_client` fix.
- Decide whether the agent app takes file uploads or needs raw URLs (private repo raw URLs need auth).
