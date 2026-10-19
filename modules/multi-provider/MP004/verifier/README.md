# Independent verifier and supplementary tests

verify_mp004.py is byte-identical to the implementation used in the original preflight and scored run. It uses Python JSON/hash/base64 support and cryptography's Ed25519 implementation. It does not import, invoke or reuse association-recorder helpers. The library dependency is fixed in ../requirements.txt; exact runtime and implementation hashes are in the run metadata.

From the MP004 root:

    python -m pip install -r requirements.txt
    python verifier/test_verify_mp004_portable.py
    python verifier/verify_mp004.py --manifest configs/MP004_RUN_MANIFEST.json --output evidence/preflight/MY_FRESH_REPRODUCTION

The output directory must not exist. Existing fixtures must equal the frozen recipes. The last command reproduces the complete case matrix in a new preflight location; it does not replace the historical scored run.

test_verify_mp004.py is the unchanged historical nine-test suite pinned by the implementation manifest. It contains the original absolute Windows root. test_verify_mp004_portable.py changes only that root assignment to derive the directory from its own file location; the test bodies are unchanged. The portable file is a publication adaptation, not the suite hash recorded before scoring.

Exit codes are 0 PASS, 1 FAIL and 2 INCOMPLETE for runs that enter the report-producing portion of main. CLI errors, an existing output directory, or filesystem failures can terminate before reports are written. Source/lock mismatches normally produce INCOMPLETE reports. The code targets this frozen MP004 campaign and fixture set, not arbitrary future evidence schemas.
