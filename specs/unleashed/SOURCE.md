# Unleashed

| Field | Value |
|---|---|
| Status | Not started |
| Dev app | Not needed: merchant's API ID + API key (Integration → Unleashed API Access). Needs a trial account to test. |
| Auth | Headers `api-auth-id` + `api-auth-signature` (HMAC-SHA256 of the query string, signed with the API key) (verify) |
| Callback URL | N/A |
| Authorize URL | N/A |
| Token URL | N/A |
| API base URL | `https://api.unleashedsoftware.com/` (verify) |
| API version | (verify) |
| Scopes / permissions | N/A (key has full account access) |
| Docs | https://apidocs.unleashedsoftware.com/ |
| Upstream spec | None found |
| Upstream license | N/A |
| Spec file in repo | none yet — write from docs |
| Last pulled | — |

## Focus resources

| Resource | Supported | Notes |
|---|---|---|
| Inventory | Yes | StockOnHand |
| Orders | Yes | SalesOrders, PurchaseOrders |
| Customers | Yes | |
| Gift cards | No | |
| Locations | Yes | Warehouses |
| Consignments | Partial (verify) | WarehouseStockTransfers |
| Images | (verify) | |

## Open questions / (verify)

- Signature scheme must be described in the spec as an API-key scheme; the agent app must compute the signature.
