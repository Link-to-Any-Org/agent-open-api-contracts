# Shopify

| Field | Value |
|---|---|
| Status | Not started |
| Dev app | Done: `link_engine_service_v2-dev-app` (Dev Dashboard, distribution: Public) |
| Auth | OAuth 2.0 (authorization code) |
| Callback URL | `https://agent.linktoany.com/oauth/callback` |
| Authorize URL | `https://{shop}.myshopify.com/admin/oauth/authorize` |
| Token URL | `https://{shop}.myshopify.com/admin/oauth/access_token` |
| API base URL | GraphQL: `https://{shop}.myshopify.com/admin/api/2026-10/graphql.json` |
| API version | `2026-10` (Shopify releases quarterly) |
| Scopes / permissions | read/write: customers, draft_orders, files, gift_card_transactions, gift_cards, inventory, inventory_transfers, locations, orders, products; read_inventory_purchase_orders |
| Docs | https://shopify.dev/docs/api/admin-graphql |
| Upstream spec | None official. GraphQL schema via introspection (not OpenAPI). REST Admin API is legacy. |
| Upstream license | N/A |
| Spec file in repo | none yet |
| Last pulled | — |

## Focus resources

| Resource | Supported | Notes |
|---|---|---|
| Inventory | Yes | inventory items / levels |
| Orders | Yes | last 60 days only until `read_all_orders` is approved |
| Customers | Yes | protected customer data access (step 1) granted |
| Gift cards | Yes | create via REST is Plus-only (verify for GraphQL) |
| Locations | Yes | |
| Consignments | Partial | inventory transfers / shipments (verify mapping) |
| Images | Yes | product media / files |

## Open questions / (verify)

- Agent app may expect REST + OpenAPI. Decide: hand-write OpenAPI for the GraphQL endpoint, or a REST subset.
- Pending: `read_all_orders` approval, then new app version + reconnect store.
- Advised to add: inventory_shipments, inventory_shipments_received_items, inventory_counts (read+write).
- Third-party REST spec exists (api-evangelist, version 2024-10): not official, check license before use.
