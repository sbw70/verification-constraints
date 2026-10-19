# MP004 results

PASS — MP004_SCORED_20261018_R1, 2026-10-18.

- B01: 17 of 17 provider signatures valid; 15 of 15 campaign assertions valid.
- N01: modified boundary value rejected by signature verification.
- N02: modified signature rejected.
- N03: original A package fails under B key; production trust-anchor validator refuses the swapped key.
- N04: false unsigned C02 execution summary contradicted by authenticated Provider B DENY auth_provider_mismatch.
- N05a: original valid package remains valid when recorder metadata falsely labels it invalid.
- N05b: modified package remains invalid when recorder metadata falsely labels it valid.

All 111 reference-source hashes, 67 original scored checksums, both trust anchors, frozen lock hashes and six fixture hashes were checked. All original recorder comparisons agree after independent verification. Nine supplementary robustness tests passed. Scored output checksums were checked after the run. The scored verifier is byte-identical to the preflight verifier.

The evidence supports authentication of the preserved provider statements and the specified contextual classifications independently of recorder classifications. It does not establish physical execution, evidence completeness, universal non-execution, global chronology, immutable storage or resistance to boundary-key compromise. N04 reports a contradiction with the provider's signed denial, not physical proof. The offline verifier creates no execution authority. No live topology changes or publication actions were performed.
