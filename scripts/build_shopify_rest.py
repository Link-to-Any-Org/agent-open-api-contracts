#!/usr/bin/env python3
"""Build specs/shopify/rest/openapi.json from Shopify's REST reference pages.

Shopify publishes no OpenAPI file, but every REST reference page is available as
markdown (https://shopify.dev/docs/api/admin-rest/<version>/resources/<slug>.md)
with the endpoint list, parameters, resource properties and example
requests/responses. For each endpoint listed in specs/shopify/rest/endpoints.yaml
this script takes:
  - path, method, summary and parameters from the page,
  - the request body from the first curl example,
  - the response schema inferred from the documented example response,
    with property descriptions (and deprecated flags) from the Properties list.

Usage: scripts/build_shopify_rest.py
"""
import json
import os
import re
import subprocess
import sys
import time

import yaml

API_VERSION = "2026-10"
DOC_URL = "https://shopify.dev/docs/api/admin-rest/{}/resources/{}.md"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DIR = os.path.join(ROOT, "specs", "shopify", "rest")
METHOD_WORD = {"GET": "get", "POST": "post", "PUT": "put", "DELETE": "del"}
ISO_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
NULL_ONLY = "Always null in Shopify's documented examples; type not documented."
TAGS = {"shop": "Shop", "location": "Locations", "product": "Products", "product-image": "Products",
        "inventoryitem": "Inventory", "inventorylevel": "Inventory", "order": "Orders",
        "customer": "Customers", "gift-card": "GiftCards"}
TAG_DESCRIPTIONS = {
    "Customers": "Customers (protected customer data approval required)",
    "GiftCards": "Gift cards (requires the gift_cards access scope)",
    "Inventory": "Inventory items and levels per location",
    "Locations": "Store and warehouse locations",
    "Orders": "Orders (last 60 days unless read_all_orders is granted)",
    "Products": "Product reads and product images (product writes are GraphQL-only)",
    "Shop": "Shop settings",
}


def clean(s):
    return s.replace("\\_", "_").replace("​", "").replace("\\&", "&").replace("\\*", "*").strip()


def fetch(slug):
    # curl, not urllib: urllib takes ~20 s per request to shopify.dev on macOS.
    url = DOC_URL.format(API_VERSION, slug)
    return subprocess.run(["curl", "-sfL", "--max-time", "60", url],
                          check=True, capture_output=True, text=True).stdout


def parse_fields(block):
    """Parse '***'-separated name / **flags** / description entries."""
    fields = {}
    for chunk in block.split("***"):
        lines = [ln.strip() for ln in chunk.strip().splitlines() if ln.strip()]
        if not lines or lines[0].startswith("#") or lines[0] == "{}":
            continue
        name = clean(lines[0])
        if not re.fullmatch(r"[a-z0-9_\[\]]+", name):
            continue
        flags = [ln.strip("*").lower() for ln in lines[1:] if ln.startswith("**")]
        desc = " ".join(ln for ln in lines[1:] if not ln.startswith("**") and not ln.startswith("->"))
        desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc).strip()
        fields[name] = {"flags": flags, "description": desc[:400]}
    return fields


def infer(value):
    if isinstance(value, dict):
        return {"type": "object", "properties": {k: infer(v) for k, v in value.items()}}
    if isinstance(value, list):
        items = {}
        for v in value:
            items = merge(items, infer(v))
        return {"type": "array", "items": items}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, str):
        return {"type": "string", "format": "date-time"} if ISO_DATETIME.match(value) else {"type": "string"}
    # null in every documented example: type unknown, so leave the schema open.
    return {"description": NULL_ONLY}


def merge(a, b):
    """Union of two inferred schemas (objects merge properties; null widens to nullable)."""
    if not a:
        return b
    if not b:
        return a
    if a.get("type") == "object" and b.get("type") == "object":
        props = dict(a["properties"])
        for k, v in b["properties"].items():
            props[k] = merge(props.get(k, {}), v)
        return {**a, "properties": props}
    if a.get("type") == "array" and b.get("type") == "array":
        return {**a, "items": merge(a["items"], b["items"])}
    if a.get("description") == NULL_ONLY:
        return {**b, "nullable": True} if "type" in b else b
    if b.get("description") == NULL_ONLY:
        return {**a, "nullable": True} if "type" in a else a
    return a


