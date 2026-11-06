# Lightspeed X-Series (formerly Vend) — knowledge

Facts table (URLs, versions, counts): [SOURCE.md](SOURCE.md). Cross-platform background: [../../KNOWLEDGE.md](../../KNOWLEDGE.md).

## Setup

- **OAuth:** authorize `https://secure.retail.lightspeed.app/connect`, token
  `https://{domain_prefix}.retail.lightspeed.app/api/1.0/token` (per store). API base
  `https://{domain_prefix}.retail.lightspeed.app/api/2026-10`. Store `{domain_prefix}` per connection.
- **Scopes go in the authorize URL** (space-separated) — i.e. the Scopes field of the system in the agent app.
  Recommended set (covers LinkOps jobs + focus resources):
  ```
  products:read products:write customers:read customers:write sales:read sales:write suppliers:read suppliers:write consignments:read consignments:write:stock_order consignments:write:stock_transfer consignments:write:inventory_count inventory:read inventory:write outlets:read gift_cards:read gift_cards:write:issue gift_cards:write:redeem retailer:read registers:read payment_types:read taxes:read users:read
  ```
- `consignments:write` **no longer exists**; it is split into `:stock_order`, `:stock_transfer`,
  `:inventory_count` (LinkOps help text still shows the old name). Reconnect after changing scopes.

## How the spec is built

- **X-Series — merge.** Lightspeed publishes no single file, but every reference page embeds a complete
  one-operation OpenAPI 3.0.1 document (ReadMe-hosted docs; append `.md` to any page URL).
  `merge_openapi.py` joins them and **refuses to write** if two pages define the same path or schema
  differently, so nothing is silently overwritten.

## Platform quirks

- Old sale-fulfillment endpoints were removed in 2026-07; return-sale is now `POST`. Our spec uses the new ones.

## Seen in live agent testing

- 2026-11-06 (tracker ISS-038): on our tax-exclusive test store, product create with `price_including_tax` failed 422 "price including tax is not allowed when retailer is tax exclusive". Send the price excluding tax only.
- 2026-11-06 (ISS-038): product create sending both a tax ID and outlet taxes failed 422 "either tax ID or outlet taxes can be provided, but not both". Send one.
- 2026-11-06 (ISS-039): sales were held as MISSING_REFERENCE when the products/customers they point to were created earlier in the same run. A second run matched them and wrote the sales without duplicates.
- 2026-11-06: payment types offered on our test store are Cash, "Other payment method" (renameable) and integrated ones (Square, Windcave). Card payments without a terminal go under "Other payment method".
- 2026-11-06: a new trial store ships 14 demo product rows (category Fashion, with variants). Store URL: at least 5 characters, lowercase, no special characters; names of closed or expired stores appear to stay reserved.
