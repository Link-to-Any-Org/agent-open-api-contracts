# Shopify

| Field | Value |
|---|---|
| Status | Ready: GraphQL (primary) + REST (legacy) |
| Dev app | Done: `link_engine_service_v2-dev-app` (Dev Dashboard, distribution: Public) |
| Auth | OAuth 2.0 (authorization code); calls send `X-Shopify-Access-Token: <token>` |
| Callback URL | `https://agent.linktoany.com/oauth/callback` |
| Authorize URL | `https://{shop}.myshopify.com/admin/oauth/authorize` |
| Token URL | `https://{shop}.myshopify.com/admin/oauth/access_token` |
| API base URL | `https://{shop}.myshopify.com/admin/api/2026-10` |
| API version | `2026-10` (Shopify releases quarterly; each version is supported ~12 months) |
| Docs | GraphQL: https://shopify.dev/docs/api/admin-graphql/2026-10 · REST: https://shopify.dev/docs/api/admin-rest/2026-10 |
| Upstream spec | None from Shopify. GraphQL is checked against the live schema; REST is built from the REST reference pages. |
| Last pulled | 2026-11-01 |

## Which one to use

| | GraphQL (`graphql/openapi.json`) | REST (`rest/openapi.json`) |
|---|---|---|
| Status at Shopify | Current API, gets all new features | Legacy, frozen |
| App Store review | Required for new public apps | Not allowed for new public apps |
| Shape | One endpoint, `POST /graphql.json`; 27 ready operations as named examples | 31 separate endpoints |
| Consignments (transfers, shipments) | Yes | No |
| Product / variant writes | Yes | Left out (deprecated) |

Rule of thumb: use GraphQL. Use REST only for simple calls the team already has working,
and plan to move them to GraphQL before App Store submission.

## GraphQL (`graphql/`)

- `operations.yaml` — source of truth: 27 operations (name, area, scopes, query, example variables).
- `openapi.json` — generated: `POST /graphql.json`, every operation as a named request example,
  plus an `x-graphql-operations` index (name, area, query/mutation, scopes).
- Every operation is validated against Shopify's live 2026-10 schema: field names, no deprecated
  fields, and example variables match their input types (`npm run validate:shopify`).

| Area | Operations |
|---|---|
| Shop | GetShop |
| Locations | ListLocations |
| Products / images | ListProducts, GetProduct, FindVariantsBySku, AddProductImage |
| Inventory | ListInventoryAtLocation, GetInventoryItem, AdjustInventory, SetInventory |
| Consignments | ListInventoryTransfers, GetInventoryTransfer, CreateInventoryTransfer, MarkTransferReadyToShip, ReceiveInventoryShipment |
| Orders | ListOrders, GetOrder |
| Customers | ListCustomers, GetCustomer, CreateCustomer, UpdateCustomer |
| Gift cards | ListGiftCards, GetGiftCard, CreateGiftCard, CreditGiftCard, DebitGiftCard, DeactivateGiftCard |

## REST (`rest/`)

- `endpoints.yaml` — which endpoints to include (31).
- `openapi.json` — generated from the markdown REST reference pages: paths, parameters and summaries
  from the page, request bodies from the documented curl examples, response schemas inferred from the
  documented example responses, property descriptions and `deprecated` flags from the Properties list.
- Fields that were `null` in every Shopify example have no type; they say so in their description.
- Lists paginate with the `Link` header (`page_info`), `limit` max 250.

## Scopes

App scopes (configured in the Dev Dashboard): read/write customers, draft_orders, files,
gift_card_transactions, gift_cards, inventory, inventory_transfers, locations, orders, products;
read_inventory_purchase_orders. Each GraphQL operation lists the scopes it needs.

Still to add in the app for the consignment operations: `read_inventory_shipments`,
`write_inventory_shipments_received_items` (and `inventory_counts` if stock counts are needed).

## Regenerate

```bash
npm install                               # once: installs graphql for validation
python3 scripts/build_shopify_graphql.py  # GraphQL: operations.yaml -> openapi.json
npm run validate:shopify                  # check every operation against the live schema
python3 scripts/build_shopify_rest.py     # REST: re-reads the 2026-10 reference pages
./scripts/lint.sh
```

To move to a new API version, change `API_VERSION` in both build scripts, rebuild, and fix
whatever `validate:shopify` reports as deprecated or missing.

## Open questions / (verify)

- Orders: only the last 60 days until `read_all_orders` is approved (requested, pending).
- Orders and customers need protected customer data access (step 1 granted for the dev store).
- Gift card creation: confirm it works on the test store (teammate saw a create error; exact text still needed).
- Schema check uses the public docs proxy `https://shopify.dev/admin-graphql-direct-proxy/2026-10`
  (what shopify.dev's GraphiQL explorer uses); if it ever closes, validate with a real store token instead.
- Scopes per GraphQL operation are taken from Shopify's docs, not checked by the validator.
