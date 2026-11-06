# Clover — knowledge

Facts table (URLs, versions, counts): [SOURCE.md](SOURCE.md). Cross-platform background: [../../KNOWLEDGE.md](../../KNOWLEDGE.md).

## Setup

- **App:** sandbox.dev.clover.com, Private app, North America, Web clients. Production needs App Market review.
- **Redirect:** Site URL `https://agent.linktoany.com` + **Alternate Launch Path** `/oauth/callback`
  (the field rejects full URLs).
- **Permissions** (App Settings → Requested Permissions): Customers R/W, Inventory R/W, Merchant R/W,
  Orders R/W, Payments R, Employees R. Orders **Write** was found unticked on 2026-11-04 and re-ticked; the
  sandbox app currently also has Employees W and Payments W ticked, which the migration does not need:
  untick them before App Market review. Leave **Ecommerce → Enable online payments** off: it is for
  taking card payments online, not for importing orders.

## Platform quirks

- Clover has no fine-grained scopes (no `atomic_orders` scope): atomic orders (`/atomic_order/checkouts`)
  use Orders Read/Write plus Inventory Read (items, tax rates).
- **Changed permissions only apply after the merchant uninstalls and reinstalls the app** (test merchants
  too), then the agent reconnects for a new token. Refreshing the old token keeps the old permissions.
- No gift-card or consignment permissions exist. One merchant = one location.
- Test merchant needs data before testing. No official spec (Postman collection only).

## Inventory tracking

| Platform | Where | Watch out for |
|---|---|---|
| Clover | Inventory → Setup → **Track stock**, then per-item stock counts | Depends on the merchant's plan |

- **Stock tracking** depends on the merchant's Clover plan (Inventory → Setup → Track stock).

## Seen in live agent testing

- 2026-11-05 (ISS-036/037): in a K-Series file migration, items with no price were written as Variable price and modifier prices as 0. The manager accepted this behaviour (rationale pending).

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Clover: `POST /atomic_order/checkouts` → 401 even with a fresh token | Clover returns 401 for a missing permission too. Orders **Write** was unticked in Requested Permissions | Tick Orders Write, Save, uninstall + reinstall the app on the merchant, reconnect the System in the agent, re-run |

## Open items

- Write the Clover spec (from docs).
- Record the rationale for accepting the Variable-price / 0-modifier behaviour (pending).
