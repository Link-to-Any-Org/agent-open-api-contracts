# Lightspeed Retail R-Series

| Field | Value |
|---|---|
| Status | Not started |
| Dev app | Done (registered at https://cloud.lightspeedapp.com/oauth/register.php) |
| Auth | OAuth 2.0 (authorization code); PKCE support (verify) |
| Callback URL | `https://agent.linktoany.com/oauth/callback` |
| Authorize URL | `https://cloud.lightspeedapp.com/auth/oauth/authorize` (verify; older: `/oauth/authorize.php`) |
| Token URL | `https://cloud.lightspeedapp.com/auth/oauth/token` (verify; older: `/oauth/access_token.php`) |
| API base URL | `https://api.lightspeedapp.com/API/V3/Account/{accountID}/` |
| API version | V3 |
| Scopes / permissions | `employee:all` |
| Docs | https://developers.lightspeedhq.com/retail/ |
| Upstream spec | None official found |
| Upstream license | N/A |
| Spec file in repo | none yet — write from docs |
| Last pulled | — |

## Focus resources

| Resource | Supported | Notes |
|---|---|---|
| Inventory | Yes (verify) | ItemShop |
| Orders | Yes (verify) | Sale; vendor Order = purchase order |
| Customers | Yes (verify) | Customer |
| Gift cards | Yes (verify) | |
| Locations | Yes | Shop |
| Consignments | Partial (verify) | Transfer |
| Images | Yes (verify) | Image |

## Open questions / (verify)

- `{accountID}` comes from the token response / Account endpoint; the agent must store it per connection.
- Leaky-bucket rate limit applies.
