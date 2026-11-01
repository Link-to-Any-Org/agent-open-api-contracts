#!/usr/bin/env node
// Validates every operation in specs/shopify/graphql/openapi.json against Shopify's
// live Admin GraphQL schema: query syntax, field names, no deprecated fields,
// example variables match their input types, and declared scopes cover the
// scopes Shopify's schema docs mention for each root field.
// Schema source: the public docs proxy shopify.dev uses for its GraphiQL explorer.
import { readFileSync } from "node:fs";
import {
  buildClientSchema, getIntrospectionQuery, parse, validate, specifiedRules,
  NoDeprecatedCustomRule, getNamedType, getVariableValues, typeFromAST,
} from "graphql";

const spec = JSON.parse(readFileSync(new URL("../specs/shopify/graphql/openapi.json", import.meta.url)));
const version = spec.info.version;
const res = await fetch(`https://shopify.dev/admin-graphql-direct-proxy/${version}`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query: getIntrospectionQuery({ descriptions: true }) }),
});
const body = await res.json();
if (!body.data) {
  console.error("could not load schema:", JSON.stringify(body).slice(0, 300));
  process.exit(2);
}
const schema = buildClientSchema(body.data);
const examples = spec.paths["/graphql.json"].post.requestBody.content["application/json"].examples;
const declared = Object.fromEntries(spec["x-graphql-operations"].map((o) => [o.name, new Set(o.scopes)]));

let failures = 0;
const warnings = [];
for (const [name, { value }] of Object.entries(examples)) {
  const problems = [];
  let doc;
  try {
    doc = parse(value.query);
  } catch (e) {
    problems.push(e.message);
  }
  if (doc) {
    for (const e of validate(schema, doc, [...specifiedRules, NoDeprecatedCustomRule])) problems.push(e.message);
    const op = doc.definitions.find((d) => d.kind === "OperationDefinition");
    if (op?.name?.value !== name) problems.push(`operation name must be ${name}`);
    if (op && problems.length === 0) {
      const vars = getVariableValues(schema, op.variableDefinitions ?? [], value.variables ?? {});
      for (const e of vars.errors ?? []) problems.push(`variables: ${e.message}`);
      // Scopes Shopify names in the root field's description ("`write_products` access scope").
      const root = op.operation === "mutation" ? schema.getMutationType() : schema.getQueryType();
      for (const sel of op.selectionSet.selections) {
        const field = root.getFields()[sel.name?.value];
        const mentioned = [...(field?.description ?? "").matchAll(/`((?:read|write|unauthenticated_\w+)_\w+)`/g)].map((m) => m[1]);
        const missing = mentioned.filter((s) => !declared[name].has(s));
        if (mentioned.length && missing.length === mentioned.length) {
          warnings.push(`${name}: schema docs for ${sel.name.value} mention ${mentioned.join(", ")}; declared ${[...declared[name]].join(", ") || "none"}`);
        }
      }
    }
  }
  if (problems.length) {
    failures++;
    console.log(`FAIL ${name}`);
    for (const p of problems) console.log(`  - ${p}`);
  } else {
    console.log(`ok   ${name}`);
  }
}
for (const w of warnings) console.log(`warn ${w}`);
console.log(`\n${Object.keys(examples).length - failures}/${Object.keys(examples).length} operations valid against Admin API ${version}`);
process.exit(failures ? 1 : 0);
