"use strict";

const { fail } = require("./errors");
const { auditHash } = require("./hashes");
const { closed, lowerHex, safeInt } = require("./schema");
const { payload, revealHash, sameValue } = require("./turn");

const RECORD_KEYS = [
  "step", "turn_message_id", "commitment_sha256", "payload", "nonce",
];

function verifyRecords(records, turns, nextStep, context) {
  if (!Array.isArray(records) || records.length !== turns.size) {
    fail("OUT_OF_ORDER", "audit must cover every locked turn");
  }
  const steps = records.map((record) => record && record.step);
  const expected = Array.from({ length: nextStep - 1 }, (_, index) => index + 1);
  if (!sameValue(steps, expected)) fail("OUT_OF_ORDER", "audit steps are not complete");
  const nonces = new Set();
  for (const value of records) {
    const record = closed(value, RECORD_KEYS, "audit record");
    const step = safeInt(record.step, "audit record step", 1);
    const turn = turns.get(step);
    lowerHex(record.turn_message_id, 32, "turn_message_id");
    lowerHex(record.commitment_sha256, 64, "commitment_sha256");
    lowerHex(record.nonce, 32, "nonce");
    const reveal = payload(record.payload, context);
    if (nonces.has(record.nonce)) fail("COMMITMENT_MISMATCH", "audit reuses nonce");
    nonces.add(record.nonce);
    if (!turn ||
        record.turn_message_id !== turn.message_id ||
        record.commitment_sha256 !== turn.commitment_sha256 ||
        reveal.step !== step ||
        reveal.role !== turn.role ||
        reveal.hint !== turn.hint ||
        !sameValue(reveal.barrier, turn.barrier) ||
        revealHash(reveal, record.nonce, context) !== turn.commitment_sha256) {
      fail("COMMITMENT_MISMATCH", "audit record does not match locked turn");
    }
  }
  return auditHash(context, records);
}

module.exports = { verifyRecords };
