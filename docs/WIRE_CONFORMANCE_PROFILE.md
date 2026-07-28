# Stage A Wire Conformance Profile

Status: **PROPOSED — awaiting explicit acceptance; not accepted**

Profile ID: `p2p-thief-option-b`

Wire version: `1.0`

Canonicalization: `RFC8785-JCS` over the I-JSON domain

This is the Thief-authored Stage A public interoperability proposal. It was produced
without reading, copying, importing, or depending on peer source, schemas, fixtures, or
runtime state. It does not authorize live peer deployment or gameplay. Acceptance
requires `CONFORMANCE_PROFILE: ACCEPTED` naming the exact repository revision.

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` are normative. Every normative group below has
an authority label:

- **BOOK-CONFIRMED** — direct project-book requirement, identified by the local
  requirements-ledger ID.
- **OPTION-B PROJECT CHOICE** — an exact public wire choice where the book leaves the
  detail open.
- **UNKNOWN** — deliberately unresolved and not silently made normative.

## 1. Scope and fixed public surface

**Authority: BOOK-CONFIRMED (`SR-004`, `SR-005`, `AE-017`) plus OPTION-B PROJECT
CHOICE for every literal name and wire shape in this section.**

Each participant is a separate process and is both a FastMCP server and client. The
public tools and their sole arguments are exactly:

| Tool | Sole argument | Required |
|---|---|---|
| `negotiate` | `offer` | yes |
| `receive_turn` | `message` | yes |
| `submit_audit` | `audit` | yes |
| `receive_control` | `message` | no; capability-negotiated |

`submit_audit` is the server tool name. Client-side helper names are not public tools.
No additional public tool, argument, alias, or positional argument conforms to v1.0.

The two actual participants MUST be supplied at runtime. A profile file, fixture, or
source file MUST NOT contain match-specific placeholder identities. Conformance
evidence MUST exercise at least two distinct participant pairs and match identities
without editing this profile or implementation constants.

## 2. JSON, primitives, closure, and limits

**Authority: OPTION-B PROJECT CHOICE, preserving the BOOK-CONFIRMED sorted, compact
UTF-8 SHA-256 primitive in `CR-001`.**

All requests, acknowledgements, errors, configuration sources, committed payloads, and
hash inputs are JSON in the RFC 8785 JSON Canonicalization Scheme (JCS) input domain:

1. Input MUST be valid UTF-8 I-JSON with no BOM.
2. Object member names MUST be unique. Duplicate names are rejected before hashing.
3. Strings MUST contain valid Unicode scalar values; lone surrogates are rejected. JCS
   performs no Unicode normalization, so different code-point sequences remain
   different values.
4. Numbers MUST be finite IEEE-754 binary64 values. Every integer-valued input MUST be
   in `-9007199254740991..9007199254740991`; fields this profile defines further
   restrict integers to `0..9007199254740991` unless a narrower range is stated.
   `NaN`, infinities, negative zero where an integer is required, and integers outside
   the safe range are rejected.
5. JCS output is the exact RFC 8785 UTF-8 byte sequence, including its property sorting,
   string escaping, and ECMAScript number rendering. No trailing newline is added.
6. Every wire object whose members this profile defines is closed. An unlisted member
   in those objects is rejected; extension fields require a new accepted profile or
   version. The embedded `game` and `rate_limits` configuration schemas remain
   externally supplied and UNKNOWN except for constraints stated in section 3.1.

In the keyset illustrations below, an empty `{}` shown for `step_zero`,
`configuration`, `body`, or `payload` is a reference to the exact closed shape defined
immediately afterward; an empty object is not valid there unless a section explicitly
says it is.

Primitive grammars are exact:

| Primitive | Constraint |
|---|---|
| group ID | ASCII `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` |
| `game_id`, `game_uid` | ASCII `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$` |
| `message_id`, `negotiation_id` | `^[0-9a-f]{32}$` |
| SHA-256 text | `^[0-9a-f]{64}$` |
| Git commit | `^[0-9a-f]{40}$` |
| role | exactly `thief` or `police` |
| coordinate | exactly `[row,column]`, two integers valid under the negotiated board |
| Base64 | RFC 4648 standard alphabet, required padding, no whitespace |
| time | integer Unix epoch milliseconds in the safe-integer range |

The two group IDs MUST differ. The two roles MUST differ. `sub_game_number` is an
integer in `1..6`. A message `expires_at_ms` MUST be greater than `sent_at_ms` and is
expired when the receiver's Unix time is greater than `expires_at_ms`.

The limit is measured as `len(JCS(argument))` after strict parsing. The root container
has depth 1; each nested object or array adds 1. Limits are:

| Tool argument | Maximum JCS bytes | Maximum container depth |
|---|---:|---:|
| `negotiate.offer` | 65,536 | 64 |
| `receive_turn.message` | 16,384 | 64 |
| `submit_audit.audit` | 8,388,608 | 64 |
| `receive_control.message` | 16,384 | 64 |

## 3. Bootstrap negotiation

### 3.1 Offer

**Authority: BOOK-CONFIRMED for two actual identities (`AB-002`), Step-0 content
(`CR-002`), and refusal on configuration disagreement (`AE-011`); OPTION-B PROJECT
CHOICE for the exact tool, fields, capabilities, order, and encodings.**

`negotiate(offer)` is the only bootstrap request and is not wrapped in the common
post-negotiation envelope. `offer` has exactly these members:

```json
{
  "profile": "p2p-thief-option-b",
  "supported_versions": ["1.0"],
  "negotiation_id": "32-lowercase-hex",
  "message_id": "32-lowercase-hex",
  "sent_at_ms": 0,
  "expires_at_ms": 1,
  "proposer_group_id": "actual-group-id",
  "proposer_role": "thief",
  "responder_group_id": "other-actual-group-id",
  "responder_role": "police",
  "game_id": "actual-game-id",
  "game_uid": "actual-game-uid",
  "sub_game_number": 1,
  "required_capabilities": ["negotiate", "receive_turn", "submit_audit"],
  "optional_capabilities": ["receive_control"],
  "step_zero": {},
  "configuration": {}
}
```

`supported_versions` MUST equal `["1.0"]`. `required_capabilities` MUST equal the shown
three-element array in that order. `optional_capabilities` MUST be either `[]` or
`["receive_control"]`; duplicates are forbidden.

`step_zero` is closed and has exactly:

```json
{
  "os": "nonempty-string",
  "cpu_cores": 0,
  "cpu_frequency_mhz": 0,
  "ram_mb": 0,
  "gpu": "none",
  "vram_mb": 0,
  "llm_name": "none",
  "code_version": "nonempty-string",
  "git_commit": "40-lowercase-hex",
  "group_id": "actual-group-id",
  "role": "thief",
  "sub_game_number": 1
}
```

All strings are nonempty; `gpu` and `llm_name` use the literal `none` when absent.
Hardware numbers are nonnegative safe integers. `group_id`, `role`, and
`sub_game_number` MUST equal the proposer's outer values. `group_id` is the Step-0 team
identity for this profile. `git_commit` MUST be the exact revision running the
sub-game, not a branch, tag, package version, or dirty-tree placeholder.

`configuration` is closed and has exactly:

```json
{
  "game_source_b64": "base64",
  "game_source_sha256": "64-lowercase-hex",
  "rate_limits_source_b64": "base64",
  "rate_limits_source_sha256": "64-lowercase-hex",
  "agreed_configuration_sha256": "64-lowercase-hex"
}
```

The two source values decode to exact UTF-8 bytes. Each source MUST itself equal
`JCS(strict_parse(source_bytes))` byte-for-byte: no BOM, whitespace variation,
duplicate key, or trailing newline is allowed. Each parsed root MUST be an object.
The parsed `game` object MUST contain `agreed_between` equal to the two actual group
IDs in ascending ASCII order, with no placeholder, omission, duplicate, or third
identity.

The receiver MUST bind the offer to the active `game_id`, `game_uid`, sub-game, two
actual group IDs, opposite roles, capabilities, and proposer's Step-0. It MUST recompute
all three configuration hashes. Two mirrored offers complete negotiation: they use the
same `negotiation_id`, match identity, configuration bytes and hashes, swap proposer
and responder, swap roles, and carry each sender's own Step-0. Gameplay is not ready
until both directions have returned an accepted acknowledgement.

The implementation readiness gate is `NegotiationState.ready`; constructing a live
message session before that state is `OUT_OF_ORDER`. After readiness, the host adapter
MUST derive `board_size` and `turn_cap` from its locally selected, hash-matched game
configuration and call `open_remote_session`. The external location/schema of those
two values remains part of the section 11 artifact-schema UNKNOWN; the adapter MUST
record the derivation in conformance evidence and MUST NOT substitute unagreed values.

### 3.2 Configuration hash domains

**Authority: BOOK-CONFIRMED for exact shared-term agreement and SHA-256 (`AE-011`,
`AE-017`); OPTION-B PROJECT CHOICE for the complete domain separation and byte
construction.**

Let `||` mean byte concatenation and `ASCII(x)` the ASCII bytes of `x`.

```text
game_source_sha256 =
  lowerhex(SHA256(
    ASCII("p2p-thief/config-source/game.json/v1|") ||
    game_source_bytes
  ))

