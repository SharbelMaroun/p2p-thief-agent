# Shared Contract Policy

This repository must represent only the Thief peer at runtime.

- It must not import from, mount, execute, or depend on the Cop repository.
- It must not share live mutable state with a Cop process.
- Thief-local state, beliefs, observations, settings, and strategy remain local.
- Cop-only strategy behavior must not be implemented as Thief responsibility.
- Shared game rules may be described only with recorded official evidence.

For the M1 contract gate, the Cop agent is process owner for the proposal only. The
Thief agent must:

1. inspect the proposal commit and its cited sources;
2. reject or question unsupported fields;
3. copy provisionally authorized parity-controlled files byte-for-byte;
4. verify every copied file against the provisional SHA-256 manifest;
5. prove parity/conformance before requesting final coordinator freeze.

This produces independent file copies, not a cross-repository package, mount, import, or
shared runtime filesystem. It does not make Cop authoritative during play.

Original candidate `84339c2` and revised candidate `b586af9` were not authorized for
Thief copying. Later observed local Cop head `665bd30` is proposed, unfrozen, and has
no coordinator verdict. Until an immutable candidate receives explicit provisional
parity authorization and a complete handoff, the contract status is `PENDING`. No
Thief MCP tools, message envelope, schema, crypto payload, fixture, active shared
configuration, or manifest format may be invented. Byte identity may be claimed only
for files whose hashes were actually compared. Provisional parity is not final freeze
or gameplay permission.

Companion: <https://github.com/SharbelMaroun/p2p-cop-agent>.
