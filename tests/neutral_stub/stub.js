#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const { fail, rejection } = require("./errors");
const {
  auditHash, configHash, decodeSource, idempotencyHash, sha256, sourceHash,
} = require("./hashes");
const { canonicalize } = require("./jcs");
const { negotiateSequence } = require("./negotiation");
const { acceptance, validateOffer } = require("./offer");
const { makeOffer } = require("./offer_builder");
const { closed, text } = require("./schema");
const { runSession } = require("./session");
const { sessionContext } = require("./session_context");
const { strictParseBytes } = require("./strict_json");
const { revealHash } = require("./turn");

function hashCommands(command) {
  if (command.op === "canonicalize") {
    closed(command, ["op", "value"], "command");
    return { ok: true, canonical: canonicalize(command.value) };
  }
  if (command.op === "sha256") {
    closed(command, ["op", "data_utf8"], "command");
    const data = Buffer.from(text(command.data_utf8, "data_utf8"), "utf8");
    return { ok: true, sha256: sha256(data) };
  }
  if (command.op === "config_hash") {
    closed(command, ["op", "game", "rate_limits"], "command");
    return { ok: true, sha256: configHash(command.game, command.rate_limits) };
  }
  if (command.op === "source_hash") {
    closed(command, ["op", "logical_name", "source_base64"], "command");
    if (!["game.json", "rate_limits.json"].includes(command.logical_name)) {
      fail("MALFORMED", "invalid logical source name");
    }
    const source = decodeSource(command.source_base64, "configuration source");
    return { ok: true, sha256: sourceHash(command.logical_name, source.bytes) };
  }
  return null;
}

function protocolHashCommands(command) {
  if (command.op === "commitment_hash") {
    closed(command, ["op", "payload", "nonce", "context"], "command");
    const context = sessionContext(command.context);
    return { ok: true, sha256: revealHash(command.payload, command.nonce, context) };
  }
  if (command.op === "audit_hash") {
    closed(command, ["op", "records", "context"], "command");
    const context = sessionContext(command.context);
    if (!Array.isArray(command.records)) {
      fail("MALFORMED", "records must be an array");
    }
    return { ok: true, sha256: auditHash(context, command.records) };
  }
  if (command.op === "idempotency_hash") {
    closed(command, ["op", "message"], "command");
    return { ok: true, sha256: idempotencyHash(command.message) };
  }
  return null;
}

function dispatch(command) {
  closed(command, Object.keys(command), "command");
  if (typeof command.op !== "string") {
    fail("MALFORMED", "command requires op");
  }
  const hashResult = hashCommands(command) || protocolHashCommands(command);
  if (hashResult !== null) return hashResult;
  if (command.op === "make_offer") return { ok: true, offer: makeOffer(command) };
  if (command.op === "validate_offer" || command.op === "accept_offer") {
    closed(command, ["op", "offer", "context"], "command");
    const validated = validateOffer(command.offer, command.context);
    return command.op === "accept_offer"
      ? { ok: true, ack: acceptance(validated) }
      : { ok: true, validation: {
        participants: [validated.context.local_group_id,
          validated.context.remote_group_id].sort(),
        agreed_configuration_sha256: validated.hashes[2],
      } };
  }
  if (command.op === "negotiate_sequence") {
    closed(command, ["op", "active", "offers"], "command");
    return { ok: true, ...negotiateSequence(command.active, command.offers) };
  }
  if (command.op === "session") {
    closed(command, ["op", "context", "actions"], "command");
    return { ok: true, ...runSession(command.context, command.actions) };
  }
  fail("MALFORMED", `unsupported operation ${command.op}`);
}

function main() {
  let command = null;
  try {
    command = strictParseBytes(fs.readFileSync(0));
    process.stdout.write(`${JSON.stringify(dispatch(command))}\n`);
  } catch (error) {
    const request = command && (command.offer || command.message);
    process.stdout.write(`${JSON.stringify({
      ok: false,
      rejection: rejection(request, error),
    })}\n`);
  }
}

main();
