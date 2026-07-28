"use strict";

const { createHash } = require("node:crypto");
const { fail } = require("./errors");
const { canonicalize } = require("./jcs");
const { strictParseBytes } = require("./strict_json");

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function decodeBase64(encoded) {
  const pattern = /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/;
  if (typeof encoded !== "string" || encoded.length % 4 !== 0 || !pattern.test(encoded)) {
    fail("MALFORMED", "configuration source must be canonical padded base64");
  }
  const bytes = Buffer.from(encoded, "base64");
  if (bytes.toString("base64") !== encoded) fail("MALFORMED", "noncanonical base64");
  return bytes;
}

function decodeSource(encoded, label) {
  const bytes = decodeBase64(encoded);
  const value = strictParseBytes(bytes, 64);
  if (!bytes.equals(Buffer.from(canonicalize(value), "utf8"))) {
    fail("CONFIG_MISMATCH", `${label} is not exact RFC 8785 JCS`);
  }
  return { bytes, value };
}

function sourceHash(logicalName, bytes) {
  const prefix = Buffer.from(`p2p-thief/config-source/${logicalName}/v1|`, "ascii");
  return sha256(Buffer.concat([prefix, bytes]));
}

function configHash(game, rateLimits) {
  if (!record(game) || !record(rateLimits)) {
    fail("CONFIG_MISMATCH", "configuration sources must contain objects");
  }
  return valueHash({
    domain: "p2p-thief/agreed-config/v1",
    game,
    rate_limits: rateLimits,
  });
}

function valueHash(value) {
  return sha256(Buffer.from(canonicalize(value), "utf8"));
}

function commitmentHash(payload, nonce) {
  return sha256(Buffer.concat([
    Buffer.from(canonicalize(payload), "utf8"),
    Buffer.from(`|${nonce}`, "ascii"),
  ]));
}

function auditHash(context, records) {
  return valueHash({
    domain: "p2p-thief/final-audit/v1",
    game_id: context.game_id,
    game_uid: context.game_uid,
    sub_game_number: context.sub_game_number,
    sender_group_id: context.remote_group_id,
    records,
  });
}

function idempotencyHash(message) {
  return valueHash({ domain: "p2p-thief/idempotency/v1", message });
}

function record(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

module.exports = {
  auditHash, commitmentHash, configHash, decodeBase64, decodeSource,
  idempotencyHash, record, sha256, sourceHash, valueHash,
};
