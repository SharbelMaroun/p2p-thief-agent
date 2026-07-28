"use strict";

class ConformanceError extends Error {
  constructor(code, detail) {
    super(detail);
    this.code = code;
  }
}

function fail(code, detail) {
  throw new ConformanceError(code, detail);
}

function messageId(value) {
  const candidate = value && typeof value === "object" ? value.message_id : null;
  return typeof candidate === "string" && /^[0-9a-f]{32}$/.test(candidate)
    ? candidate
    : null;
}

function rejection(value, error) {
  return {
    status: "rejected",
    acknowledges: messageId(value),
    error: {
      code: error instanceof ConformanceError ? error.code : "INTERNAL_ERROR",
      detail: String(error.message || "internal failure").slice(0, 512),
      retryable: false,
    },
  };
}

module.exports = { ConformanceError, fail, rejection };
