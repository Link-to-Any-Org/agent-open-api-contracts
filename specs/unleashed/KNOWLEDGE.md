# Unleashed — knowledge

Facts table (URLs, versions, counts): [SOURCE.md](SOURCE.md). Cross-platform background: [../../KNOWLEDGE.md](../../KNOWLEDGE.md).

## Status

- **Unleashed:** no OAuth — API ID + API key, requests signed with HMAC-SHA256. Needs a trial account.

## What we know

- Auth: headers `api-auth-id` + `api-auth-signature` (HMAC-SHA256 of the query string, signed with the API key) (verify); base URL `https://api.unleashedsoftware.com/` (verify).
- Docs: https://apidocs.unleashedsoftware.com/; no upstream spec found, so write from docs. See [SOURCE.md](SOURCE.md).

## Open items

- Signature scheme must be described in the spec as an API-key scheme; the agent app must compute the signature.
- Get a trial account to test.