rate_limits_source_sha256 =
  lowerhex(SHA256(
    ASCII("p2p-thief/config-source/rate_limits.json/v1|") ||
    rate_limits_source_bytes
  ))

agreed_configuration_sha256 =
  lowerhex(SHA256(JCS({
    "domain": "p2p-thief/agreed-config/v1",
    "game": strict_parse(game_source_bytes),
    "rate_limits": strict_parse(rate_limits_source_bytes)
  })))
```

The source hashes lock exact canonical source bytes. The agreed-configuration hash
locks the two parsed semantic values under a separate domain. They are not move
commitments and MUST NOT be substituted for each other.

A syntactically valid but incorrectly declared hash is `HASH_MISMATCH`. A second
direction that supplies different valid configuration bytes or values is
`CONFIG_MISMATCH`.

### 3.3 Accepted negotiation acknowledgement

**Authority: OPTION-B PROJECT CHOICE.**

Success returns this closed direct object:

```json
{
  "profile": "p2p-thief-option-b",
  "version": "1.0",
  "status": "accepted",
  "acknowledges": "offer-message-id",
  "negotiation_id": "offer-negotiation-id",
  "game_id": "offer-game-id",
  "game_uid": "offer-game-uid",
  "sub_game_number": 1,
  "participants": [
    {"group_id": "proposer-group-id", "role": "thief"},
    {"group_id": "responder-group-id", "role": "police"}
  ],
  "accepted_capabilities": ["negotiate", "receive_turn", "submit_audit", "receive_control"],
  "game_source_sha256": "64-lowercase-hex",
  "rate_limits_source_sha256": "64-lowercase-hex",
  "agreed_configuration_sha256": "64-lowercase-hex"
}
```

`participants` is in proposer-then-responder order and each item has exactly
`group_id` and `role`. `accepted_capabilities` is the required three-element sequence
followed by the sorted optional intersection; omit `receive_control` when it was not
offered or is not supported. Every identity and hash MUST echo a verified offer.

## 4. Post-negotiation envelope

**Authority: OPTION-B PROJECT CHOICE.**

Every request except `negotiate` is the following closed envelope, passed directly as
the tool's sole argument:

```json
{
  "profile": "p2p-thief-option-b",
  "version": "1.0",
  "message_id": "32-lowercase-hex",
  "sent_at_ms": 0,
  "expires_at_ms": 1,
  "game_uid": "negotiated-game-uid",
  "sub_game_number": 1,
  "sender_group_id": "negotiated-sender",
  "recipient_group_id": "negotiated-recipient",
  "type": "type-defined-below",
  "body": {}
}
```

`profile` and `version` require exact equality; no prefix, semantic-version range, or
implicit default is accepted. Identity fields MUST match the accepted negotiation.
The negotiated `game_id` is recovered from the state keyed by `game_uid`; an unknown or
ambiguous mapping is `IDENTITY_MISMATCH`.

## 5. Turn commitment

### 5.1 Public turn message and lock acknowledgement

**Authority: BOOK-CONFIRMED for commit-before-reveal, nonce secrecy, natural-language
hints, and public barrier disclosure (`AE-017`, `AE-021`, `AE-022`); OPTION-B PROJECT
CHOICE for the exact fields and acknowledgement.**

`receive_turn(message)` requires `type: "turn_commit"` and this exact `body`:

```json
{
  "step": 1,
  "role": "thief",
  "commitment_sha256": "64-lowercase-hex",
  "hint": "public natural-language hint",
  "barrier": null
}
```

`barrier` is either `null` or the closed object
`{"position": [row, column]}`. `step` starts at 1, increases by exactly one for each
sender, and MUST NOT exceed the turn cap in the accepted game configuration. `role`
MUST equal the sender's negotiated role. `hint` is a string of at most 4,096 Unicode
scalar values. A non-null barrier and the hint are public; the true move, pre-move
position, intent, payload, verdict, and nonce are not.

The bound message session rejects a public barrier outside its negotiated
`board_size`. At audit it rejects an off-board pre-move position, barrier, or move
whose destination leaves that board as `COMMITMENT_MISMATCH`, which enters the
technical-loss state described in section 6.

Success atomically locks the request's `(sender_group_id, step, message_id,
commitment_sha256, hint, barrier)` and returns:

```json
{
  "profile": "p2p-thief-option-b",
  "version": "1.0",
  "status": "locked",
  "acknowledges": "turn-message-id",
  "game_uid": "negotiated-game-uid",
  "sub_game_number": 1,
  "step": 1,
  "commitment_sha256": "64-lowercase-hex"
}
```

This acknowledgement has exactly the eight shown members. A later message cannot
replace a locked value.

### 5.2 Committed payload, nonce, and commitment

**Authority: BOOK-CONFIRMED for SHA-256 commit-reveal, delayed nonce reveal, and the
sorted compact UTF-8 core (`AE-017`, `CR-001`); OPTION-B PROJECT CHOICE for the exact
payload, RFC 8785 completion, nonce profile, and construction.**

The private committed payload is closed and has exactly:

```json
{
  "domain": "p2p-thief/move-commitment/v1",
  "game_id": "negotiated-game-id",
  "game_uid": "negotiated-game-uid",
  "sub_game_number": 1,
  "step": 1,
  "sender_group_id": "negotiated-sender",
  "role": "thief",
  "position": [0, 0],
  "move": "STAY",
  "intent": "private intent",
  "hint": "exact public hint",
  "barrier": null
}
```

`move` is exactly one of `N`, `S`, `E`, `W`, or `STAY`; `intent` is exactly `truth` or
`lie`. `position` is the sender's pre-move position. `hint` is at most 4,096 Unicode
scalar values. `hint` and `barrier` MUST equal the public turn fields. All identity,
role, step, coordinate, and movement values MUST be valid under the accepted
negotiation and game configuration.

The nonce MUST be 32 independently generated cryptographically secure random bytes,
encoded as exactly 64 lowercase hexadecimal characters. It MUST be unique per committed
record and remain secret until `final_audit`.

```text
commitment_sha256 =
  lowerhex(SHA256(
    JCS(payload) ||
    ASCII("|") ||
    ASCII(nonce)
  ))
