# Locked definitions and implementation identity

MP004_CONTRACT.md is revision 1.0. MP004_RUN_MANIFEST.json pins 17 raw package hashes, 15 campaign expectations and six negative-fixture recipes; N05 has two subcases. MP004_SOURCE_MANIFEST.json inventories 111 copied MP003 reference files. MP004_PUBLICATION_COMPARISON.json records their exact Git blob matches to commit fa541618b1a3bc58700a81b29129b17b35b1e0fc. MP004_LOCK_SHA256SUMS.txt authenticates these four locked files relative to this directory.

MP004_IMPLEMENTATION_MANIFEST.json was created after implementation/preflight and before scoring. It pins the scored verifier, original nine-test suite and fixture manifest. All six original config files are copied unchanged. NOT_IMPLEMENTED and NOT_RUN in the frozen input manifest describe the earlier lock moment; scored run metadata records the later outcome. Absolute Windows paths are retained historical provenance, not required paths for reproduction.
