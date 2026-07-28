"use strict";

const { fail } = require("./errors");
const { closed, identifier, lowerHex, safeInt } = require("./schema");

const CONTEXT_KEYS = [
  "game_id", "game_uid", "sub_game_number", "local_group_id", "local_role",
  "remote_group_id", "remote_role", "agreed_configuration_sha256", "turn_cap",
  "optional_control", "axis_start_index", "grid_size",
];

function sessionContext(value) {
  const context = closed(value, CONTEXT_KEYS, "session context");
  identifier(context.game_id, "game_id");
  identifier(context.game_uid, "game_uid");
  safeInt(context.sub_game_number, "sub_game_number", 1, 6);
  identifier(context.local_group_id, "local_group_id", 64);
  identifier(context.remote_group_id, "remote_group_id", 64);
  lowerHex(context.agreed_configuration_sha256, 64, "agreed_configuration_sha256");
  safeInt(context.turn_cap, "turn_cap", 1);
  safeInt(context.axis_start_index, "axis_start_index");
  safeInt(context.grid_size, "grid_size", 1);
  if (!Number.isSafeInteger(context.axis_start_index + context.grid_size - 1)) {
    fail("MALFORMED", "board bounds exceed safe integer range");
  }
  if (typeof context.optional_control !== "boolean") {
    fail("MALFORMED", "optional_control must be a boolean");
  }
  if (context.local_group_id === context.remote_group_id ||
      new Set([context.local_role, context.remote_role]).size !== 2 ||
      !["police", "thief"].includes(context.local_role) ||
      !["police", "thief"].includes(context.remote_role)) {
    fail("IDENTITY_MISMATCH", "session participants are invalid");
  }
  return context;
}

module.exports = { CONTEXT_KEYS, sessionContext };
