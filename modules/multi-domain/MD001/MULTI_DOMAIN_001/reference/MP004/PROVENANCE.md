# MP004 provenance

## Source and claim

MP004 reuses preserved MP003 session MP003_SCORED_20261015_R2 as offline input. The selected source files match published commit fa541618b1a3bc58700a81b29129b17b35b1e0fc in sbw70/verification-constraints. The comparison used GitHub's complete commit tree and locally recomputed Git blob identities. All 111 selected files matched; their SHA-256 inventory is locked separately.

The property tested is authentication and specified interpretation of preserved provider evidence independently of recorder classifications. NUVL remains transport. Providers retain execution authority. Neither the association nor this verifier creates authority.

## Preparation and scoring

Draft 0.1 was preserved before revision 1.0 was locked. The contract, input manifest, source inventory and publication comparison were frozen before verifier implementation. The run manifest pins 17 raw packages, 15 campaign expectations and mutation recipes. Boundary keys were independently checked against pinned raw-key fingerprints. No provider issuance or boundary private key is needed for this offline test.

Implementation used Python 3.12.14 and cryptography 50.0.2 on the operator Windows machine. The verifier was written separately and did not import or run the association recorder. It used the published wire specification for canonicalization/domain separation and a standard Ed25519 library. Independence is from recorder verification code/classification, not from the shared protocol specification, operating system, CPU or operator.

The original preflight passed. Nine supplementary robustness tests passed. An implementation manifest fixed verifier/test/fixture identities before the scored run. MP004_SCORED_20261018_R1 then passed all seven expected outcomes. Original run files and manifests are preserved unchanged. The frozen manifest's earlier NOT_IMPLEMENTED/NOT_RUN fields remain as historical lock-state fields.

## Corrections and publication

Operational misfires and the user's clarification about the scoring transition are recorded in notes/PUBLICATION_NOTES.md. Staging uses copies and includes all original MP004 preflight, scored and retained material. The portable test adaptation is a later publication change with no scored-verifier change. Subsequent staging checks are separately retained under evidence/publication_check/. No remote publication was performed.

## Limits

A verified signature authenticates a statement under a pinned key; it does not prove the provider's policy correct or establish a physical outcome. N04 establishes contradiction with an authenticated denial, not universal non-execution. MP004 does not test compromised boundary keys or hosts, missing/undelivered evidence, immutable storage, association hash-chain validity, global chronology, restart durability, crash behavior, concurrency or cross-provider atomicity. MP003 laboratory private keys were published intentionally; this is not an adversarial post-publication historical authenticity proof.