```

The payload's fixed `domain` provides move-commitment domain separation. The nonce is
outside the JSON payload. No newline, NUL, length prefix, hex decoding of the nonce, or
Unicode normalization is performed.

## 6. Final audit

**Authority: BOOK-CONFIRMED for final reveal, recomputation, mismatch technical loss,
and zero score (`AE-017`); OPTION-B PROJECT CHOICE for the exact request, ordering,
digest, and acknowledgement.**

`submit_audit(audit)` requires `type: "final_audit"` and a closed body with only
`records`:

```json
{
  "records": [
    {
      "step": 1,
      "turn_message_id": "32-lowercase-hex",
      "commitment_sha256": "64-lowercase-hex",
      "payload": {},
      "nonce": "64-lowercase-hex"
    }
  ]
}
```

Each record has exactly the five shown members. `payload` is the exact committed
payload from section 5.2. Records MUST be strictly ascending by `step`, contain no
duplicate step or `turn_message_id`, and cover every locked turn for the sender exactly
once. `turn_message_id`, public fields, and commitment MUST match the lock. The
receiver MUST recompute the commitment for every record before accepting any of them.

Any well-formed but changed identity, role, step, position, move, intent, hint, barrier,
nonce, or commitment is `COMMITMENT_MISMATCH`; malformed or unknown fields retain the
earlier validation code from section 10. On `COMMITMENT_MISMATCH`, the receiver's
orchestration layer MUST record the book-required technical loss with score zero and
the audit is not verified. Score is not added to the closed wire rejection object.

After complete verification, compute:

```text
audit_sha256 =
  lowerhex(SHA256(JCS({
    "domain": "p2p-thief/final-audit/v1",
    "game_id": negotiated_game_id,
    "game_uid": envelope.game_uid,
    "sub_game_number": envelope.sub_game_number,
    "sender_group_id": envelope.sender_group_id,
    "records": envelope.body.records
  })))
