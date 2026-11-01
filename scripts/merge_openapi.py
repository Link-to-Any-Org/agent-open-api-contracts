#!/usr/bin/env python3
"""Merge several small OpenAPI 3 documents into one.

Inputs can be .json files or .md pages that embed the spec in a ```json block
under an "OpenAPI definition" heading (the ReadMe-hosted docs format used by
Lightspeed X-Series). info, servers, security and externalDocs come from the
first input; paths, tags and components are unioned.

Fails if two inputs define the same path+method or the same component name
with different content, so a silent overwrite can never happen.

Usage:
  scripts/merge_openapi.py <out.json> <in1.md|json> [<in2> ...] [--title TEXT]
"""
import argparse
import json
import re
import sys

HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
MD_SPEC = re.compile(r"#\s*OpenAPI definition\s*```json\s*(.*?)```", re.S)


def load(path):
    text = open(path).read()
    if path.endswith(".md"):
        m = MD_SPEC.search(text)
        if not m:
            sys.exit(f"{path}: no OpenAPI definition block found")
        text = m.group(1)
    return json.loads(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dst")
    ap.add_argument("srcs", nargs="+")
    ap.add_argument("--title")
    args = ap.parse_args()

    out = None
    origin = {}  # "path METHOD" or "components/section/name" -> source file
    tags = {}
    errors = []

    for src in args.srcs:
        doc = load(src)
        if out is None:
            out = {k: doc[k] for k in ("openapi", "info", "servers", "security", "externalDocs") if k in doc}
            out["paths"] = {}
            out["components"] = {}
        elif doc.get("openapi") != out["openapi"] or doc.get("servers") != out.get("servers"):
            errors.append(f"{src}: openapi version or servers differ from {args.srcs[0]}")

        for t in doc.get("tags", []):
            tags.setdefault(t["name"], t)

        for path, item in doc.get("paths", {}).items():
            target = out["paths"].setdefault(path, {})
            for method, op in item.items():
                key = f"{path} {method.upper()}"
                if method in target and target[method] != op:
                    errors.append(f"{key}: defined differently in {origin.get(key)} and {src}")
                    continue
                target[method] = op
                if method in HTTP_METHODS:
                    origin.setdefault(key, src)

        for section, entries in doc.get("components", {}).items():
            target = out["components"].setdefault(section, {})
            for name, value in entries.items():
                key = f"components/{section}/{name}"
                if name in target and target[name] != value:
                    errors.append(f"{key}: defined differently in {origin.get(key)} and {src}")
                    continue
                target[name] = value
                origin.setdefault(key, src)

    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"{len(errors)} conflict(s); nothing written")

    if args.title:
        out["info"] = {**out["info"], "title": args.title}
    out["tags"] = [tags[n] for n in sorted(tags)]
    out["paths"] = dict(sorted(out["paths"].items()))
    for section in out["components"]:
        out["components"][section] = dict(sorted(out["components"][section].items()))

    with open(args.dst, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    ops = sum(1 for item in out["paths"].values() for m in item if m in HTTP_METHODS)
    schemas = len(out["components"].get("schemas", {}))
    print(f"merged {len(args.srcs)} inputs: {len(out['paths'])} paths, {ops} operations, {schemas} schemas",
          file=sys.stderr)


if __name__ == "__main__":
    main()
