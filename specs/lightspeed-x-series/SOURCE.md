# Lightspeed Retail X-Series (formerly Vend)

| Field | Value |
|---|---|
| Status | Not started |
| Dev app | Done (developers.vendhq.com) |
| Auth | OAuth 2.0 (authorization code); personal tokens for single-store use |
| Callback URL | `https://agent.linktoany.com/oauth/callback` |
| Authorize URL | (verify) |
| Token URL | (verify) — per-store, under the retailer's domain prefix |
| API base URL | `https://{domain_prefix}.retail.lightspeed.app/api/2026-10` |
| API version | `2026-10` (date-based; v0.9 and v2.0 are deprecated) |
| Scopes / permissions | (verify) |
| Docs | https://x-series-api.lightspeedhq.com/docs/introduction |
| Upstream spec | No single file. Each reference page embeds an OpenAPI 3.0.1 definition for one operation (e.g. https://x-series-api.lightspeedhq.com/reference/listsales). |
| Upstream license | Not stated (verify) |
| Spec file in repo | none yet — assemble from per-operation definitions |
| Last pulled | — |

## Focus resources

| Resource | Supported | Notes |
|---|---|---|
| Inventory | Yes (verify endpoints) | |
| Orders | Yes | sales |
| Customers | Yes (verify) | |
| Gift cards | Yes (verify) | |
| Locations | Yes | outlets |
| Consignments | Yes | native "consignments" (stock orders / transfers) |
| Images | Yes (verify) | product images |

## Open questions / (verify)

- Check reference pages in a browser for a full-spec download button before assembling by hand.
- `{domain_prefix}` is the store's subdomain; the agent must store it per connection.
