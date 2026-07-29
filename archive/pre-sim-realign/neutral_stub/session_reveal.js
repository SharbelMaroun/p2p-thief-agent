"use strict";

const { fail } = require("./errors");
const { envelope } = require("./schema");
const { revealBody } = require("./turn");

function receiveReveal(session, value, nowMs) {
  const message = envelope(
    value, "move_reveal", nowMs, session.context, 16_384, true, ["body.move"],
  );
  const body = revealBody(message.body);
  const cached = session.cached(message);
  if (cached.result !== null) return cached.result;
  if (session.closed !== null) fail("OUT_OF_ORDER", "reveal stream is closed");
  let repeated = false;
  if (body.step < session.nextReveal) {
    const accepted = session.reveals.get(body.step);
    if (body.move !== accepted.move || body.hint !== accepted.hint) {
      fail("COMMITMENT_MISMATCH", "move reveal conflicts with the accepted live reveal");
    }
    repeated = true;
  } else if (body.step !== session.nextReveal || body.step >= session.nextStep) {
    fail("OUT_OF_ORDER", "reveal must follow the next locked commitment");
  }
  if (!repeated) {
    const turn = session.turns.get(body.step);
    if (body.hint !== turn.hint) {
      fail("COMMITMENT_MISMATCH", "revealed hint does not match the locked turn");
    }
  }
  const result = session.ack(
    message, "revealed", { step: body.step, move: body.move },
  );
  if (!repeated) {
    session.reveals.set(body.step, { move: body.move, hint: body.hint });
    session.nextReveal += 1;
  }
  return session.remember(cached, result);
}

module.exports = { receiveReveal };
