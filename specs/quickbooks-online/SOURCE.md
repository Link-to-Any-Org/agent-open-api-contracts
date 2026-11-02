# QuickBooks Online (Intuit)

| Field | Value |
|---|---|
| Status | Ready (hand-written paths + schemas generated from Intuit's official XSDs) |
| Dev app | Done: `link_engine_service_v2-dev-app` (workspace "link"). Development keys work now; production keys need App URLs, terms, categories and the compliance questionnaire. |
| Auth | OAuth 2.0 (authorization code) |
| Callback URL | `https://agent.linktoany.com/oauth/callback` (added under Development and Production Redirect URIs) |
| Authorize URL | `https://appcenter.intuit.com/connect/oauth2` |
| Token URL | `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer` (also used to refresh) |
| API base URL | `https://quickbooks.api.intuit.com/v3/company/{realmId}` (sandbox: `https://sandbox-quickbooks.api.intuit.com/v3/company/{realmId}`) |
| API version | v3, `minorversion=75` (Intuit retired 1–74 on 2025-08-01; 75 is the default) |
| Scopes / permissions | `com.intuit.quickbooks.accounting` |
| Docs | https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account |
| Upstream spec | No OpenAPI from Intuit. Schemas come from the XSDs in https://github.com/intuit/QuickBooks-V3-Java-SDK (`ipp-v3-java-data/src/main/xsd/`) |
| Upstream commit | `c4d5dfad23ffebf0302356876d0dc389708513a9` (2026-07-17) |
| Upstream license | Apache-2.0 (Java SDK repo, checked on GitHub 2026-11-01) |
| Spec file in repo | `openapi.json` (generated, 302 KB): 24 operations, 85 schemas. Source of truth for paths: `openapi.base.yaml` |
| Last pulled | 2026-11-01 (re-checked 2026-11-02: XSDs unchanged, minorversion 75 still current) |

## How it is built

- `openapi.base.yaml` — hand-written: servers, OAuth, the 24 endpoints, response envelopes, errors.
- `scripts/build_quickbooks_online.py` — downloads Intuit's XSDs at the pinned commit, converts the
  entity types to JSON Schema, and writes `openapi.json`. **Edit the base file, never `openapi.json`.**
- XSD → JSON follows QBO's JSON shape: references are `{value, name}`, XML attributes become fields.
- Intuit's XSD labels some fields desktop-only (QBW). Those labels are unreliable (`Item.Active` is
  labelled QBW but works in QBO), so the fields are kept and flagged `x-intuit-products: [QBW]`.

## Endpoints

| Resource | Endpoints | Notes |
|---|---|---|
| Inventory | `POST /item`, `GET /item/{id}`, `POST /inventoryadjustment`, `GET /inventoryadjustment/{id}` | Item `Type=Inventory` + `TrackQtyOnHand` holds `QtyOnHand` |
| Orders | invoice, salesreceipt, estimate, purchaseorder (create/update, get, delete; void for invoice + salesreceipt) | |
| Customers | `POST /customer`, `GET /customer/{id}` | cannot delete; set `Active=false` |
| Gift cards | — | not in QBO |
| Locations | `POST /department`, `GET /department/{id}` | QBO "location tracking" |
| Consignments | — | not in QBO |
| Images | `POST /upload`, `POST /attachable`, `GET /attachable/{id}` | upload a file and link it via `AttachableRef` |
| Support | `GET /query`, `GET /cdc`, `GET /companyinfo/{companyId}`, vendor create/get | list/search, incremental sync, vendors for POs |

All lists go through `GET /query?query=SELECT ...` (max 1000 rows per page).

## Regenerate

```bash
python3 scripts/build_quickbooks_online.py   # needs PyYAML
./scripts/lint.sh
```

To add an entity: add its type to `ROOT_TYPES` in the script and its paths to `openapi.base.yaml`.

## Open questions / (verify)

- `InventoryAdjustment`: confirmed in Intuit's docs (`POST /v3/company/{realmId}/inventoryadjustment`,
  requires `DocNumber`, `AdjustAccountRef`, `Line`, `TxnDate`; Intuit docs fetched 2026-11-02 via Context7).
  Not yet tried against the sandbox company.
- `realmId` (company ID) comes back on the OAuth callback; the agent must store it per connection.
- Intuit App Partner Program meters data reads; check which tier the workspace is on.
- Production App URLs (launch, disconnect, connect/reconnect) needed from the team.
- Not yet tried against the sandbox company.
