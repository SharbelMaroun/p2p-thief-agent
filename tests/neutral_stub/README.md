# Independent Node conformance stub

`stub.js` is a black-box, neutral implementation of the Option-B wire profile. It uses
Node's standard library only, imports no Thief package module, opens no socket, and
shares no serializer or validation code with the Python implementation.

Send exactly one JSON command on standard input; one JSON result is written to standard
output. Hash operations are `canonicalize`, `sha256`, `config_hash`, `source_hash`,
`commitment_hash`, `audit_hash`, and `idempotency_hash`. Negotiation operations are
`make_offer`, `validate_offer`, `accept_offer`, and stateful `negotiate_sequence`.
Stateful `session` executes ordered `receive_move`, `submit_audit`, and
`receive_control` actions in one isolated process.

Failed top-level commands return `{"ok":false,"rejection":{...}}`; the nested rejection
is the profile's exact `status`/`acknowledges`/`error` object. Stateful scenario results
contain exact acknowledgements or rejections directly.

Example:

```powershell
'{"op":"canonicalize","value":{"b":2,"a":"שלום"}}' |
  node tests/neutral_stub/stub.js
```

The stub deliberately validates closed offer and configuration wrappers. The embedded
`game` and `rate_limits` documents remain data governed by their own semantic profile;
the neutral boundary requires their decoded bytes to be exact RFC 8785 JCS, then checks
their source-byte hashes, canonical semantic hash, and sorted `game.agreed_between`
participant binding.

Standard input is decoded as fatal UTF-8 and parsed by a duplicate-aware I-JSON parser.
The session enforces profile byte/depth limits, active identity and configuration
binding, deadlines, privacy, ordering, replay, idempotency, commitment reveal, audit,
and optional-control semantics entirely in Node.
