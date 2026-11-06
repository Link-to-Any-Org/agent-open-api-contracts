# Lightspeed Retail R-Series

| Field | Value |
|---|---|
| Status | Ready (hand-written from docs; not tried against a live store) |
| Dev app | Done (registered at https://cloud.lightspeedapp.com/oauth/register.php) |
| Auth | OAuth 2.0 (authorization code); PKCE support (verify) |
| Callback URL | `https://agent.linktoany.com/oauth/callback` |
| Authorize URL | `https://cloud.lightspeedapp.com/auth/oauth/authorize` (older: `/oauth/authorize.php`) |
| Token URL | `https://cloud.lightspeedapp.com/auth/oauth/token` (older: `/oauth/access_token.php`) |
| API base URL | `https://api.lightspeedapp.com/API/V3/Account/{accountID}` (`accountID` is a server variable); `GET /Account.json` uses `https://api.lightspeedapp.com/API/V3` |
| API version | V3 |
| Scopes / permissions | `employee:all` |
| Docs | https://developers.lightspeedhq.com/retail/ |
| Upstream spec | None official. Written from the docs via Context7 (`/websites/developers_lightspeedhq_retail`) |
| Upstream license | N/A (own work) |
| Spec file in repo | `openapi.yaml`: 49 operations, 33 paths, 90 schemas. Hand-edit this file (it was drafted with a one-off script that is not kept) |
| Last pulled | 2026-11-06 via Context7 |

## Typing rule

R-Series JSON sends every scalar as a string. Every scalar in request and response schemas is `type: string`;
the description says the meaning ("Integer ID, sent as a string", "\"true\" or \"false\""). Timestamps are
`string` with `format: date-time`. **String-typed request bodies were not verified against the live API**: some
docs curl examples send plain numbers/booleans (e.g. the Sale create example sends `"employeeID": 2`).

## Endpoints (all confirmed in Context7)

| Group | Operations |
|---|---|
| Account | `GET /Account.json` |
| Inventory | Item (list, get, create, update incl. `ItemShops.ItemShop.qoh`), ItemShop (list), ItemMatrix (list, get, create, update), ItemAttributeSet (list, get, create), Manufacturer (list, get, create), Category (list, create), Vendor (list, create), TaxClass (list), TaxCategory (list) |
| Customers | Customer (list, get, create, update); Contact is nested |
| Orders | Sale (list, get, create, update, with nested SaleLines + SalePayments), PaymentType, Register, Employee (list), purchase Order (list, get, create), OrderLine (create) |
| Gift cards | CreditAccount (list, get, create, update); gift card = `giftCard` flag, code 8-32 digits |
| Locations | Shop (list, get) |
| Consignments | Inventory/Transfer (list, get, create), `TransferItems` (list), `AddItems` (create) |
| Images | `POST /Image.json` (multipart: `data` JSON part + `image` file part) |

Shared: V3 cursor paging (`@attributes.next`/`previous`), parameters `limit`, `sort`, `after`, `before`, `archived`,
`load_relations`, `count`; query operators are described once in `info.description`. Errors: 401 and 429 (with `Retry-After`).

## Scopes

Context7 shows finer scopes on some endpoint pages (`employee:inventory`, `employee:inventory_read`,
`employee:product_cost` for ItemShop; `employee:register` for Register and DisplayTemplate/Employee;
`employee:inventory_base` for label templates; `employee:admin_employees` for EmployeeHours). None contradicts
`employee:all`, so only `employee:all` is declared. Scope pages for the other resources were not returned (verify).

## Open questions / (verify)

Left out of the spec because Context7 did not show them:
- **ItemShop write endpoint** (`PUT /ItemShop/{id}.json`): only the update through `PUT /Item/{id}.json` is documented.
- **Image list/get** (`GET /Image.json`, `/Image/{imageID}.json`): fields and a "read single" example exist, but no path or list definition came back. Also `POST /ItemMatrix/{id}/Image.json` (documented) is not included; use `/Image.json` with `itemMatrixID`.
- **Category/Vendor get and update, Customer/Sale delete, Order update, OrderLine list/update, Sale refund, Transfer update/send/check-in/receive**: not queried or not shown.
- **Writing item attributes** for a variant (`ItemAttributes` / `attribute1..3` on Item create): shown only in a response.
- **Writing contact addresses/websites** on Customer or Vendor; the `Vendor.Contact` and `Reps` shapes.
- Customer **CustomerType, Discount** endpoints (IDs are in the spec, endpoints are not).

Docs inconsistencies kept as-is:
- ItemAttributeSet `name`: the fields table says only Color/Size, Size, Color, 3 Attributes are allowed; the create example uses "Color/Size/Fabric".
- CreditAccount create: the endpoint page requires `customerID`; the gift card tutorial does not (and says POST is for gift cards only). `customerID` is optional in the spec.
- Order create: the request example says `stockInstruction`, the attributes table says `stockInstructions`. The spec uses `stockInstructions`.
- Sale: `updatetime` (list/update) vs `updateTime` (create) in responses. ItemShop `onWorkOrder` (table) vs `onWorkorder` (example); the spec uses the example's spelling.
- A list with one record may come back as an object, not an array (CreditAccount list example); clients should accept both.
- Request examples mix numbers and strings (`"employeeID": 2` vs `"2"`).

Other:
- `{accountID}` comes from `GET /Account.json`; the agent must store it per connection.
- Whether the `Account` response has an `@attributes` envelope is not shown.
- PKCE support (verify).
- Leaky-bucket rate limit applies (bucket size 90 and burst 20 in the docs example); `count=1` costs 10 drips.
- Not tried against a live store.
