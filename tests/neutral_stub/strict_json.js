"use strict";

const { TextDecoder } = require("node:util");
const { fail } = require("./errors");
const { validUnicode } = require("./jcs");
class Parser {
  constructor(text, maximumDepth = 128) {
    this.text = text;
    this.index = 0;
    this.maximumDepth = maximumDepth;
  }

  whitespace() {
    while (/[ \t\r\n]/.test(this.text[this.index] || "")) this.index += 1;
  }

  parse() {
    this.whitespace();
    const result = this.value(0);
    this.whitespace();
    if (this.index !== this.text.length) fail("MALFORMED", "trailing JSON data");
    return result;
  }

  value(depth) {
    const character = this.text[this.index];
    if (character === "{") return this.object(depth + 1);
    if (character === "[") return this.array(depth + 1);
    if (character === '"') return this.string();
    for (const [literal, value] of [["true", true], ["false", false], ["null", null]]) {
      if (this.text.startsWith(literal, this.index)) {
        this.index += literal.length;
        return value;
      }
    }
    return this.number();
  }

  container(depth) {
    if (depth > this.maximumDepth) fail("MALFORMED", "JSON exceeds maximum depth");
  }

  object(depth) {
    this.container(depth);
    this.index += 1;
    this.whitespace();
    const result = Object.create(null);
    const names = new Set();
    if (this.text[this.index] === "}") {
      this.index += 1;
      return result;
    }
    while (true) {
      if (this.text[this.index] !== '"') fail("MALFORMED", "object name must be text");
      const name = this.string();
      if (names.has(name)) fail("MALFORMED", `duplicate JSON member ${name}`);
      names.add(name);
      this.whitespace();
      if (this.text[this.index] !== ":") fail("MALFORMED", "missing object colon");
      this.index += 1;
      this.whitespace();
      result[name] = this.value(depth);
      this.whitespace();
      if (this.text[this.index] === "}") {
        this.index += 1;
        return result;
      }
      if (this.text[this.index] !== ",") fail("MALFORMED", "missing object comma");
      this.index += 1;
      this.whitespace();
    }
  }

  array(depth) {
    this.container(depth);
    this.index += 1;
    this.whitespace();
    const result = [];
    if (this.text[this.index] === "]") {
      this.index += 1;
      return result;
    }
    while (true) {
      result.push(this.value(depth));
      this.whitespace();
      if (this.text[this.index] === "]") {
        this.index += 1;
        return result;
      }
      if (this.text[this.index] !== ",") fail("MALFORMED", "missing array comma");
      this.index += 1;
      this.whitespace();
    }
  }

  string() {
    const start = this.index;
    this.index += 1;
    while (this.index < this.text.length) {
      const character = this.text[this.index];
      if (character === '"') {
        this.index += 1;
        let result;
        try {
          result = JSON.parse(this.text.slice(start, this.index));
        } catch {
          fail("MALFORMED", "invalid JSON string");
        }
        validUnicode(result);
        return result;
      }
      if (character.charCodeAt(0) < 0x20) fail("MALFORMED", "unescaped control character");
      if (character === "\\") {
        this.index += this.text[this.index + 1] === "u" ? 6 : 2;
      } else {
        this.index += 1;
      }
    }
    fail("MALFORMED", "unterminated JSON string");
  }

  number() {
    const match = this.text.slice(this.index).match(
      /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/,
    );
    if (!match) fail("MALFORMED", "invalid JSON value");
    this.index += match[0].length;
    const result = Number(match[0]);
    if (!Number.isFinite(result)) fail("MALFORMED", "nonfinite JSON number");
    if (!/[.eE]/.test(match[0]) && !Number.isSafeInteger(result)) {
      fail("MALFORMED", "integer exceeds safe range");
    }
    return result;
  }
}

function strictParseBytes(bytes, maximumDepth = 128) {
  if (bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) {
    fail("MALFORMED", "JSON must not contain a BOM");
  }
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    fail("MALFORMED", "JSON must be valid UTF-8");
  }
  return new Parser(text, maximumDepth).parse();
}

module.exports = { strictParseBytes };
