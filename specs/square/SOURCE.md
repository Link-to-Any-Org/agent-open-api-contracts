# Square

| Field | Value |
|---|---|
| Status | Not started (official spec ready to pull) |
| Dev app | Done: "link engine service v2" (Sandbox + Production credentials) |
| Auth | OAuth 2.0 (authorization code) |
| Callback URL | `https://agent.linktoany.com/oauth/callback` (set per environment: Sandbox and Production) |
| Authorize URL | `https://connect.squareup.com/oauth2/authorize` (sandbox: `https://connect.squareupsandbox.com/oauth2/authorize`) |
| Token URL | `https://connect.squareup.com/oauth2/token` (sandbox: `https://connect.squareupsandbox.com/oauth2/token`) |
| API base URL | `https://connect.squareup.com/v2` (sandbox: `https://connect.squareupsandbox.com/v2`) |
| API version | Set by `Square-Version` header (record the spec's version when pulled) |
| Scopes / permissions | Requested at authorize time: ITEMS_READ/WRITE, INVENTORY_READ/WRITE, ORDERS_READ/WRITE, CUSTOMERS_READ/WRITE, GIFTCARDS_READ/WRITE, MERCHANT_PROFILE_READ, PAYMENTS_READ |
| Docs | https://developer.squareup.com/reference/square |
| Upstream spec | https://github.com/square/connect-api-specification (`api.json`) |
| Upstream license | Apache-2.0 (checked on GitHub, 2026-10-30; repo last pushed 2026-09-15) |
| Spec file in repo | none yet |
| Last pulled | — |

## Focus resources

| Resource | Supported | Notes |
|---|---|---|
| Inventory | Yes | Inventory API |
| Orders | Yes | Orders API |
| Customers | Yes | Customers API |
| Gift cards | Yes | Gift Cards + Gift Card Activities APIs |
| Locations | Yes | Locations API (MERCHANT_PROFILE_READ) |
| Consignments | No native concept (verify) | |
| Images | Yes | Catalog images |

## Open questions / (verify)

- Full `api.json` is very large; trim to the focus resources or upload whole (check agent app size limit).
- Webhook notification URL still needed from the team (must not be the OAuth callback).
