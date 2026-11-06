# QuickBooks Online (Intuit) — knowledge

Facts table (URLs, versions, counts): [SOURCE.md](SOURCE.md). Cross-platform background: [../../KNOWLEDGE.md](../../KNOWLEDGE.md).

## Setup

- **App:** developer.intuit.com, workspace "link". Development keys work at once; **production keys** need
  App URLs (host domain, launch, disconnect, connect/reconnect), terms/privacy links, categories and the
  compliance questionnaire. Categories chosen: Inventory, Orders & sales, Customer management, eCommerce.
- **Redirect URIs are per environment** (Development and Production tabs). Keep Intuit's default
  `https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl` for testing.
- **OAuth:** authorize `https://appcenter.intuit.com/connect/oauth2`, token (and refresh)
  `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer`, scope `com.intuit.quickbooks.accounting`.
- **API base:** `https://quickbooks.api.intuit.com/v3/company/{realmId}`; sandbox
  `https://sandbox-quickbooks.api.intuit.com/v3/company/{realmId}`. `realmId` comes back on the callback.

## How the spec is built

- **QuickBooks — XSD → JSON Schema.** Intuit publishes no OpenAPI file, but its official Java SDK ships the
  XSD files the API is generated from. Converting them gives exact field names instead of hand-typed ones.
  Conversion follows QBO's JSON shape: references become `{value, name, type}`, XML attributes become fields.
- **QBO desktop-only labels are unreliable.** Intuit's XSD marks some fields "QBW" (desktop) only, but
  `Item.Active` is marked QBW and works in QBO. All such fields are kept and flagged
  `x-intuit-products: [QBW]` instead of dropped (109 fields).

## Platform quirks

- **Sandbox realm ⇒ Development keys + sandbox base URL.** Mixing them fails.
- Lists go through `GET /query?query=SELECT …` (max 1000 rows); `GET /cdc` for incremental sync.
- `InventoryAdjustment` create requires `DocNumber`, `AdjustAccountRef`, `Line`, `TxnDate`.
- No gift cards or consignments in QBO. Data reads are metered under the Intuit App Partner Program.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| QBO callback: `CONNECT_FAILED … invalid_client` | Token request rejected the client credentials. Intuit's OAuth Playground worked with the Development keys, so the agent held different credentials (likely Production keys or a mistyped secret) | Re-save the **Development** client ID + secret in the agent's Developer app; use the sandbox API base; start a fresh sign-in (codes are single-use, ~5 min). If it persists, check the agent sends credentials as HTTP Basic |

## Open items

- QBO: production App URLs from the team; confirm the agent's credential method after the `invalid_client` fix.
