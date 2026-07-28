"use strict";

const { fail } = require("./errors");

function validUnicode(text) {
  for (let index = 0; index < text.length; index += 1) {
    const unit = text.charCodeAt(index);
    if (unit >= 0xd800 && unit <= 0xdbff) {
      const next = text.charCodeAt(index + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) {
        fail("MALFORMED", "unpaired high surrogate");
      }
      index += 1;
    } else if (unit >= 0xdc00 && unit <= 0xdfff) {
      fail("MALFORMED", "unpaired low surrogate");
    }
  }
}

function canonicalize(value) {
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "string") {
    validUnicode(value);
    return JSON.stringify(value);
  }
  if (typeof value === "number") {
    if (!Number.isFinite(value)) fail("MALFORMED", "JCS number must be finite");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const members = Object.keys(value).sort().map((key) => {
      validUnicode(key);
      return `${JSON.stringify(key)}:${canonicalize(value[key])}`;
    });
    return `{${members.join(",")}}`;
  }
  fail("MALFORMED", `JCS cannot encode ${typeof value}`);
}

function containerDepth(value) {
  const children = Array.isArray(value)
    ? value
    : value !== null && typeof value === "object" ? Object.values(value) : null;
  if (children === null) return 0;
  let maximum = 0;
  for (const child of children) maximum = Math.max(maximum, containerDepth(child));
  return 1 + maximum;
}

function requireLimits(value, maximumBytes, maximumDepth = 64) {
  if (Buffer.byteLength(canonicalize(value), "utf8") > maximumBytes) {
    fail("MALFORMED", "argument exceeds byte limit");
  }
  if (containerDepth(value) > maximumDepth) {
    fail("MALFORMED", "argument exceeds depth limit");
  }
}

module.exports = { canonicalize, requireLimits, validUnicode };
