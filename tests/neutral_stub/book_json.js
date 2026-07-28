"use strict";

// Independent reproduction of Python json.dumps(sort_keys=True,
// separators=(",", ":")) with the book's default ensure_ascii=True, matching the
// project book Chapter 5.3 commit construction byte-for-byte. Shares no code with the
// Thief Python serializer.

const { fail } = require("./errors");
const { validUnicode } = require("./jcs");

const SHORT = { 8: "\\b", 9: "\\t", 10: "\\n", 12: "\\f", 13: "\\r" };

function escapeAscii(text) {
  validUnicode(text);
  let out = '"';
  for (const ch of text) {
    const cp = ch.codePointAt(0);
    if (ch === '"') out += '\\"';
    else if (ch === "\\") out += "\\\\";
    else if (cp in SHORT) out += SHORT[cp];
    else if (cp < 0x20) out += "\\u" + cp.toString(16).padStart(4, "0");
    else if (cp <= 0x7e) out += ch;
    else if (cp < 0x10000) out += "\\u" + cp.toString(16).padStart(4, "0");
    else {
      const n = cp - 0x10000;
      const hi = 0xd800 | ((n >> 10) & 0x3ff);
      const lo = 0xdc00 | (n & 0x3ff);
      out += "\\u" + hi.toString(16).padStart(4, "0") + "\\u" + lo.toString(16).padStart(4, "0");
    }
  }
  return out + '"';
}

function bookCanonical(value) {
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "string") return escapeAscii(value);
  if (typeof value === "number") {
    if (!Number.isInteger(value)) fail("MALFORMED", "book payload numbers must be integers");
    return String(value);
  }
  if (Array.isArray(value)) return `[${value.map(bookCanonical).join(",")}]`;
  if (typeof value === "object") {
    const members = Object.keys(value)
      .sort()
      .map((key) => `${escapeAscii(key)}:${bookCanonical(value[key])}`);
    return `{${members.join(",")}}`;
  }
  fail("MALFORMED", `book serializer cannot encode ${typeof value}`);
}

module.exports = { bookCanonical, escapeAscii };
