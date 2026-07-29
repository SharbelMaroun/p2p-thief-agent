"use strict";

const { fail } = require("./errors");
const { closed, identifier, text } = require("./schema");
const { record } = require("./hashes");

function controlBody(value) {
  if (!record(value)) fail("MALFORMED", "body must be an object");
  if (value.control === "heartbeat") {
    return closed(value, ["control"], "body");
  }
  if (value.control !== "abort") {
    fail("MALFORMED", "body.control must be heartbeat or abort");
  }
  const body = closed(value, ["control", "code", "reason"], "body");
  identifier(body.code, "body.code", 64);
  text(body.reason, "body.reason", 512);
  return body;
}

module.exports = { controlBody };
