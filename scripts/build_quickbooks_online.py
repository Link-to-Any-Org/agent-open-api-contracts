#!/usr/bin/env python3
"""Build specs/quickbooks-online/openapi.json.

Intuit publishes no OpenAPI file for the QuickBooks Online Accounting API, but
its official Java SDK ships the XSD schemas the API is generated from. This
script:
  1. downloads those XSDs at a pinned SDK commit,
  2. converts the entity types the agent needs (and every type they use) into
     JSON Schema, following QBO's JSON conventions (ReferenceType -> {value,
     name, type}; XML attributes -> properties; fields Intuit labels as
     desktop-only are kept and flagged with x-intuit-products: [QBW]),
  3. merges them into the hand-written paths in openapi.base.yaml.

Usage: scripts/build_quickbooks_online.py
"""
import json
import os
import re
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

import yaml

SDK_COMMIT = "c4d5dfad23ffebf0302356876d0dc389708513a9"
XSD_URL = ("https://raw.githubusercontent.com/intuit/QuickBooks-V3-Java-SDK/"
           f"{SDK_COMMIT}/ipp-v3-java-data/src/main/xsd/{{}}.xsd")
XSD_FILES = ["IntuitBaseTypes", "IntuitNamesTypes", "Finance", "IntuitRestServiceDef"]

# Entity types exposed by openapi.base.yaml; everything they reference is pulled in.
ROOT_TYPES = [
    "Item", "InventoryAdjustment", "Customer", "Vendor", "Invoice", "SalesReceipt",
    "Estimate", "PurchaseOrder", "Department", "Attachable", "CompanyInfo", "Fault",
]

XS = "{http://www.w3.org/2001/XMLSchema}"
XS_TYPES = {
    "string": {"type": "string"}, "normalizedString": {"type": "string"},
    "token": {"type": "string"}, "anyURI": {"type": "string"},
    "base64Binary": {"type": "string", "format": "byte"},
    "boolean": {"type": "boolean"},
    "decimal": {"type": "number"}, "double": {"type": "number"}, "float": {"type": "number"},
    "int": {"type": "integer"}, "integer": {"type": "integer"}, "long": {"type": "integer"},
    "short": {"type": "integer"}, "positiveInteger": {"type": "integer"},
    "nonNegativeInteger": {"type": "integer"}, "unsignedInt": {"type": "integer"},
    "dateTime": {"type": "string", "format": "date-time"},
    "date": {"type": "string", "format": "date"},
    "time": {"type": "string"}, "anyType": {},
}
DESC_MAX = 300

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DIR = os.path.join(ROOT, "specs", "quickbooks-online")


def local(name):
    return name.split(":")[-1] if name else name


def doc_text(node):
    """QBO description from an xs:annotation, and whether Intuit labels it QBW-only."""
    ann = node.find(f"{XS}annotation/{XS}documentation")
    if ann is None or not ann.text:
        return "", False
    text = " ".join(ann.text.split())
    products = re.findall(r"Product:\s*(\w+)", text)
    qbw_only = bool(products) and not any(p in ("QBO", "ALL") for p in products)
    m = re.search(r"Product:\s*(?:QBO|ALL)\s*Description:\s*(.*?)(?=Product:|$)", text)
    desc = (m.group(1) if m else re.sub(r"Product:\s*\w+\s*Description:\s*", "", text)).strip()
    if len(desc) > DESC_MAX:
        desc = desc[:DESC_MAX].rsplit(" ", 1)[0] + "..."
    return desc, qbw_only


