# Square — knowledge

Facts table (URLs, versions, counts): [SOURCE.md](SOURCE.md). Cross-platform background: [../../KNOWLEDGE.md](../../KNOWLEDGE.md).

## Setup

- **OAuth:** authorize `https://connect.squareup.com/oauth2/authorize`, token `…/oauth2/token`
  (sandbox host `connect.squareupsandbox.com`). Redirect URL is set **per environment**.
- **Scopes are requested at authorize time**, not in the dashboard. The kept operations use:
  `ITEMS_*`, `INVENTORY_*`, `ORDERS_*`, `CUSTOMERS_*`, `GIFTCARDS_*`, `MERCHANT_PROFILE_READ`, plus
  `MERCHANT_PROFILE_WRITE` (create/update locations) and `PAYMENTS_WRITE` (PayOrder, CreateCustomerCard) only if
  the agent should do those.
- **Webhook URL must not be the OAuth callback.** The real webhook URL is still needed from the team.
- **Sandbox:** the Default Test Account starts empty; add data in the sandbox dashboard or API Explorer
  (`https://developer.squareup.com/explorer/square`).

## How the spec is built

- **Square — trim, don't copy whole.** The official `api.json` is 3.1 MB with 250+ paths; the trimmed file is
  1.0 MB with 70 operations. Smaller specs are easier for the agent to choose from. `trim_openapi.py` keeps
  every schema the kept operations reference, drops deprecated operations and Square's `x-unitTests`
  fixtures, and keeps only the OAuth scopes those operations use. It also moves `info.externalDocs` to the
  root, because Square nests it where OpenAPI does not allow it (a lint error otherwise).

## Platform quirks

- **Consignments** = `TransferOrder`. **Images** live under Catalog.

## Inventory tracking

| Platform | Where | Watch out for |
|---|---|---|
| Square | Item → **Manage inventory** → ⋯ on the location row → **Track by stock count** | **"Track by availability"** keeps no count — it is not tracking. Bulk "Enable tracking" (Items → Settings → Inventory) is missing in the sandbox dashboard and sets never-counted items to 0 (sold out) |

By API: Square `track_inventory: true` on each item
variation (send the full variation with its current `version`), then a `PHYSICAL_COUNT` via BatchChangeInventory.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Square spec lint error on `externalDocs` | Square nests it under `info` | `trim_openapi.py` moves it to the root (already fixed) |
| `trim_openapi.py` `KeyError: 'AppFeeAllocation'` | Square's `api.json` references a schema it never defines (pulled in by the `Refunds` tag) | Script adds a placeholder `object` schema and prints a WARNING naming it (already fixed) |

## Open items

- Square webhook URL from the team; Square production redirect URL.
