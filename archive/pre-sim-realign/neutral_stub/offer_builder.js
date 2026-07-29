"use strict";

const { configHash, decodeSource, sourceHash } = require("./hashes");
const { PROFILE, REQUIRED_CAPABILITIES, VERSION, closed } = require("./schema");
const { validateOffer } = require("./offer");

const MAKE_KEYS = [
  "op", "proposer_group_id", "proposer_role", "responder_group_id", "responder_role",
  "game_id", "game_uid", "sub_game_number", "message_id", "negotiation_id",
  "sent_at_ms", "expires_at_ms", "step_zero", "game_source_b64",
  "rate_limits_source_b64", "optional_capabilities",
];

function makeOffer(command) {
  closed(command, MAKE_KEYS, "command");
  const game = decodeSource(command.game_source_b64, "game source");
  const rate = decodeSource(command.rate_limits_source_b64, "rate-limits source");
  const hashes = [
    sourceHash("game.json", game.bytes),
    sourceHash("rate_limits.json", rate.bytes),
    configHash(game.value, rate.value),
  ];
  const offer = {
    profile: PROFILE,
    supported_versions: [VERSION],
    negotiation_id: command.negotiation_id,
    message_id: command.message_id,
    sent_at_ms: command.sent_at_ms,
    expires_at_ms: command.expires_at_ms,
    proposer_group_id: command.proposer_group_id,
    proposer_role: command.proposer_role,
    responder_group_id: command.responder_group_id,
    responder_role: command.responder_role,
    game_id: command.game_id,
    game_uid: command.game_uid,
    sub_game_number: command.sub_game_number,
    required_capabilities: [...REQUIRED_CAPABILITIES],
    optional_capabilities: command.optional_capabilities,
    step_zero: command.step_zero,
    configuration: {
      game_source_b64: command.game_source_b64,
      game_source_sha256: hashes[0],
      rate_limits_source_b64: command.rate_limits_source_b64,
      rate_limits_source_sha256: hashes[1],
      agreed_configuration_sha256: hashes[2],
    },
  };
  validateOffer(offer, {
    now_ms: command.sent_at_ms,
    game_id: command.game_id,
    game_uid: command.game_uid,
    sub_game_number: command.sub_game_number,
    local_group_id: command.responder_group_id,
    local_role: command.responder_role,
    remote_group_id: command.proposer_group_id,
    remote_role: command.proposer_role,
    agreed_configuration_sha256: hashes[2],
    remote_git_commit: command.step_zero.git_commit,
  });
  return offer;
}

module.exports = { MAKE_KEYS, makeOffer };