def json_after(text, marker):
    m = re.search(re.escape(marker) + r"\s*JSON\s*```json\s*(HTTP/1\.1 (\d+)[^\n{]*)?\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        return None, None
    return int(m.group(2) or 200), json.loads(m.group(3))


def curl_body(text):
    m = re.search(r"```curl\s*curl -d '(\{.*?\})'", text, re.S)
    return json.loads(m.group(1)) if m else None


def singular(key):
    return key[:-1] if key.endswith("s") else key


def schema_name(key):
    return "".join(p.capitalize() for p in singular(key).split("_"))


def main():
    with open(os.path.join(SPEC_DIR, "endpoints.yaml")) as f:
        wanted = yaml.safe_load(f)

    paths, components, problems = {}, {}, []
    descriptions = {}  # schema name -> {prop: field}
    for slug, endpoints in wanted.items():
        page = fetch(slug)
        time.sleep(0.3)
        props_block = page.split("### Properties", 1)[1].split("## The ", 1)[0] if "### Properties" in page else ""
        prop_fields = parse_fields(props_block)

        # Endpoint list: method, path, summary.
        listed = {}
        ep_block = page.split("## Endpoints", 1)[1].split("\n***", 1)[0]
        for m, path, summary in re.findall(
                r"\* \[(get|post|put|del)\]\([^)]*\)\s*\n\s*\n\s*\[([^\]]+)\]\([^)]*\)\s*\n\s*\n\s*([^\n]+)", ep_block):
            path = clean(path).split("?")[0].replace("/admin/api/latest", "")
            listed[(m, path)] = summary.strip()

        sections = re.split(r"\n(?=## (?:get|post|put|del)[A-Z])", page)
        for entry in endpoints:
            method, path = entry.split(" ", 1)
            word = METHOD_WORD[method]
            summary = listed.get((word, path))
            if summary is None:
                problems.append(f"{slug}: {entry} not on the doc page")
                continue
            section = next((s for s in sections if s.startswith(f"## {word}{summary}")), None)
            if section is None:
                problems.append(f"{slug}: no section for {entry}")
                continue

            params_block = section.split("### Parameters", 1)[1].split("### Examples", 1)[0] \
                if "### Parameters" in section else ""
            fields = parse_fields(params_block)
            path_params = re.findall(r"\{(\w+)\}", path)
            parameters = [{"name": p, "in": "path", "required": True, "schema": {"type": "string"}}
                          for p in path_params]
            if method == "GET":
                for name, fld in fields.items():
                    if name in path_params or name == "api_version":
                        continue
                    ptype = next((t for t in ("integer", "boolean") if t in fld["flags"]), "string")
                    param = {"name": name, "in": "query", "required": "required" in fld["flags"],
                             "schema": {"type": ptype}}
                    if fld["description"]:
                        param["description"] = fld["description"]
                    parameters.append(param)

            status, response = json_after(section, "## Response")
            op = {
                "operationId": re.sub(r"[^A-Za-z]", "", summary.title())[:1].lower()
                               + re.sub(r"[^A-Za-z]", "", summary.title())[1:],
                "summary": summary,
                "tags": [TAGS[slug]],
                "externalDocs": {"url": DOC_URL.format(API_VERSION, slug).replace(".md", "")},
            }
            if parameters:
                op["parameters"] = parameters
            if method in ("POST", "PUT"):
                body = curl_body(section)
                if body is None:
                    problems.append(f"{slug}: no request example for {entry}")
                else:
                    op["requestBody"] = {"required": True, "content": {"application/json": {
                        "schema": infer(body), "example": body}}}

            if response is None:
                if method == "DELETE":
                    op["responses"] = {"200": {"description": "Deleted"}}
                else:
                    problems.append(f"{slug}: no response example for {entry}")
                    continue
            else:
                resp_props = {}
                for key, value in response.items():
                    is_list = isinstance(value, list) and value and isinstance(value[0], dict)
                    if is_list or isinstance(value, dict):
                        name = schema_name(key)
                        # For lists, infer() merges every element so nulls in later items widen the type.
                        inferred = infer(value)["items"] if is_list else infer(value)
                        components[name] = merge(components.get(name, {}), inferred)
                        # Property docs belong to the page about this resource
                        # (product-image -> image, inventorylevel -> inventory_level).
                        if slug.replace("-", "").endswith(singular(key).replace("_", "")):
                            descriptions.setdefault(name, {}).update(prop_fields)
                        ref = {"$ref": f"#/components/schemas/{name}"}
                        resp_props[key] = {"type": "array", "items": ref} if isinstance(value, list) else ref
                    else:
                        resp_props[key] = infer(value)
                op["responses"] = {str(status or 200): {
                    "description": summary,
                    "content": {"application/json": {"schema": {"type": "object", "properties": resp_props},
                                                      "example": response}}}}
            op["responses"].update({
                "401": {"description": "Missing or invalid access token"},
                "403": {"description": "App lacks a required access scope or protected-data approval"},
                "404": {"description": "Not found"},
                "429": {"description": "Rate limited (leaky bucket); retry after the Retry-After header"},
            })
            if method == "GET" and path.endswith("s.json") and "{" not in path.rsplit("/", 1)[-1]:
                op["description"] = ("Paginated with cursors: follow the `Link` response header "
                                     "(`page_info`), and use `limit` (max 250).")
            paths.setdefault(path, {})[method.lower()] = op

    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(f"{len(problems)} problem(s); nothing written")

    # Attach descriptions / deprecated flags from each page's Properties list.
    for name, schema in components.items():
        for prop, fld in descriptions.get(name, {}).items():
            if prop in schema.get("properties", {}):
                target = schema["properties"][prop]
                if fld["description"]:
                    target["description"] = fld["description"]
                if "deprecated" in fld["flags"]:
                    target["deprecated"] = True

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": f"Shopify REST Admin API {API_VERSION} (agent contract, legacy)",
            "version": API_VERSION,
            "description": (
                "Legacy REST API. Shopify adds no new features here and requires new public apps to use "
                "GraphQL (see specs/shopify/graphql). Use these endpoints only for simple reads/writes "
                "already in use; transfers, shipments and product writes are GraphQL-only. "
                "Generated from Shopify's REST reference pages by scripts/build_shopify_rest.py; "
                "schemas are inferred from documented examples."
            ),
        },
        "externalDocs": {"url": f"https://shopify.dev/docs/api/admin-rest/{API_VERSION}"},
        "servers": [{
            "url": f"https://{{shop}}.myshopify.com/admin/api/{API_VERSION}",
            "variables": {"shop": {"default": "your-store", "description": "Store subdomain"}},
        }],
        "security": [{"accessToken": []}],
        "tags": [{"name": t, "description": TAG_DESCRIPTIONS[t]} for t in sorted(set(TAGS.values()))],
        "paths": dict(sorted(paths.items())),
        "components": {
            "securitySchemes": {"accessToken": {
                "type": "apiKey", "in": "header", "name": "X-Shopify-Access-Token",
                "description": ("Offline access token from OAuth. Authorize: "
                                "https://{shop}.myshopify.com/admin/oauth/authorize · Token: "
                                "https://{shop}.myshopify.com/admin/oauth/access_token"),
            }},
            "schemas": dict(sorted(components.items())),
        },
    }
    with open(os.path.join(SPEC_DIR, "openapi.json"), "w") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")
    ops = sum(len(v) for v in paths.values())
    print(f"wrote {len(paths)} paths, {ops} operations, {len(components)} schemas", file=sys.stderr)


if __name__ == "__main__":
    main()
