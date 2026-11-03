#!/usr/bin/env python3
"""Trim an OpenAPI 3 document to the operations carrying the given tags.

Keeps every component schema the kept operations reference (transitively),
drops deprecated operations and vendor test fixtures (x-unitTests), and limits
OAuth scopes to the ones the kept operations use.

Usage:
  scripts/trim_openapi.py <in.json> <out.json> --tags Tag1,Tag2 \
      [--server URL --server-description TEXT ...] [--keep-deprecated]
"""
import argparse
import json
import sys

HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
DROP_KEYS = {"x-unitTests"}


def strip(node):
    if isinstance(node, dict):
        return {k: strip(v) for k, v in node.items() if k not in DROP_KEYS}
    if isinstance(node, list):
        return [strip(v) for v in node]
    return node


def refs_in(node, found):
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/"):
            found.add(ref)
        for v in node.values():
            refs_in(v, found)
    elif isinstance(node, list):
        for v in node:
            refs_in(v, found)


def resolve(doc, ref):
    node = doc
    for part in ref[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


# Stands in for a schema the upstream document references but never defines (a dangling $ref).
def placeholder(ref):
    return {
        "type": "object",
        "description": f"Not defined in the upstream spec: it references {ref} but has no such schema. "
                       "Placeholder added by trim_openapi.py; check the vendor's API reference for the real shape.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--tags", required=True, help="comma-separated operation tags to keep")
    ap.add_argument("--server", action="append", default=[], help="server URL (repeatable)")
    ap.add_argument("--server-description", action="append", default=[])
    ap.add_argument("--keep-deprecated", action="store_true", help="keep operations marked deprecated")
    args = ap.parse_args()

    doc = json.load(open(args.src))
    keep_tags = {t.strip() for t in args.tags.split(",") if t.strip()}

    paths = {}
    used_scopes = set()
    for path, item in doc["paths"].items():
        kept = {}
        for method, op in item.items():
            if method in HTTP_METHODS and op.get("deprecated") and not args.keep_deprecated:
                continue
            if method in HTTP_METHODS and keep_tags & set(op.get("tags", [])):
                kept[method] = strip(op)
                for req in op.get("security", []):
                    for scopes in req.values():
                        used_scopes.update(scopes)
            elif method not in HTTP_METHODS:
                kept[method] = item[method]
        if any(m in HTTP_METHODS for m in kept):
            paths[path] = kept

    # Walk $refs transitively from the kept paths.
    pending = set()
    refs_in(paths, pending)
    seen = set()
    dangling = set()
    while pending:
        ref = pending.pop()
        if ref in seen:
            continue
        seen.add(ref)
        target = resolve(doc, ref)
        if target is None:
            dangling.add(ref)
        else:
            refs_in(target, pending)

    components = {}
    for ref in sorted(seen):
        _, _, section, name = ref.split("/", 3)
        target = resolve(doc, ref)
        components.setdefault(section, {})[name] = placeholder(ref) if target is None else strip(target)

    schemes = json.loads(json.dumps(doc.get("components", {}).get("securitySchemes", {})))
    for scheme in schemes.values():
        for flow in scheme.get("flows", {}).values():
            if "scopes" in flow:
                flow["scopes"] = {k: v for k, v in flow["scopes"].items() if k in used_scopes}
    if schemes:
        components["securitySchemes"] = schemes

    info = dict(doc["info"])
    out = {"openapi": doc["openapi"], "info": info}
    # Some vendors nest externalDocs under info, which OpenAPI does not allow; move it to the root.
    if "externalDocs" in info:
        out["externalDocs"] = info.pop("externalDocs")
    elif "externalDocs" in doc:
        out["externalDocs"] = doc["externalDocs"]
    if args.server:
        descs = args.server_description + [None] * len(args.server)
        out["servers"] = [
            {"url": u, **({"description": d} if d else {})} for u, d in zip(args.server, descs)
        ]
    elif "servers" in doc:
        out["servers"] = doc["servers"]
    out["tags"] = [{"name": t} for t in sorted(keep_tags)]
    out["paths"] = paths
    out["components"] = components

    with open(args.dst, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    ops = sum(1 for item in paths.values() for m in item if m in HTTP_METHODS)
    missing = keep_tags - {t for item in paths.values() for m, op in item.items()
                           if m in HTTP_METHODS for t in op.get("tags", [])}
    print(f"kept {len(paths)} paths, {ops} operations, {len(seen)} components", file=sys.stderr)
    if missing:
        print(f"WARNING: no operations for tags: {sorted(missing)}", file=sys.stderr)
    if dangling:
        print(f"WARNING: upstream references undefined schemas, placeholders added: {sorted(dangling)}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
