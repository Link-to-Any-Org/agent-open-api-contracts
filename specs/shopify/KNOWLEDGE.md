# Shopify — knowledge

Facts table (URLs, versions, counts): [SOURCE.md](SOURCE.md). Cross-platform background: [../../KNOWLEDGE.md](../../KNOWLEDGE.md).

## Setup

- **App:** Dev Dashboard (dev.shopify.com), distribution **Public** — this cannot be undone.
- **OAuth:** authorize `https://{shop}.myshopify.com/admin/oauth/authorize`, token
  `https://{shop}.myshopify.com/admin/oauth/access_token`; calls send `X-Shopify-Access-Token`.
- **Protected customer data:** orders and customers need it. Step 1 (data fields + reasons) is enough for
  dev stores; the 403 "not approved to access REST endpoints with protected customer data" means it is missing.
- **Order history:** only the last 60 days until `read_all_orders` is approved (requested on the app's API
  access page; needs a distribution choice first). After approval: add the scope in a new app version,
  release, reconnect the store.
- **Scopes still to add** for consignment receiving: `read_inventory_shipments`,
  `write_inventory_shipments_received_items` (and `inventory_counts` if counts are needed).

## How the spec is built

- **Shopify GraphQL — one endpoint, named examples.** GraphQL has a single `POST /graphql.json`, and OpenAPI
  cannot list the same path twice, so each operation is a named request example plus an
  `x-graphql-operations` index. Every operation is validated against Shopify's live schema.
- **Shopify REST — generated from docs.** Shopify's REST reference pages are available as markdown
  (`https://shopify.dev/docs/api/admin-rest/<version>/resources/<slug>.md`) with endpoints, parameters,
  property lists and example requests/responses. Response schemas are inferred from those examples.
- **Shopify REST nulls.** Fields that are `null` in every Shopify example have no type; their description
  says so (13 on Order, a few elsewhere).
- **Shopify REST property docs** only cover the main properties Shopify documents (about 12 per resource);
  the rest are typed from examples without a description.

## Platform quirks

- **GraphQL vs REST:** same token and scopes work for both. REST is frozen and **not allowed for new public
  apps at App Store review**; transfers/shipments and product writes are GraphQL-only. Use GraphQL; keep REST
  only for simple calls already in use and move them before submission.
- **Schema source:** `https://shopify.dev/admin-graphql-direct-proxy/<version>` answers introspection without
  a login (it backs shopify.dev's GraphiQL). If it ever closes, validate with a real store token.
- **2026-10 deprecations caught by the validator:** `ProductVariant.barcode` → `barcodes`,
  `InventoryItem.variant` → `variants`.

## Inventory tracking

| Platform | Where | Watch out for |
|---|---|---|
| Shopify | Product → variant → Inventory → **Inventory tracked** (older label "Track quantity"); bulk: Products → select → **Bulk edit** → Columns → add the column | The list shows "Inventory not tracked" for untracked items; tracked ones show "N in stock" |

By API: Shopify `inventoryItemUpdate` (`tracked: true`).

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Shopify 403 on REST with customer data | Protected customer data access not requested | Request step 1 on the app's API access page |
| Shopify GraphQL op fails validation after a version bump | Field deprecated in the new version | Follow the validator's "Use X instead" message, rebuild |
| `build_shopify_rest.py` hangs | Python `urllib` takes ~20 s per request to shopify.dev on macOS | Script fetches with `curl` instead (already fixed) |

## Open items

- Shopify: `read_all_orders` approval; teammate's gift-card create error (exact text needed).
