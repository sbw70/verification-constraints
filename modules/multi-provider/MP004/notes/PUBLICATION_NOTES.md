# Publication preparation record

The user requested a flat local staging root, MULTI_PROVIDER_004/github/, with repository nesting deferred until push. No push, PR, remote branch or repository mutation is part of this preparation.

The assistant proceeded from the locked contract into offline scoring after the user's instruction to proceed. The user later clarified they had not necessarily intended that transition, while accepting the already-completed offline run. This process clarification is retained; no additional user approval milestone is asserted in the publication history.

Operational corrections: the initial web fetch failed; the GitHub connection subsequently succeeded and all 111 copied files matched the pinned published commit. A read-only Git command against the earlier repo_push checkout was blocked by Git's ownership check; no global safe.directory exception was added, and publication comparison used the GitHub connection instead. The initial verifier installation command had an incorrect relative source path and failed before a run existed; the corrected absolute-path installation succeeded. There were no scored property failures.

Staging copies configs, source references, fixture bytes, original verifier/test suite, all MP004 evidence and the correction note. Python bytecode/cache directories are excluded. Requirements and .gitattributes are added for reproduction and byte preservation. The portable supplementary test file changes only the original test's absolute-root assignment. The scored verifier is unchanged. Historical manifests, transcripts and paths remain intact.

Limitations of implementation/reporting identified during inspection: N03 and N04 descriptor files are preserved fixture descriptions, while their fixed semantics are evaluated directly by the harness. Some per-record interpretation_status fields remain not_requested; N04's interpretation is in case_results.json. The verifier checks raw package hashes and source context but does not authenticate historical request transmission, independently verify issuance authorization signatures, prove physical execution, check an association hash chain, or establish completeness. Claims and results must remain limited accordingly.

Local paths and lab host information are retained as provenance. The copied source contains contextual documentation that refers to the larger MP003 module; it is not a complete implementation checkout. The scored source manifest fixes the selected subset.

The publication root SHA256SUMS.txt covers all staged files except itself. It is an integrity inventory, not an external signature or immutable trust anchor. PUBLICATION_MANIFEST.json explains byte-identical copies and added publication files.

During publication auditing, the first comparison of the portable test copy failed because the audit reader used the Windows default text encoding on a file containing a Greek character. Reading both files explicitly as UTF-8 resolved the audit comparison. Neither the test code nor the scored verifier changed; the portable tests and staging replay had already passed. The final audit passed.
