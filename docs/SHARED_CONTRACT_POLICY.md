# Shared Contract Policy

This repository must represent only the Thief peer at runtime.

- It must not import from, mount, execute, or depend on the Cop repository.
- It must not share live mutable state with a Cop process.
- Thief-local state, beliefs, observations, settings, and strategy remain local.
- Cop-only strategy behavior must not be implemented as Thief responsibility.
- Shared game rules may be described only with recorded official evidence.

For M1 the Thief independently authors a public interoperability profile from
book-confirmed rules and recorded Option-B choices. It must:

1. label every profile item by authority and keep unresolved choices explicit;
2. define exact canonical bytes, hash domains, messages, and acknowledgements;
3. prove both proposal directions against a neutral stub sharing no project source;
4. reject identity, value, version, hash, ordering, replay, and leakage failures;
5. record explicit profile acceptance before declaring M1 complete.

No peer repository, bundle, manifest, schema, or fixture is an input to this workflow.
Historical Cop candidate reviews remain audit evidence only. Runtime peers stay
separate and exchange only the negotiated public messages defined by the accepted
profile.

Companion: <https://github.com/SharbelMaroun/p2p-cop-agent>.