class Converter:
    def __init__(self, roots):
        self.complex, self.simple = {}, {}
        for r in roots:
            for node in r:
                if node.tag == f"{XS}complexType" and node.get("name"):
                    self.complex[node.get("name")] = node
                elif node.tag == f"{XS}simpleType" and node.get("name"):
                    self.simple[node.get("name")] = node
        self.schemas, self.pending = {}, []

    def ref(self, type_name):
        name = local(type_name)
        if name in XS_TYPES:
            return dict(XS_TYPES[name])
        if name in self.simple:
            return self.simple_schema(self.simple[name])
        if name in self.complex:
            if name not in self.schemas and name not in self.pending:
                self.pending.append(name)
            return {"$ref": f"#/components/schemas/{name}"}
        return {}

    def simple_schema(self, node):
        restr = node.find(f"{XS}restriction")
        if restr is None:
            return {"type": "string"}
        base = self.ref(restr.get("base"))
        enums = [e.get("value") for e in restr.findall(f"{XS}enumeration")]
        if enums:
            return {"type": "string", "enum": enums}
        return base or {"type": "string"}

    def add_particles(self, node, props, required):
        for child in node:
            tag = child.tag[len(XS):]
            if tag in ("sequence", "choice", "all"):
                self.add_particles(child, props, required if tag != "choice" else [])
            elif tag == "element" and child.get("name"):
                desc, qbw_only = doc_text(child)
                if child.get("type"):
                    schema = self.ref(child.get("type"))
                else:
                    inline = child.find(f"{XS}complexType")
                    schema = self.complex_body(inline) if inline is not None else {"type": "string"}
                if child.get("maxOccurs") not in (None, "0", "1"):
                    schema = {"type": "array", "items": schema}
                if desc or qbw_only:
                    extra = {"description": desc} if desc else {}
                    if qbw_only:
                        # Intuit's XSD labels are not reliable (e.g. Item.Active says QBW yet works in QBO),
                        # so keep the field and flag it rather than drop it.
                        extra["x-intuit-products"] = ["QBW"]
                    schema = {"allOf": [schema], **extra} if "$ref" in schema else {**schema, **extra}
                props[child.get("name")] = schema
                if child.get("minOccurs", "1") != "0" and required is not None:
                    required.append(child.get("name"))
            elif tag == "attribute" and child.get("name"):
                props[child.get("name")] = self.ref(child.get("type", "xs:string")) or {"type": "string"}

    def complex_body(self, node):
        props, required = {}, []
        for child in node:
            tag = child.tag[len(XS):]
            if tag in ("complexContent", "simpleContent"):
                ext = child.find(f"{XS}extension")
                if ext is None:
                    continue
                base = local(ext.get("base"))
                if tag == "simpleContent":
                    # QBO JSON puts the element's text in "value" (e.g. ReferenceType).
                    props["value"] = self.ref(base) or {"type": "string"}
                elif base in self.complex:
                    inherited = self.complex_body(self.complex[base])
                    props.update(inherited.get("properties", {}))
                    required.extend(inherited.get("required", []))
                self.add_particles(ext, props, required)
            elif tag in ("sequence", "choice", "all"):
                self.add_particles(child, props, required if tag != "choice" else [])
            elif tag == "attribute" and child.get("name"):
                props[child.get("name")] = self.ref(child.get("type", "xs:string")) or {"type": "string"}
        out = {"type": "object", "properties": props}
        if required:
            out["required"] = sorted(set(required))
        return out

    def build(self, roots):
        for r in roots:
            self.ref(r)
        while self.pending:
            name = self.pending.pop(0)
            node = self.complex[name]
            schema = self.complex_body(node)
            desc, _ = doc_text(node)
            if desc:
                schema["description"] = desc
            self.schemas[name] = schema
        return dict(sorted(self.schemas.items()))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        roots = []
        for name in XSD_FILES:
            path = os.path.join(tmp, f"{name}.xsd")
            urllib.request.urlretrieve(XSD_URL.format(name), path)
            roots.append(ET.parse(path).getroot())

    schemas = Converter(roots).build(ROOT_TYPES)

    with open(os.path.join(SPEC_DIR, "openapi.base.yaml")) as f:
        spec = yaml.safe_load(f)
    clash = set(schemas) & set(spec["components"].get("schemas", {}))
    if clash:
        sys.exit(f"hand-written schemas clash with generated ones: {sorted(clash)}")
    spec["components"]["schemas"] = {**spec["components"].get("schemas", {}), **schemas}

    with open(os.path.join(SPEC_DIR, "openapi.json"), "w") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")
    ops = sum(1 for p in spec["paths"].values() for m in p if m in ("get", "post", "put", "delete"))
    print(f"wrote {len(spec['paths'])} paths, {ops} operations, "
          f"{len(spec['components']['schemas'])} schemas ({len(schemas)} from XSD)", file=sys.stderr)


if __name__ == "__main__":
    main()
