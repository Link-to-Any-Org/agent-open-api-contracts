#!/usr/bin/env python3
"""Build specs/shopify/graphql/openapi.json from operations.yaml.

GraphQL has a single endpoint, so the OpenAPI file describes POST /graphql.json
once and lists every operation as a named request example (plus an
x-graphql-operations index the agent can read). Validate the result with
`npm run validate:shopify`.

Usage: scripts/build_shopify_graphql.py
"""
import json
import os
import sys

import yaml

API_VERSION = "2026-10"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DIR = os.path.join(ROOT, "specs", "shopify", "graphql")


def main():
    with open(os.path.join(SPEC_DIR, "operations.yaml")) as f:
        ops = yaml.safe_load(f)

    names = [op["name"] for op in ops]
    if len(names) != len(set(names)):
        sys.exit("duplicate operation names in operations.yaml")

    examples = {
        op["name"]: {
            "summary": f"[{op['tag']}] {op['summary']}",
            "value": {"query": op["query"], "variables": op.get("variables") or {}},
        }
        for op in ops
    }
    index = [
        {"name": op["name"], "tag": op["tag"], "summary": op["summary"],
         "kind": "mutation" if op["query"].lstrip().startswith("mutation") else "query",
         "scopes": op.get("scopes", [])}
        for op in ops
    ]
    tags = sorted({op["tag"] for op in ops})

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": f"Shopify Admin GraphQL API {API_VERSION} (agent contract)",
            "version": API_VERSION,
            "description": (
                "Every call is `POST /graphql.json` with a `query` and `variables`. The named request "
                "examples (also listed in `x-graphql-operations`) are the operations the agent should use; "
                "each is validated against Shopify's live schema for this version. "
                "Check `userErrors` on every mutation: Shopify returns HTTP 200 even when a mutation fails. "
                "Generated from operations.yaml by scripts/build_shopify_graphql.py; do not edit by hand."
            ),
        },
        "externalDocs": {"url": f"https://shopify.dev/docs/api/admin-graphql/{API_VERSION}"},
        "servers": [{
            "url": f"https://{{shop}}.myshopify.com/admin/api/{API_VERSION}",
            "variables": {"shop": {"default": "your-store",
                                   "description": "Store subdomain, e.g. link-engine-service-v2-test-store-1"}},
        }],
        "security": [{"accessToken": []}],
        "tags": [{"name": "GraphQL", "description": "Shopify Admin GraphQL endpoint"}],
        "x-graphql-operations": index,
        "paths": {
            "/graphql.json": {
                "post": {
                    "operationId": "adminGraphql",
                    "summary": "Run a Shopify Admin GraphQL query or mutation",
                    "description": "Operations by area: " + ", ".join(
                        f"{t} ({', '.join(o['name'] for o in ops if o['tag'] == t)})" for t in tags) + ".",
                    "tags": ["GraphQL"],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {
                            "schema": {"$ref": "#/components/schemas/GraphqlRequest"},
                            "examples": examples,
                        }},
                    },
                    "responses": {
                        "200": {
                            "description": "GraphQL result. Errors appear in `errors` (query problems) or "
                                           "`data.<mutation>.userErrors` (business rules).",
                            "content": {"application/json": {
                                "schema": {"$ref": "#/components/schemas/GraphqlResponse"}}},
                        },
                        "401": {"description": "Missing or invalid access token"},
                        "402": {"description": "Shop is frozen or unpaid"},
                        "403": {"description": "App lacks a required access scope or protected-data approval"},
                        "429": {"description": "Rate limited; see extensions.cost.throttleStatus"},
                    },
                }
            }
        },
        "components": {
            "securitySchemes": {
                "accessToken": {
                    "type": "apiKey", "in": "header", "name": "X-Shopify-Access-Token",
                    "description": (
                        "Offline access token from OAuth. Authorize: https://{shop}.myshopify.com/admin/oauth/authorize "
                        "· Token: https://{shop}.myshopify.com/admin/oauth/access_token"),
                }
            },
            "schemas": {
                "GraphqlRequest": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string", "description": "GraphQL document"},
                        "variables": {"type": "object", "additionalProperties": True},
                        "operationName": {"type": "string"},
                    },
                },
                "GraphqlResponse": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "object", "nullable": True, "additionalProperties": True},
                        "errors": {"type": "array", "items": {"$ref": "#/components/schemas/GraphqlError"}},
                        "extensions": {
                            "type": "object",
                            "properties": {"cost": {"$ref": "#/components/schemas/QueryCost"}},
                        },
                    },
                },
                "GraphqlError": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "locations": {"type": "array", "items": {"type": "object", "properties": {
                            "line": {"type": "integer"}, "column": {"type": "integer"}}}},
                        "path": {"type": "array", "items": {"type": "string"}},
                        "extensions": {"type": "object", "additionalProperties": True},
                    },
                },
                "QueryCost": {
                    "type": "object",
                    "properties": {
                        "requestedQueryCost": {"type": "number"},
                        "actualQueryCost": {"type": "number"},
                        "throttleStatus": {"type": "object", "properties": {
                            "maximumAvailable": {"type": "number"},
                            "currentlyAvailable": {"type": "number"},
                            "restoreRate": {"type": "number"}}},
                    },
                },
            },
        },
    }

    with open(os.path.join(SPEC_DIR, "openapi.json"), "w") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {len(ops)} operations across {len(tags)} areas", file=sys.stderr)


if __name__ == "__main__":
    main()
