# Clover

| Field | Value |
|---|---|
| Status | Not started |
| Dev app | Done (sandbox, Private app, North America). Production needs App Market review. |
| Auth | OAuth 2.0 (authorization code) |
| Callback URL | Site URL `https://agent.linktoany.com` + Alternate Launch Path `/oauth/callback` |
| Authorize URL | (verify) — sandbox host `https://sandbox.dev.clover.com` |
| Token URL | (verify) — sandbox API host `https://apisandbox.dev.clover.com` |
| API base URL | `https://apisandbox.dev.clover.com/v3/merchants/{mId}` (sandbox); production `https://api.clover.com/v3/merchants/{mId}` (NA, verify) |
| API version | v3 |
| Scopes / permissions | Customers R/W, Inventory R/W, Merchant R/W, Orders R/W, Payments R, Employees R |
| Docs | https://docs.clover.com/dev/reference |
| Upstream spec | None official; Postman collection available |
| Upstream license | Not stated (verify) |
| Spec file in repo | none yet — convert Postman collection or write from docs |
| Last pulled | — |

## Focus resources

| Resource | Supported | Notes |
|---|---|---|
| Inventory | Yes | items, stock |
| Orders | Yes | |
| Customers | Yes | |
| Gift cards | No | no gift card permission in dashboard |
| Locations | No | one merchant = one location |
| Consignments | No | |
| Images | (verify) | |

## Open questions / (verify)

- Test merchant needs data before testing.
- `{mId}` comes back on the OAuth redirect; the agent must store it per connection.
