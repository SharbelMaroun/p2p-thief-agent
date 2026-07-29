"use strict";

const { ConformanceError, fail, rejection } = require("./errors");
const { negotiateSequence } = require("./negotiation");
const { runSession } = require("./session");
const { sessionContext } = require("./session_context");

function linked(active, sessionValue) {
  const context = sessionContext(sessionValue);
  const participants = new Set([active.group_a_id, active.group_b_id]);
  const roles = new Map([
    [active.group_a_id, active.group_a_role],
    [active.group_b_id, active.group_b_role],
  ]);
  if (active.game_id !== context.game_id ||
      active.game_uid !== context.game_uid ||
      active.sub_game_number !== context.sub_game_number ||
      active.agreed_configuration_sha256 !== context.agreed_configuration_sha256 ||
      !participants.has(context.local_group_id) ||
      !participants.has(context.remote_group_id) ||
      roles.get(context.local_group_id) !== context.local_role ||
      roles.get(context.remote_group_id) !== context.remote_role) {
    fail("IDENTITY_MISMATCH", "session context does not match negotiation");
  }
  return context;
}

function wireSequence(active, offers, sessionValue, actions) {
  const negotiation = negotiateSequence(active, offers);
  linked(active, sessionValue);
  if (negotiation.ready) {
    return { negotiation, session: runSession(sessionValue, actions) };
  }
  if (!Array.isArray(actions)) fail("MALFORMED", "actions must be an array");
  const error = new ConformanceError("OUT_OF_ORDER", "traffic precedes mirrored negotiation");
  return {
    negotiation,
    session: {
      results: actions.map((action) => rejection(action && action.message, error)),
      state: { next_step: 1, closed: null },
    },
  };
}

module.exports = { wireSequence };
