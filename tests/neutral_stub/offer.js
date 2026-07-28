"use strict";

const { fail } = require("./errors");
const { configHash, decodeSource, record, sourceHash } = require("./hashes");
const { requireLimits } = require("./jcs");
const {
  PROFILE, REQUIRED_CAPABILITIES, VERSION, closed, exactArray, identifier, lowerHex,
  safeInt, text,
} = require("./schema");

const OFFER_KEYS = [
  "profile", "supported_versions", "negotiation_id", "message_id", "sent_at_ms",
  "expires_at_ms", "proposer_group_id", "proposer_role", "responder_group_id",
  "responder_role", "game_id", "game_uid", "sub_game_number",
  "required_capabilities", "optional_capabilities", "step_zero", "configuration",
];
const CONFIG_KEYS = [
  "game_source_b64", "game_source_sha256", "rate_limits_source_b64",
  "rate_limits_source_sha256", "agreed_configuration_sha256",
];
const STEP_KEYS = [
  "os", "cpu_cores", "cpu_frequency_mhz", "ram_mb", "gpu", "vram_mb", "llm_name",
  "code_version", "git_commit", "group_id", "role", "sub_game_number",
];
const CONTEXT_KEYS = [
  "now_ms", "game_id", "game_uid", "sub_game_number", "local_group_id", "local_role",
  "remote_group_id", "remote_role", "agreed_configuration_sha256", "remote_git_commit",
];

function offerContext(value) {
  const context = closed(value, CONTEXT_KEYS, "offer context");
  safeInt(context.now_ms, "now_ms");
  identifier(context.game_id, "game_id");
  identifier(context.game_uid, "game_uid");
  safeInt(context.sub_game_number, "sub_game_number", 1, 6);
  identifier(context.local_group_id, "local_group_id", 64);
  identifier(context.remote_group_id, "remote_group_id", 64);
  if (context.local_group_id === context.remote_group_id ||
      new Set([context.local_role, context.remote_role]).size !== 2 ||
      !["police", "thief"].includes(context.local_role) ||
      !["police", "thief"].includes(context.remote_role)) {
    fail("IDENTITY_MISMATCH", "offer context participants are invalid");
  }
  lowerHex(context.agreed_configuration_sha256, 64, "agreed_configuration_sha256");
  lowerHex(context.remote_git_commit, 40, "remote_git_commit");
  return context;
}

function stepZero(offer, context) {
  const step = closed(offer.step_zero, STEP_KEYS, "step_zero");
  for (const key of ["os", "gpu", "llm_name", "code_version"]) {
    text(step[key], `step_zero.${key}`, null, true);
  }
  for (const key of ["cpu_cores", "cpu_frequency_mhz", "ram_mb", "vram_mb"]) {
    safeInt(step[key], `step_zero.${key}`);
  }
  lowerHex(step.git_commit, 40, "step_zero.git_commit");
  return step;
}

function header(offer, context) {
  lowerHex(offer.negotiation_id, 32, "negotiation_id");
  lowerHex(offer.message_id, 32, "message_id");
  identifier(offer.proposer_group_id, "proposer_group_id", 64);
  identifier(offer.responder_group_id, "responder_group_id", 64);
  identifier(offer.game_id, "game_id");
  identifier(offer.game_uid, "game_uid");
  safeInt(offer.sub_game_number, "sub_game_number", 1, 6);
  const sent = safeInt(offer.sent_at_ms, "sent_at_ms");
  const expires = safeInt(offer.expires_at_ms, "expires_at_ms");
  if (expires <= sent) fail("MALFORMED", "expiry must follow sent time");
  const step = stepZero(offer, context);
  if (offer.profile !== PROFILE) fail("UNSUPPORTED_PROFILE", "profile mismatch");
  exactArray(offer.supported_versions, [VERSION], "UNSUPPORTED_VERSION", "versions");
  exactArray(
    offer.required_capabilities,
    REQUIRED_CAPABILITIES,
    "CAPABILITY_MISMATCH",
    "required capabilities",
  );
  const optional = offer.optional_capabilities;
  if (!Array.isArray(optional) || optional.length > 1 ||
      optional.some((item) => item !== "receive_control")) {
    fail("CAPABILITY_MISMATCH", "optional capabilities are invalid");
  }
  if (offer.game_id !== context.game_id || offer.game_uid !== context.game_uid ||
      offer.sub_game_number !== context.sub_game_number ||
      offer.proposer_group_id !== context.remote_group_id ||
      offer.proposer_role !== context.remote_role ||
      offer.responder_group_id !== context.local_group_id ||
      offer.responder_role !== context.local_role) {
    fail("IDENTITY_MISMATCH", "offer does not bind the active match");
  }
  if (step.group_id !== offer.proposer_group_id ||
      step.role !== offer.proposer_role ||
      step.sub_game_number !== offer.sub_game_number ||
      step.git_commit !== context.remote_git_commit) {
    fail("IDENTITY_MISMATCH", "step_zero does not bind the active proposer");
  }
}

function validateOffer(value, contextValue) {
  requireLimits(value, 65_536, 64);
  const offer = closed(value, OFFER_KEYS, "offer");
  const config = closed(offer.configuration, CONFIG_KEYS, "configuration");
  const context = offerContext(contextValue);
  header(offer, context);
  const game = decodeSource(config.game_source_b64, "game source");
  const rate = decodeSource(config.rate_limits_source_b64, "rate-limits source");
  if (!record(game.value) || !record(rate.value)) {
    fail("CONFIG_MISMATCH", "configuration roots must be objects");
  }
  const participants = [context.local_group_id, context.remote_group_id].sort();
  exactArray(game.value.agreed_between, participants, "IDENTITY_MISMATCH", "agreed_between");
  const hashes = [
    sourceHash("game.json", game.bytes),
    sourceHash("rate_limits.json", rate.bytes),
    configHash(game.value, rate.value),
  ];
  const fields = ["game_source_sha256", "rate_limits_source_sha256",
    "agreed_configuration_sha256"];
  fields.forEach((field, index) => {
    lowerHex(config[field], 64, field);
    if (config[field] !== hashes[index]) fail("HASH_MISMATCH", `${field} mismatch`);
  });
  if (hashes[2] !== context.agreed_configuration_sha256) {
    fail("CONFIG_MISMATCH", "offered configuration differs from active agreement");
  }
  if (context.now_ms > offer.expires_at_ms) fail("EXPIRED", "offer has expired");
  return { offer, context, hashes };
}

function acceptance(validated) {
  const { offer, hashes } = validated;
  return {
    profile: PROFILE, version: VERSION, status: "accepted",
    acknowledges: offer.message_id, negotiation_id: offer.negotiation_id,
    game_id: offer.game_id, game_uid: offer.game_uid,
    sub_game_number: offer.sub_game_number,
    participants: [
      { group_id: offer.proposer_group_id, role: offer.proposer_role },
      { group_id: offer.responder_group_id, role: offer.responder_role },
    ],
    accepted_capabilities: [...REQUIRED_CAPABILITIES, ...offer.optional_capabilities],
    game_source_sha256: hashes[0], rate_limits_source_sha256: hashes[1],
    agreed_configuration_sha256: hashes[2],
  };
}

module.exports = { CONFIG_KEYS, OFFER_KEYS, acceptance, offerContext, validateOffer };
