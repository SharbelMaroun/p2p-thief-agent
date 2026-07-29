"use strict";

// Independent reproduction of Python
// json.dumps(sort_keys=True, ensure_ascii=False, separators=(",", ":")), matching the
// reference simulator's canonical JSON for the commitment construction
// SHA256(canonical_json(payload) + "|" + nonce). Shares no code with the Thief Python
// serializer. (File name retained; this superseded the earlier ensure_ascii=True form.)

const { fail } = require("./errors");
const { validUnicode } = require("./jcs");

const SHORT = { 8: "\\b", 9: "\\t", 10: "\\n", 12: "\\f", 13: "\\r" };

function escapeUnicode(text) {
  validUnicode(text);
  let out = '"';
  for (const ch of text) {
    const cp = ch.codePointAt(0);
    if (ch === '"') out += '\\"';
    else if (ch === "\\") out += "\\\\";
    else if (cp in SHORT) out += SHORT[cp];
    else if (cp < 0x20) out += "\\u" + cp.toString(16).padStart(4, "0");
    else out += ch;
  }
  return out + '"';
}

function simCanonical(value) {
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "string") return escapeUnicode(value);
  if (typeof value === "number") {
    if (!Number.isInteger(value)) fail("MALFORMED", "commitment payload numbers must be integers");
    return String(value);
  }
  if (Array.isArray(value)) return `[${value.map(simCanonical).join(",")}]`;
  if (typeof value === "object") {
    const members = Object.keys(value)
      .sort()
      .map((key) => `${escapeUnicode(key)}:${simCanonical(value[key])}`);
    return `{${members.join(",")}}`;
  }
  fail("MALFORMED", `serializer cannot encode ${typeof value}`);
}

module.exports = { simCanonical, escapeUnicode };