```

Success returns the closed direct object:

```json
{
  "profile": "p2p-thief-option-b",
  "version": "1.0",
  "status": "verified",
  "acknowledges": "audit-message-id",
  "game_uid": "negotiated-game-uid",
  "sub_game_number": 1,
  "record_count": 1,
  "audit_sha256": "64-lowercase-hex"
}
```

`record_count` equals the records-array length. A verified audit closes that sender's
turn stream; a later turn is `OUT_OF_ORDER`.

## 7. Optional control tool

**Authority: OPTION-B PROJECT CHOICE.**

`receive_control(message)` is conforming only when `receive_control` was negotiated.
It requires `type: "control"` and exactly one of these closed bodies:

```json
{"control": "heartbeat"}
```

```json
{"control": "abort", "code": "ASCII-identifier", "reason": "Unicode text"}
```

Abort `code` matches the group-ID character class with maximum length 64. `reason` is
at most 512 Unicode scalar values. Heartbeat changes no state. Abort permanently closes
the sub-game's wire stream.

Success returns:

```json
{
  "profile": "p2p-thief-option-b",
  "version": "1.0",
  "status": "accepted",
  "acknowledges": "control-message-id",
  "game_uid": "negotiated-game-uid",
  "sub_game_number": 1,
  "control": "heartbeat"
}
```

`control` echoes `heartbeat` or `abort`. If the capability was not negotiated, an
exposed endpoint returns `OPTIONAL_TOOL_UNAVAILABLE`. If the endpoint is omitted, the
caller MUST map the transport's tool-not-found result to the same outcome and continue
without assuming control support.

## 8. Privacy and early-leak rejection

**Authority: BOOK-CONFIRMED for private truth and nonce secrecy (`SR-004`, `AE-017`);
OPTION-B PROJECT CHOICE for deterministic wire enforcement.**

Before `final_audit`, a sender MUST NOT disclose or encode its true runtime position,
move, intent, verdict, committed payload, or nonce in any field, alias, extension, or
free-text value. The only coordinate exception is
`receive_turn.message.body.barrier.position`. Negotiated static starting coordinates
inside the canonical configuration sources are public configuration, not runtime
truth.

The pre-audit structural scanner runs before generic unknown-field rejection. A member
named exactly `payload`, `move`, `position`, `intent`, `verdict`, or `nonce` at any
pre-audit location returns `PRIVATE_FIELD_LEAK`, except for the barrier-position and
static-configuration exceptions above. Closed schemas reject aliases and all other
extensions. A receiver that otherwise detects semantic disclosure in a hint or reason
MUST also return `PRIVATE_FIELD_LEAK`; free text is not permission to bypass secrecy.

`verdict` is not a v1.0 commitment or audit-payload member. Its final reporting
semantics remain UNKNOWN; it is nevertheless explicitly forbidden before audit.

## 9. Idempotency, replay, and ordering

**Authority: BOOK-CONFIRMED for explicit state, illegal-transition rejection,
deadlines, and watchdog behavior (`SR-009`, `AE-006`); OPTION-B PROJECT CHOICE for the
exact keys and outcomes.**

The idempotency key is `(sender identity, message_id)`, where sender identity is
`proposer_group_id` for an offer and `sender_group_id` afterward. Its fingerprint is:

```text
lowerhex(SHA256(JCS({
  "domain": "p2p-thief/idempotency/v1",
  "message": the_entire_sole_argument
})))
```

The idempotency cache becomes addressable after strict parsing and validation of a
syntactically valid message ID and sender identity. On the first addressable receipt,
the receiver atomically caches the fingerprint and exact success or application-level
rejection.
The same key and fingerprint returns that cached result without repeating effects.
The same key with different content returns `IDEMPOTENCY_CONFLICT`. Entries and
semantic-event tombstones MUST be retained through the game and for at least 60,000 ms
after it closes. Inputs rejected before a safe key can be established are not cache
entries and are deterministically revalidated on retry.

A new message ID that repeats an already consumed `negotiation_id`, sender/step lock,
sender final audit, abort, or audited `turn_message_id` is `REPLAYED_MESSAGE`.
Out-of-sequence steps, pre-negotiation traffic, incomplete/mismatched mirrored
negotiation, audit coverage errors, post-audit turns, and post-abort traffic are
`OUT_OF_ORDER`. Exact idempotent retries are the sole exception.

The wire state is:

```text
BOOTSTRAP -> two mirrored accepted offers -> READY
READY -> first locked turn -> ACTIVE
READY|ACTIVE -> verified final audit -> AUDITED
READY|ACTIVE -> commitment-mismatched final audit -> TECHNICAL_LOSS
READY|ACTIVE -> accepted abort -> ABORTED
```

`TECHNICAL_LOSS` is terminal and fixes the sender's score at zero. Heartbeat is
state-preserving. This is transport ordering only; it does not choose the
unresolved gameplay event order listed in section 11.

## 10. Rejections

**Authority: OPTION-B PROJECT CHOICE.**

Every application-level rejection is this closed direct object:

```json
{
  "status": "rejected",
  "acknowledges": "request-message-id-or-null",
  "error": {
    "code": "ERROR_CODE",
    "detail": "nonempty diagnostic",
    "retryable": false
  }
}
```

`acknowledges` is the valid request `message_id`, or `null` when none can be safely
parsed. `detail` is diagnostic only and MUST NOT contain private data. Error codes are
exactly:

| Code | Meaning |
|---|---|
| `MALFORMED` | size, depth, encoding, I-JSON, required member, type, grammar, or range failure |
| `UNKNOWN_FIELD` | unlisted member not classified as a private leak |
| `UNSUPPORTED_PROFILE` | profile ID is not exact |
| `UNSUPPORTED_VERSION` | v1.0 is absent or a post-negotiation version is not exact |
| `CAPABILITY_MISMATCH` | required capability or capability ordering/value mismatch |
| `IDENTITY_MISMATCH` | participant, role, match, sub-game, Step-0, sender, or recipient mismatch |
| `CONFIG_MISMATCH` | valid directional configuration values/bytes disagree |
| `HASH_MISMATCH` | a declared source or agreed-configuration hash is wrong |
| `OUT_OF_ORDER` | legal message in an illegal wire state or sequence |
| `REPLAYED_MESSAGE` | a new ID repeats a consumed semantic event |
| `IDEMPOTENCY_CONFLICT` | one sender reuses a message ID with different content |
| `EXPIRED` | request deadline has passed |
| `PRIVATE_FIELD_LEAK` | runtime private truth or nonce appears before audit |
| `OPTIONAL_TOOL_UNAVAILABLE` | unnegotiated or absent optional control tool |
| `COMMITMENT_MISMATCH` | audit record does not reproduce its locked commitment |
| `INTERNAL_ERROR` | unexpected receiver failure without private diagnostic leakage |

Validation is fail-closed. Limits and strict parsing precede application validation,
and the pre-audit private-field scan precedes ordinary unknown-field rejection.
Within a closed object, primitive/schema faults precede state mutation. Senders MUST
submit single-fault negative vectors: this profile does not promise one universal code
for an input containing unrelated simultaneous faults at different nested layers.
`INTERNAL_ERROR` is never a substitute for a known single-fault code.

## 11. Explicit UNKNOWN items

**Authority: UNKNOWN. These are not v1.0 fields or inferred rules.**

| Unknown | v1.0 treatment |
|---|---|
| Signature algorithm, signed bytes, public-key format, trust root, and key distribution | No signature or key field is allowed by the closed v1.0 shapes. Transport/conformance evidence makes no authenticity claim. Resolution requires an accepted revision or new version. |
| Six-sub-game role scheduling | Negotiation binds the two roles for one sub-game, but does not decide which participant receives which role in any other sub-game. |
| Complete declaration, configuration, log, result, and reporting artifact schemas | The two negotiated canonical configuration values and this final-audit wire shape do not claim to be official artifact schemas. Requiredness, enums, signatures, and compatibility remain unresolved. |
| Nonquantitative gameplay event ordering | The profile does not decide move versus barrier application, capture timing, scent emission/decay/observation, scoring edge cases, or other gameplay ordering. Section 9 defines transport order only. |

These UNKNOWNs MUST remain visible in Stage B and Stage C evidence. They may be resolved
or explicitly accepted as named scoped risks, but this proposal MUST NOT be described
as accepted before that decision is recorded.
