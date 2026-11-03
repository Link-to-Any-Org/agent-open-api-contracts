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
| Spec file in repo | `openapi.json`: 73 operations, 60 paths, 404 schemas (1.1 MB; upstream is 3.1 MB) |
| Last pulled | 2026-11-03 (same upstream commit; `Refunds` tag added) |

## What was kept

Operation tags kept: `Catalog`, `Customers`, `GiftCardActivities`, `GiftCards`, `Inventory`,
`Locations`, `Merchants`, `Orders`, `Refunds`, `TransferOrder`.

Removed: every other tag (Payments, Bookings, Labor, Loyalty, Terminal, Vendors, ...),
the 5 deprecated Inventory operations, Square's `x-unitTests` fixtures, and unused OAuth scopes.
`info.externalDocs` was moved to the document root (OpenAPI does not allow it under `info`).

Upstream bug: Square's `api.json` references `AppFeeAllocation` (in `RefundPaymentRequest` and
`PaymentRefund`) but never defines it. `trim_openapi.py` adds a placeholder `object` schema for it and
prints a warning. The field is `app_fee_allocations`, which the agent does not need for migrations.

| Resource | Square API | Notes |
|---|---|---|
| Inventory | Inventory | counts, changes, adjustments, physical counts |
| Orders | Orders | |
| Refunds | Refunds | `RefundPayment`, `ListPaymentRefunds`, `GetPaymentRefund`; refunds for imported historical orders |
| Customers | Customers | |
| Gift cards | GiftCards, GiftCardActivities | |
| Locations | Locations, Merchants | |
| Consignments | TransferOrder | transfers between locations |
| Images | Catalog | `CreateCatalogImage`, `UpdateCatalogImage`; items live in Catalog too |

## Scopes

The kept operations use these scopes:
`ITEMS_READ/WRITE`, `INVENTORY_READ/WRITE`, `ORDERS_READ/WRITE`, `CUSTOMERS_READ/WRITE`,
`GIFTCARDS_READ/WRITE`, `MERCHANT_PROFILE_READ/WRITE`, `PAYMENTS_READ/WRITE`.

Compared with the scopes planned for the authorize request:
- `MERCHANT_PROFILE_WRITE` is needed only for `CreateLocation` / `UpdateLocation`.
- `PAYMENTS_WRITE` is needed only for `PayOrder`, `CreateCustomerCard` and `RefundPayment`.
- `PAYMENTS_READ` is needed only for `ListPaymentRefunds` and `GetPaymentRefund`.
- Add them to the authorize request only if the agent should do those actions.

## Regenerate

```bash
curl -sfL -o /tmp/square-api.json \
  https://raw.githubusercontent.com/square/connect-api-specification/master/api.json
scripts/trim_openapi.py /tmp/square-api.json specs/square/openapi.json \
  --tags Catalog,Customers,GiftCardActivities,GiftCards,Inventory,Locations,Merchants,Orders,Refunds,TransferOrder \
  --server https://connect.squareup.com --server-description Production \
  --server https://connect.squareupsandbox.com --server-description Sandbox
./scripts/lint.sh
```

Then update the upstream commit, `Square-Version` and "Last pulled" above.

## Open questions

- Webhook notification URL still needed from the team (must not be the OAuth callback).
- Vendor style warnings are switched off for this file in `redocly.yaml`; real errors still fail lint.
- `RefundPayment` needs the `payment_id` of the payment to refund. The `Payments` tag (`CreatePayment`,
  `ListPayments`) is not kept, so the spec cannot create or list payments; unlinked refunds
  (`unlinked: true`, destination `CASH` or `EXTERNAL`) need no `payment_id`. Add `Payments` if the agent
  must create the payments for historical orders itself.
