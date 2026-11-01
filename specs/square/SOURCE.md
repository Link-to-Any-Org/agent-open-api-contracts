# Square

| Field | Value |
|---|---|
| Status | Ready (trimmed official spec) |
| Dev app | Done: "link engine service v2" (Sandbox + Production credentials) |
| Auth | OAuth 2.0 (authorization code) |
| Callback URL | `https://agent.linktoany.com/oauth/callback` (set per environment: Sandbox and Production) |
| Authorize URL | `https://connect.squareup.com/oauth2/authorize` (sandbox: `https://connect.squareupsandbox.com/oauth2/authorize`) |
| Token URL | `https://connect.squareup.com/oauth2/token` (sandbox: `https://connect.squareupsandbox.com/oauth2/token`) |
| API base URL | `https://connect.squareup.com` (sandbox: `https://connect.squareupsandbox.com`); paths start with `/v2/` |
| API version | `Square-Version: 2026-09-16` header (spec default) |
| Scopes / permissions | See below |
| Docs | https://developer.squareup.com/reference/square |
| Upstream spec | https://github.com/square/connect-api-specification (`api.json`, OpenAPI 3.0.0) |
| Upstream commit | `0689c901bdfe1ff73f47aa28b17ccd6e0c40bf2d` (2026-09-15) |
| Upstream license | Apache-2.0 (checked on GitHub, 2026-10-30) |
| Spec file in repo | `openapi.json`: 70 operations, 58 paths, 392 schemas (1.0 MB; upstream is 3.1 MB) |
| Last pulled | 2026-11-01 |

## What was kept

Operation tags kept: `Catalog`, `Customers`, `GiftCardActivities`, `GiftCards`, `Inventory`,
`Locations`, `Merchants`, `Orders`, `TransferOrder`.

Removed: every other tag (Payments, Bookings, Labor, Loyalty, Terminal, Vendors, ...),
the 5 deprecated Inventory operations, Square's `x-unitTests` fixtures, and unused OAuth scopes.
`info.externalDocs` was moved to the document root (OpenAPI does not allow it under `info`).

| Resource | Square API | Notes |
|---|---|---|
| Inventory | Inventory | counts, changes, adjustments, physical counts |
| Orders | Orders | |
| Customers | Customers | |
| Gift cards | GiftCards, GiftCardActivities | |
| Locations | Locations, Merchants | |
| Consignments | TransferOrder | transfers between locations |
| Images | Catalog | `CreateCatalogImage`, `UpdateCatalogImage`; items live in Catalog too |

## Scopes

The kept operations use these scopes:
`ITEMS_READ/WRITE`, `INVENTORY_READ/WRITE`, `ORDERS_READ/WRITE`, `CUSTOMERS_READ/WRITE`,
`GIFTCARDS_READ/WRITE`, `MERCHANT_PROFILE_READ/WRITE`, `PAYMENTS_WRITE`.

Compared with the scopes planned for the authorize request:
- `MERCHANT_PROFILE_WRITE` is needed only for `CreateLocation` / `UpdateLocation`.
- `PAYMENTS_WRITE` is needed only for `PayOrder` and `CreateCustomerCard`.
- Add them to the authorize request only if the agent should do those actions.

## Regenerate

```bash
curl -sfL -o /tmp/square-api.json \
  https://raw.githubusercontent.com/square/connect-api-specification/master/api.json
scripts/trim_openapi.py /tmp/square-api.json specs/square/openapi.json \
  --tags Catalog,Customers,GiftCardActivities,GiftCards,Inventory,Locations,Merchants,Orders,TransferOrder \
  --server https://connect.squareup.com --server-description Production \
  --server https://connect.squareupsandbox.com --server-description Sandbox
./scripts/lint.sh
```

Then update the upstream commit, `Square-Version` and "Last pulled" above.

## Open questions

- Webhook notification URL still needed from the team (must not be the OAuth callback).
- Vendor style warnings are switched off for this file in `redocly.yaml`; real errors still fail lint.
