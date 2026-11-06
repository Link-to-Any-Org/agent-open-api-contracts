# Lightspeed R-Series — knowledge

Facts table (URLs, versions, counts): [SOURCE.md](SOURCE.md). Cross-platform background: [../../KNOWLEDGE.md](../../KNOWLEDGE.md).

## Setup

- **App:** registered at `https://cloud.lightspeedapp.com/oauth/register.php` (one API client per integration).
- **OAuth:** authorize `https://cloud.lightspeedapp.com/auth/oauth/authorize`, token
  `https://cloud.lightspeedapp.com/auth/oauth/token` (older `/oauth/authorize.php` and `/oauth/access_token.php`
  are legacy). API base `https://api.lightspeedapp.com/API/V3/Account/{accountID}/`.
- **Scope `employee:all` is correct.** R-Series scopes mirror employee permissions; there are no
  "sales"/"consignments" scopes (those are X-Series names). LinkOps uses only `employee:all` and creates
  sales, orders, purchase orders, gift cards and inventory updates with it.
- In the agent app: an Owner must save the R-Series Developer app first, or the OAuth app dropdown shows
  "None for https://cloud.lightspeedapp.com".
- Docs list finer scopes per endpoint (e.g. `employee:inventory`, `employee:register`); `employee:all` is the one we request.

## How the spec is built

- **Spec:** `specs/lightspeed-r-series/openapi.yaml`, hand-written from the Context7 docs (library
  `/websites/developers_lightspeedhq_retail`, API V3); Lightspeed publishes no OpenAPI file. Facts not shown
  by Context7 are left out and listed in `SOURCE.md` under (verify).
- **Everything is a string.** R-Series JSON sends every scalar as a string (IDs, numbers, "true"/"false").
  The spec types every scalar in request and response schemas as `type: string` and the description says what it
  means; timestamps are `string` + `format: date-time`. Request bodies typed this way were not tried against a live store.

## Platform quirks

- Lightspeed's developer site is behind a bot check, so docs cannot be fetched by scripts.
- **V3 paging:** cursor based. Every list returns `@attributes.next`/`previous` (full URLs, empty string at the end);
  follow them, never build `after`/`before`. Limit max 100. `count` is only returned with `count=1`. `offset` and `orderby` are gone (use `sort`).
- **Account ID:** `GET https://api.lightspeedapp.com/API/V3/Account.json` first; the spec models it as the `accountID` server variable.

## Seen in live agent testing

- 2026-11-06: the API's Manufacturer is called **Brands** in the UI (Inventory → Brands); attribute sets are under Inventory → Matrix Attribute Sets. The docs (Context7) say a completed Sale must have payments equal to its total.
- 2026-11-06: before a spec existed, the agent planner reported "No R-Series Capability creates manufacturers" and "No API lists attribute sets". The spec added in 5c6bce5 covers both.

## Open items

- R-Series spec is untested against a live store: string-typed request bodies, one-record list shape, and the (verify) items in its SOURCE.md.
