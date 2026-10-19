Publication preparation record

MP004 publication staging preserves the locked test definition, verifier implementation, fixtures, scored evidence, selected MP003 source evidence, integrity manifests, and supporting documentation used to reproduce and inspect the result.

The selected MP003 source material used by MP004 was checked against the pinned published source. The scored verifier was not modified during publication preparation.

The publication includes the original verifier and test suite together with a supplementary portable test copy. The portable copy changes only the local root-path assignment required to run the same tests from the published directory structure; it does not change verifier logic or scored semantics.

The scored MP004 result contained no property failures. Preflight, scored execution, portable tests, staging replay, and the final publication audit completed successfully.

N03 and N04 descriptor files are preserved fixture descriptions, while their fixed test semantics are evaluated directly by the harness. N04 interpretation is recorded in `case_results.json`. Some per-record `interpretation_status` fields remain `not_requested`; those fields are not the basis of the scored N04 result.

The independent verifier checks preserved provider boundary packages from their raw recorded bytes, derives provider key identifiers from the published boundary public keys, reconstructs canonical signature inputs, verifies Ed25519 provider signatures independently of recorder verdict fields, evaluates the defined tamper and wrong-anchor cases, and compares preserved recorder classifications only after independent verification.

The verifier does not authenticate historical request transmission, independently verify provider authorization-issuance signatures, prove physical execution, establish evidence completeness, or treat recorder metadata as an authority source. MP004 claims are limited accordingly.

The copied `source/MP003/` material is the source subset fixed for MP004 and is not presented as a complete duplicate of the MP003 module.

The publication-root `SHA256SUMS.txt` provides an integrity inventory of the staged publication files except itself. `PUBLICATION_MANIFEST.json` identifies the publication contents and distinguishes preserved test material from publication-specific support files.
