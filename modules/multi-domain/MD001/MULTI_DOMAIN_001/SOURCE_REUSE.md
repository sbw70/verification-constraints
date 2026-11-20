# Source inventory and compatibility review

Exact absolute paths, retained paths, sizes, actual SHA-256 values, and available
baseline hash comparisons for 34 files are in `reference/SOURCE_INVENTORY.json`.
The MP005-reference checkout is commit `73713f6e9ed9c95251cc69ec88ef816cab771ac0`.
The outer workspace has an unborn Git HEAD; local MD-001 and MP006 revisions are
identified by content manifests rather than an invented commit.

| Component | Inspected role | Reuse / adapter / limitation |
|---|---|---|
| MH001 frozen R4.3 | hub.py, wire.py, routes.py, freeze, baseline, source review | These three Python files execute unchanged. New launcher creates HUB_B with static numeric routes. The standard CLI requires a two-hub pair and is not reused. Unused PROVIDER_A route points to loopback port 1 in simulation and is never selected. Physical disposition requires review. |
| MP005 R3 reference | provider_a.py, mint_authorization_a.py, requirements, locks and harness conventions | `canonical_bytes` function is copied verbatim from provider_a.py, asserted by AST source comparison. Ed25519 `sign(tag + canonical)` and `verify(signature, tag + canonical)` patterns are adapted to a new MD001 domain-separation tag and schema. No whole provider import. |
| MP004 | verifier/verify_mp004.py, provenance and checksums | Inspected only. Record verification is separable from contextual analysis, but schema, anchors, lifecycle correlation and `auth_spent` reason vocabulary are MP-specific. No MP004 runtime import or function reuse. |
| MP006 | mp006.py, README, SOURCE_REVIEW, SHA256SUMS | Evidence conventions only: exclusive run directories, preserved bytes, source/config hashes, process identity and observed decisions. Its consumption/replay scorers and state-recovery logic are incompatible and not reused. |
| ESP-LOCAL-008 | provider, presenter, endpoint C source, witness C source and documentation | Design-only source inspection. No runtime import, firmware edits, key substitution, flashing, or actuation. Historical evidence remains in place. |

MP005/MP004 restrictions were reviewed before new implementation: no consumption,
SPENT state, replay denial, seen-ID history, lifecycle state correlation, issuance,
or authorization enforcement is included in the MD-001 verifier. Full reference
files retain original bytes for provenance, not as dependencies of the verifier.

The MH001 mechanical relay accepts bounded HTTP/1 requests with Content-Length,
requires exactly one `X-MH-Destination: PROVIDER_B`, and selects a configured numeric
endpoint. It preserves body bytes; Host and hop-by-hop HTTP framing can change.
It forwards the verifier response without interpreting the verdict. Unsupported
transfer encoding, upgrades, Expect, malformed framing, and oversized request bodies
fail at transport. It sends once, without retry. Existing relay body hashes are
diagnostics; its egress hash records a send attempt, not proof of wire delivery.
Our independent downstream application observation establishes received bytes in
simulation. No hashing was added to the frozen relay.

Dependencies: Python standard library and `cryptography` (validated 49.0.0).
MP005 allows >=41,<51; the desktop pin is within that range. The relay itself is
standard-library-only. Physical ESP tooling, ESP-IDF, existing keys and network
configuration are separate future prerequisites. No new cryptographic algorithm
was implemented. All incompatibilities above were reported before adaptation.
