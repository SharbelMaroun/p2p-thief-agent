"use strict";

const { fail } = require("./errors");
const { requireLimits, validUnicode } = require("./jcs");
const { record } = require("./hashes");

const PROFILE = "p2p-thief-option-b";
const VERSION = "1.0";
const REQUIRED_CAPABILITIES = ["negotiate", "receive_move", "submit_audit"];
const PRIVATE_FIELDS = new Set(["payload", "nonce", "position", "move", "intent", "verdict"]);
const ENVELOPE_KEYS = [
  "profile", "version", "message_id", "sent_at_ms", "expires_at_ms", "game_uid",
  "sub_game_number", "sender_group_id", "recipient_group_id", "type", "body",
];

function closed(value, keys, label) {
  if (!record(value)) fail("MALFORMED", `${label} must be an object`);
  const allowed = new Set(keys);
  const missing = keys.filter((key) => !Object.hasOwn(value, key)).sort();
  if (missing.length) fail("MALFORMED", `${label} is missing ${missing[0]}`);
  const unknown = Object.keys(value).filter((key) => !allowed.has(key)).sort();
  if (unknown.length) fail("UNKNOWN_FIELD", `${label} has unknown field ${unknown[0]}`);
  return value;
}

function text(value, label, maximum = null, nonempty = false) {
  if (typeof value !== "string") fail("MALFORMED", `${label} must be text`);
  validUnicode(value);
  const length = [...value].length;
  if ((nonempty && length === 0) || (maximum !== null && length > maximum)) {
    fail("MALFORMED", `${label} has invalid length`);
  }
  return value;
}

function identifier(value, label, maximum = 128) {
  text(value, label);
  const expression = new RegExp(`^[A-Za-z0-9][A-Za-z0-9._-]{0,${maximum - 1}}$`);
  if (!expression.test(value)) fail("MALFORMED", `${label} is not an ASCII identifier`);
  return value;
}

function lowerHex(value, length, label) {
  if (typeof value !== "string" || !new RegExp(`^[0-9a-f]{${length}}$`).test(value)) {
    fail("MALFORMED", `${label} must be ${length} lowercase hex characters`);
  }
  return value;
}

function safeInt(value, label, minimum = 0, maximum = Number.MAX_SAFE_INTEGER) {
  if (!Number.isSafeInteger(value) || Object.is(value, -0) ||
      value < minimum || value > maximum) {
    fail("MALFORMED", `${label} must be an integer from ${minimum} to ${maximum}`);
  }
  return value;
}

function exactArray(value, expected, code, label) {
  if (!Array.isArray(value) || value.length !== expected.length ||
      value.some((item, index) => item !== expected[index])) {
    fail(code, `${label} does not match`);
  }
}

function privateScan(value, path = [], allow = []) {
  if (Array.isArray(value)) {
    for (const child of value) privateScan(child, path, allow);
    return;
  }
  if (!record(value)) return;
  for (const [key, child] of Object.entries(value)) {
    const next = [...path, key];
    const joined = next.join(".");
    const allowed = joined === "body.barrier.position" || allow.includes(joined);
    if (PRIVATE_FIELDS.has(key) && !allowed) {
      fail("PRIVATE_FIELD_LEAK", `private field ${joined}`);
    }
    privateScan(child, next, allow);
  }
}

function coordinate(value, label, context) {
  if (!Array.isArray(value) || value.length !== 2) {
    fail("MALFORMED", `${label} must be a coordinate`);
  }
  const lower = context.axis_start_index;
  const upper = lower + context.grid_size - 1;
  return [
    safeInt(value[0], `${label}[0]`, lower, upper),
    safeInt(value[1], `${label}[1]`, lower, upper),
  ];
}

function envelope(value, expectedType, nowMs, context, maximumBytes, scan = true, allow = []) {
  requireLimits(value, maximumBytes, 64);
  if (scan) privateScan(value, [], allow);
  const message = closed(value, ENVELOPE_KEYS, "message");
  lowerHex(message.message_id, 32, "message_id");
  const sent = safeInt(message.sent_at_ms, "sent_at_ms");
  const expires = safeInt(message.expires_at_ms, "expires_at_ms");
  identifier(message.game_uid, "game_uid");
  safeInt(message.sub_game_number, "sub_game_number", 1, 6);
  identifier(message.sender_group_id, "sender_group_id", 64);
  identifier(message.recipient_group_id, "recipient_group_id", 64);
  if (expires <= sent) fail("MALFORMED", "expiry must follow sent time");
  if (message.profile !== PROFILE) fail("UNSUPPORTED_PROFILE", "profile mismatch");
  if (message.version !== VERSION) fail("UNSUPPORTED_VERSION", "version mismatch");
  if (message.game_uid !== context.game_uid ||
      message.sub_game_number !== context.sub_game_number ||
      message.sender_group_id !== context.remote_group_id ||
      message.recipient_group_id !== context.local_group_id) {
    fail("IDENTITY_MISMATCH", "message identity does not match session");
  }
  if (safeInt(nowMs, "now_ms") > expires) fail("EXPIRED", "message has expired");
  if (message.type !== expectedType) fail("OUT_OF_ORDER", `expected ${expectedType}`);
  return message;
}

module.exports = {
  PROFILE, REQUIRED_CAPABILITIES, VERSION, closed, coordinate, envelope, exactArray,
  identifier, lowerHex, privateScan, safeInt, text,
};
