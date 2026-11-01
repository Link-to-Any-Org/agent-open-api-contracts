# QuickBooks Online (Intuit)

| Field | Value |
|---|---|
| Status | Not started |
| Dev app | Done: `link_engine_service_v2-dev-app` (workspace "link"). Development keys work now; production keys need App URLs, terms, categories and the compliance questionnaire. |
| Auth | OAuth 2.0 (authorization code) |
| Callback URL | `https://agent.linktoany.com/oauth/callback` (added under Development and Production Redirect URIs) |
| Authorize URL | `https://appcenter.intuit.com/connect/oauth2` |
| Token URL | `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer` |
| API base URL | `https://quickbooks.api.intuit.com/v3/company/{realmId}/` (sandbox: `https://sandbox-quickbooks.api.intuit.com/v3/company/{realmId}/`) |
| API version | v3 + `?minorversion=<n>` query param on every call (pick current minor version, verify) |
| Scopes / permissions | `com.intuit.quickbooks.accounting` |
| Docs | https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account |
| Upstream spec | None official found. Community copies only (API Evangelist, 2018). |
| Upstream license | N/A |
| Spec file in repo | none yet — write from docs (or Intuit Postman collection, verify) |
| Last pulled | — |

## Focus resources

| Resource | Supported | Entity |
|---|---|---|
| Inventory | Yes | Item (`QtyOnHand`), InventoryAdjustment (verify) |
| Orders | Yes | SalesReceipt, Invoice, Estimate, PurchaseOrder |
| Customers | Yes | Customer |
| Gift cards | No | |
| Locations | Partial | Department ("location tracking") |
| Consignments | No | |
| Images | Yes | Attachable |

## Open questions / (verify)

- `realmId` (company ID) comes back on the OAuth callback; the agent must store it per connection.
- Intuit App Partner Program meters data reads; check which tier the workspace is on.
- Production App URLs (launch, disconnect, connect/reconnect) needed from the team.
