"use strict";

const { fail, rejection } = require("./errors");
const { idempotencyHash } = require("./hashes");
const { acceptance, validateOffer } = require("./offer");
const { closed, identifier, lowerHex, safeInt } = require("./schema");

const ACTIVE_KEYS = [
  "now_ms", "game_id", "game_uid", "sub_game_number", "group_a_id", "group_a_role",
  "group_a_git_commit", "group_b_id", "group_b_role", "group_b_git_commit",
  "agreed_configuration_sha256",
];

function activeContext(value) {
  const active = closed(value, ACTIVE_KEYS, "negotiation context");
  safeInt(active.now_ms, "now_ms");
  identifier(active.game_id, "game_id");
  identifier(active.game_uid, "game_uid");
  safeInt(active.sub_game_number, "sub_game_number", 1, 6);
  identifier(active.group_a_id, "group_a_id", 64);
  identifier(active.group_b_id, "group_b_id", 64);
  lowerHex(active.group_a_git_commit, 40, "group_a_git_commit");
  lowerHex(active.group_b_git_commit, 40, "group_b_git_commit");
  lowerHex(active.agreed_configuration_sha256, 64, "agreed_configuration_sha256");
  if (active.group_a_id === active.group_b_id ||
      new Set([active.group_a_role, active.group_b_role]).size !== 2 ||
      !["police", "thief"].includes(active.group_a_role) ||
      !["police", "thief"].includes(active.group_b_role)) {
    fail("IDENTITY_MISMATCH", "negotiation context participants are invalid");
  }
  return active;
}

function direction(active, offer) {
  if (offer.proposer_group_id === active.group_a_id) {
    return {
      now_ms: active.now_ms,
      game_id: active.game_id,
      game_uid: active.game_uid,
      sub_game_number: active.sub_game_number,
      local_group_id: active.group_b_id,
      local_role: active.group_b_role,
      remote_group_id: active.group_a_id,
      remote_role: active.group_a_role,
      agreed_configuration_sha256: active.agreed_configuration_sha256,
      remote_git_commit: active.group_a_git_commit,
    };
  }
  if (offer.proposer_group_id === active.group_b_id) {
    return {
      now_ms: active.now_ms,
      game_id: active.game_id,
      game_uid: active.game_uid,
      sub_game_number: active.sub_game_number,
      local_group_id: active.group_a_id,
      local_role: active.group_a_role,
      remote_group_id: active.group_b_id,
      remote_role: active.group_b_role,
      agreed_configuration_sha256: active.agreed_configuration_sha256,
      remote_git_commit: active.group_b_git_commit,
    };
  }
  fail("IDENTITY_MISMATCH", "offer proposer is not an active participant");
}

function mirrored(first, second) {
  if (first.negotiation_id !== second.negotiation_id) {
    fail("OUT_OF_ORDER", "mirrored offers use different negotiation IDs");
  }
  const fields = [
    "game_source_b64", "game_source_sha256", "rate_limits_source_b64",
    "rate_limits_source_sha256", "agreed_configuration_sha256",
  ];
  if (fields.some((field) => first.configuration[field] !== second.configuration[field])) {
    fail("CONFIG_MISMATCH", "mirrored offers use different configuration");
  }
}

function negotiateSequence(activeValue, offers) {
  const active = activeContext(activeValue);
  if (!Array.isArray(offers)) fail("MALFORMED", "offers must be an array");
  const cache = new Map();
  const accepted = new Map();
  const results = [];
  for (const offer of offers) {
    try {
      const validated = validateOffer(offer, direction(active, offer));
      const key = `${offer.proposer_group_id}|${offer.message_id}`;
      const digest = idempotencyHash(offer);
      if (cache.has(key)) {
        const cached = cache.get(key);
        if (cached.digest !== digest) {
          fail("IDEMPOTENCY_CONFLICT", "offer message_id was reused");
        }
        results.push(cached.result);
        continue;
      }
      if (accepted.has(offer.proposer_group_id)) {
        fail("REPLAYED_MESSAGE", "offer direction was already accepted");
      }
      if (accepted.size === 1) mirrored([...accepted.values()][0].offer, offer);
      const result = acceptance(validated);
      cache.set(key, { digest, result });
      accepted.set(offer.proposer_group_id, { offer, result });
      results.push(result);
    } catch (error) {
      results.push(rejection(offer, error));
    }
  }
  return { results, ready: accepted.size === 2 };
}

module.exports = { ACTIVE_KEYS, negotiateSequence };
