# Shared Contract Policy

This repository must represent only the Thief peer at runtime.

- It must not import from, mount, execute, or depend on the Cop repository.
- It must not share live mutable state with a Cop process.
- Thief-local state, beliefs, observations, settings, and strategy remain local.
- Cop-only strategy behavior must not be implemented as Thief responsibility.
- Shared game rules may be described only with recorded official evidence.

Whether generic stateless protocol/domain code may be independently duplicated in both
repositories is `UNKNOWN`. Until clarified, create no cross-repository package/link,
claim no byte-identical config/code, and invent no schema, message, or crypto payload.

Companion: <https://github.com/SharbelMaroun/p2p-cop-agent>.
