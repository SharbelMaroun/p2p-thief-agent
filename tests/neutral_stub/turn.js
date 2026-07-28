"use strict";

const { fail } = require("./errors");
const { commitmentHash } = require("./hashes");
const { canonicalize } = require("./jcs");
const {
  closed, coordinate, identifier, lowerHex, safeInt, text,
} = require("./schema");

const TURN_KEYS = ["step", "role", "commitment_sha256", "hint", "barrier"];
const PAYLOAD_KEYS = [
  "domain", "game_id", "game_uid", "sub_game_number", "step", "sender_group_id",
  "role", "position", "move", "intent", "hint", "barrier",
];

function barrier(value, label, context) {
  if (value === null) return null;
  const result = closed(value, ["position"], label);
  coordinate(result.position, `${label}.position`, context);
  return result;
}

function turnBody(value, context) {
  const body = closed(value, TURN_KEYS, "body");
  safeInt(body.step, "body.step", 1);
  lowerHex(body.commitment_sha256, 64, "body.commitment_sha256");
  text(body.hint, "body.hint", 4096);
  barrier(body.barrier, "body.barrier", context);
  if (body.role !== context.remote_role) {
    fail("IDENTITY_MISMATCH", "turn role does not match sender");
  }
  return body;
}

function payload(value, context) {
  const result = closed(value, PAYLOAD_KEYS, "payload");
  if (result.domain !== "p2p-thief/move-commitment/v1") {
    fail("MALFORMED", "payload domain mismatch");
  }
  identifier(result.game_id, "payload.game_id");
  identifier(result.game_uid, "payload.game_uid");
  identifier(result.sender_group_id, "payload.sender_group_id", 64);
  safeInt(result.sub_game_number, "payload.sub_game_number", 1, 6);
  safeInt(result.step, "payload.step", 1);
  coordinate(result.position, "payload.position", context);
  if (!["N", "S", "E", "W", "STAY"].includes(result.move)) {
    fail("MALFORMED", "payload move is invalid");
  }
  if (!["truth", "lie"].includes(result.intent)) {
    fail("MALFORMED", "payload intent is invalid");
  }
  if (!["police", "thief"].includes(result.role)) {
    fail("MALFORMED", "payload role is invalid");
  }
  text(result.hint, "payload.hint", 4096);
  barrier(result.barrier, "payload.barrier", context);
  if (result.game_id !== context.game_id || result.game_uid !== context.game_uid ||
      result.sub_game_number !== context.sub_game_number ||
      result.sender_group_id !== context.remote_group_id ||
      result.role !== context.remote_role) {
    fail("COMMITMENT_MISMATCH", "payload identity does not match session");
  }
  return result;
}

function revealHash(value, nonce, context) {
  const result = payload(value, context);
  lowerHex(nonce, 64, "nonce");
  return commitmentHash(result, nonce);
}

function sameValue(first, second) {
  return canonicalize(first) === canonicalize(second);
}

module.exports = { payload, revealHash, sameValue, turnBody };
