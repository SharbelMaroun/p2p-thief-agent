"use strict";

const { verifyRecords } = require("./audit");
const { controlBody } = require("./control");
const { fail, rejection } = require("./errors");
const { idempotencyHash } = require("./hashes");
const { envelope, closed, safeInt, PROFILE, VERSION } = require("./schema");
const { sessionContext } = require("./session_context");
const { revealBody, turnBody } = require("./turn");

const ACTION_KEYS = ["tool", "message", "now_ms"];

class Session {
  constructor(value) {
    this.context = sessionContext(value);
    this.nextStep = 1;
    this.nextReveal = 1;
    this.cache = new Map();
    this.turns = new Map();
    this.reveals = new Map();
    this.closed = null;
  }

  cached(message) {
    const key = `${message.sender_group_id}|${message.message_id}`;
    const digest = idempotencyHash(message);
    if (!this.cache.has(key)) return { key, digest, result: null };
    const found = this.cache.get(key);
    if (found.digest !== digest) {
      fail("IDEMPOTENCY_CONFLICT", "message_id was reused with different content");
    }
    return { key, digest, result: found.result };
  }

  remember(cached, result) {
    this.cache.set(cached.key, { digest: cached.digest, result });
    return result;
  }

  ack(message, status, extra) {
    return {
      profile: PROFILE, version: VERSION, status,
      acknowledges: message.message_id, game_uid: this.context.game_uid,
      sub_game_number: this.context.sub_game_number, ...extra,
    };
  }

  turn(value, nowMs) {
    const message = envelope(value, "turn_commit", nowMs, this.context, 16_384);
    const body = turnBody(message.body, this.context);
    const cached = this.cached(message);
    if (cached.result !== null) return cached.result;
    if (this.closed !== null) fail("OUT_OF_ORDER", "turn stream is closed");
    if (body.step < this.nextStep) fail("REPLAYED_MESSAGE", "turn step was consumed");
    if (body.step > this.nextStep || body.step > this.context.turn_cap) {
      fail("OUT_OF_ORDER", "turn is not the next expected step");
    }
    const result = this.ack(message, "locked", {
      step: body.step, commitment_sha256: body.commitment_sha256,
    });
    this.turns.set(body.step, { message_id: message.message_id, ...body });
    this.nextStep += 1;
    return this.remember(cached, result);
  }

  reveal(value, nowMs) {
    const message = envelope(
      value, "move_reveal", nowMs, this.context, 16_384, true, ["body.move"],
    );
    const body = revealBody(message.body);
    const cached = this.cached(message);
    if (cached.result !== null) return cached.result;
    if (this.closed !== null) fail("OUT_OF_ORDER", "reveal stream is closed");
    if (body.step < this.nextReveal) fail("REPLAYED_MESSAGE", "move step was revealed");
    if (body.step !== this.nextReveal || body.step >= this.nextStep) {
      fail("OUT_OF_ORDER", "reveal must follow the next locked commitment");
    }
    const turn = this.turns.get(body.step);
    if (body.hint !== turn.hint) {
      fail("COMMITMENT_MISMATCH", "revealed hint does not match the locked turn");
    }
    const result = this.ack(message, "revealed", { step: body.step, move: body.move });
    this.reveals.set(body.step, body.move);
    this.nextReveal += 1;
    return this.remember(cached, result);
  }

  audit(value, nowMs) {
    const message = envelope(value, "final_audit", nowMs, this.context, 8_388_608, false);
    const body = closed(message.body, ["records"], "body");
    const cached = this.cached(message);
    if (cached.result !== null) return cached.result;
    if (this.closed === "audited") fail("REPLAYED_MESSAGE", "audit was already accepted");
    if (this.closed !== null) fail("OUT_OF_ORDER", "audit stream is closed");
    const digest = verifyRecords(
      body.records, this.turns, this.nextStep, this.context, this.reveals,
    );
    const result = this.ack(message, "verified", {
      record_count: body.records.length, audit_sha256: digest,
    });
    this.closed = "audited";
    return this.remember(cached, result);
  }

  control(value, nowMs) {
    const message = envelope(value, "control", nowMs, this.context, 16_384);
    const body = controlBody(message.body);
    const cached = this.cached(message);
    if (cached.result !== null) return cached.result;
    if (!this.context.optional_control) {
      fail("OPTIONAL_TOOL_UNAVAILABLE", "control capability was not negotiated");
    }
    if (this.closed !== null) {
      const code = this.closed === "abort" && body.control === "abort"
        ? "REPLAYED_MESSAGE" : "OUT_OF_ORDER";
      fail(code, "control stream is closed");
    }
    const result = this.ack(message, "accepted", { control: body.control });
    if (body.control === "abort") this.closed = "abort";
    return this.remember(cached, result);
  }

  action(value) {
    let action;
    try {
      action = closed(value, ACTION_KEYS, "action");
      safeInt(action.now_ms, "action.now_ms");
      if (action.tool === "receive_move") return this.turn(action.message, action.now_ms);
      if (action.tool === "receive_reveal") return this.reveal(action.message, action.now_ms);
      if (action.tool === "submit_audit") return this.audit(action.message, action.now_ms);
      if (action.tool === "receive_control") return this.control(action.message, action.now_ms);
      fail("MALFORMED", "unknown session tool");
    } catch (error) {
      return rejection(action && action.message, error);
    }
  }
}

function runSession(context, actions) {
  if (!Array.isArray(actions)) fail("MALFORMED", "actions must be an array");
  const session = new Session(context);
  const results = actions.map((action) => session.action(action));
  return {
    results,
    state: { next_step: session.nextStep, closed: session.closed },
  };
}

module.exports = { runSession };
