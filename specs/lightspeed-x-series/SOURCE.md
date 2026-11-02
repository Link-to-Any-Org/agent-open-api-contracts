# Lightspeed Retail X-Series (formerly Vend)

| Field | Value |
|---|---|
| Status | Ready (merged from official per-endpoint definitions) |
| Dev app | Done (developers.vendhq.com) |
| Auth | OAuth 2.0 (authorization code); API calls send `Authorization: Bearer <token>` |
| Callback URL | `https://agent.linktoany.com/oauth/callback` |
| Authorize URL | `https://secure.retail.lightspeed.app/connect` |
| Token URL | `https://{domain_prefix}.retail.lightspeed.app/api/1.0/token` (per store) |
| API base URL | `https://{domain_prefix}.retail.lightspeed.app/api/2026-10` |
| API version | `2026-10` (date-based; v0.9 and v2.0 are deprecated) |
| Scopes / permissions | See below |
| Docs | https://x-series-api.lightspeedhq.com/docs/introduction (auth: `/docs/authorization`, scopes: `/docs/scopes`) |
| Upstream spec | No single file. Each reference page embeds a one-operation OpenAPI 3.0.1 definition. |
| Upstream license | Apache-2.0 (stated in each embedded definition's `info.license`) |
| Spec file in repo | `openapi.json`: 71 operations, 50 paths, 191 schemas (385 KB) |
| Last pulled | 2026-11-02 (`/search` gained paging: `SearchPageInfo`, `SearchVersionRange`). 2027-01 is announced (fulfillment packages); not adopted yet |

## What was kept

The 71 reference pages listed in `endpoints.txt`, merged with `scripts/merge_openapi.py`.
The merge fails on any path or schema defined two different ways; this pull had no conflicts.

| Resource | X-Series API | Notes |
|---|---|---|
| Inventory | Inventory, inventory levels, stock adjustments, reorder points | |
| Orders | Sales (+ return, fulfillments), Purchase Orders (read-only) | |
| Customers | Customers, addresses, customer groups (read) | |
| Gift cards | Gift Cards | list, create, find, transactions, reverse, void |
| Locations | Outlets, Retailer | |
| Consignments | Consignments, Consignment Products | `SUPPLIER`, `OUTLET`, `STOCKTAKE`, `RETURN` types |
| Images | Product Images, product family images | |
| (support) | Products, Product families, Suppliers, Search | needed to resolve IDs used above |

Left out: the deprecated `voidgiftcard` endpoint, and everything outside the focus resources
(price books, promotions, registers, services, store credit, users, webhooks, ...).

## Scopes

Scopes named by the kept operations (requested in the `scope` param on the authorize URL):
`consignments:read`, `consignments:write:inventory_count`, `consignments:write:stock_order`,
`consignments:write:stock_transfer`, `customers:read`, `customers:write`, `gift_cards:read`,
`gift_cards:write:issue`, `gift_cards:write:redeem`, `inventory:read`, `inventory:write`,
`outlets:read`, `payment_types:read`, `products:read`, `products:read:costs`, `products:write`,
`retailer:read`, `sales:read`, `sales:write`, `suppliers:read`, `users:read`.

## Regenerate

```bash
./scripts/build_x_series.sh   # re-downloads every page in endpoints.txt and re-merges
./scripts/lint.sh
```

To add an endpoint: add its slug (the last part of the reference page URL) to `endpoints.txt`, then rebuild.
When Lightspeed releases a new date version, the build picks it up; update "API version" above.

## Open questions / (verify)

- `{domain_prefix}` is the store's subdomain; the agent must store it per connection.
- Spec uses a plain `bearerAuth` scheme, not an `oauth2` scheme; the agent app's OAuth setup supplies the token.
- Vendor lint warnings (examples, 4xx responses, one ambiguous gift-card path) are off for this file in `redocly.yaml`.
