# MP005 Phase 1 build handoff

Root: `C:\Users\holiw\esp32-main\MULTI_PROVIDER_005`.

Phase 1 non-execution preparation is complete. The candidate harness is implemented and syntax/helper checked, but is NOT validated by Linux provider simulation. S00 = NOT_RUN; S01 = NOT_RUN; S02 = NOT_RUN; S03 = NOT_RUN. Linux availability is an environment limitation, not a provider/MP005 failure.

## Proposed claim

"In the tested implementation, when the same durable provider state is preserved across a forced process restart performed while idle, previously consumed provider authorization remains spent: exact replay is denied without another execution, while fresh valid provider authorization remains usable after restart."

## Proposed scored cases

R01_PROVIDER_A_RESTART_DURABILITY: consume fresh A authority through relay; prove consume/COMPLETE and local execution; capture idle A process/state identity; STOP for operator forced termination and manual same-runtime/same-state restart; prove a later new process instance; exact replay must produce signed auth_spent with identical spent/log bytes, lengths and counts; fresh A authority must execute normally.

R02_PROVIDER_B_RESTART_DURABILITY: mirror R01 for B with distinct deterministic request/context and fresh B authorization. Relay, recorder and non-target provider stay running; incidental non-target auth_missing is not failure. No other primary scored cases. Live kill is never automated. Exact operator actions and per-host deployed-source/path/filesystem checks are in operator/LIVE_RUNBOOK.md.

## Static inspection complete

Both providers load spent state before constructing/listening on the server; fail startup on missing/invalid top-level state; persist via temporary write, flush/fsync, atomic replace and directory fsync; update in-memory state only after persistence; emit START after consume; append/fsync execution evidence. No shutdown persistence handler exists. Source-level verification and provider-specific line spans are in notes/MP005_IMPLEMENTATION_FACTS.json.

EXECUTION_SEQ resets to zero and is not reconstructed. Sequence reuse may occur after restart, but has NOT been observed under MP005 because no provider ran. It is not scored. No obvious anti-rollback mechanism was found statically; S03 has no result yet and anti-rollback resistance is NOT ESTABLISHED.

## Tools prepared

Separate frozen implementation and MP005-only manifests; provider-specific minting/preserved exact replay; raw state/log snapshots and hash/count validation; Linux /proc process identity, start ticks/time, command, cwd, executable/version and mount data; independent boundary-signature/correlation with per-send recorder cursors and a final late-event replay recheck; per-assertion scorer; non-self-referential inventories; operator-only live restart checkpoints; host-local preflight hash tools; gated future role launchers.

The simulation runs providers sequentially. It uses unchanged providers and relay with in-memory path/loopback configuration only, a single-target loopback relay route and a simulation-only raw recorder. It never tests the live topology or substitutes fsync/persistence behavior. The platform guard is before provider import/start/output creation. Simulation sockets are restricted to numeric loopback. S03 substitutes old state only inside a verified disposable simulation directory and preserves S0/S1/final evidence.

## Exact future Linux command

Copy/access the entire tree with byte preservation on an approved LOCAL Linux environment. From its root:

```sh
python3 -m pip install -r requirements.txt
python3 simulation/run.py --session MP005_SIMULATED_SMOKE_R1
```

Dependencies: Python 3.10+ on Linux; cryptography >=41,<51; readable /proc and same-user child process metadata; a writable local filesystem supporting the unchanged directory open/fsync path; free loopback ports. No SSH, credentials, external service, lab host, Docker or extra process library is required for simulation. The directory must be fresh; nothing is deleted. Results stay under evidence/simulated_smoke/SESSION/provider/S00–S03. Stop for review afterward. Do not use historical laboratory hosts as a local-environment substitute.

The tree is path-portable as prepared (derived roots and relative manifests); actual Linux execution remains unverified. The source/private laboratory keys are preserved intentionally for reproduction. Future live deployment configuration is deliberately unresolved and gated shut.

## Build checks and disposition

15 Python source files compiled without executing them; eight synthetic helper checks passed; four Linux guards statically checked; 17 implementation/key files remain byte-identical to the pinned published MP003 files. No simulation entry point was invoked. Build-only BOM decoding and default-temp access corrections are recorded in CHECK_ME; they did not change provider artifacts or run any provider.

No live laboratory host contact; no live rehearsal; no scored MP005 run; no GitHub/repository mutation; no final live contract lock. No live authorization or PASS result is asserted. Recommendation: ready to take to an approved LOCAL Linux environment for simulation and review, NOT ready to freeze for live rehearsal yet. Phases remain separate.

## Candidate draft hashes (informational; not a live lock)

| File | SHA-256 |
|---|---|
| MP005_CONTRACT.md | `b4859868f9f6bcaa6d100fb89dfeafb384e95e8fbd49959d8c5c039eace2be25` |
| MP005_SOURCE_MANIFEST.json | `90f41266e17869449a70403baba697a2196d499e007adab49cf519912c3fe913` |
| MP005_IMPLEMENTATION_MANIFEST.json | `63e267b32864251d19bd74130430fed292d159ab795454b7292f8de187b53810` |
| MP005_HARNESS_MANIFEST.json | `2a985ec95d7fcba21da032b6947ffc36f0fab0da04e699daf698ed79c37244f4` |
| MP005_RUN_MANIFEST.json | `059b0c59e818e124d2be75bcc6daab5e42d1d1fbf0b360c66b9c3341e83f25c4` |

## Frozen implementation identities

Pinned published commit: fa541618b1a3bc58700a81b29129b17b35b1e0fc. Registry transcription correction confirmed by operator; source unchanged.

| Relative path | SHA-256 |
|---|---|
| provider_a/provider_a.py | `c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606` |
| provider_b/provider_b.py | `5e0ab4b79df4c97bc7bc324d63da85711728d625b82306cdce6c92592e2ee13e` |
| intermediary/nuvl_multi_relay.py | `09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4` |
| association/association_recorder.py | `fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc` |
| association/provider_registry.json | `59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d` |
| association/trust/provider_a_public.pem | `4f9f01b0296f75a7acf8c3fd11bf7f27d75f0526e7912a02d0a725b1e6fbaa19` |
| association/trust/provider_b_public.pem | `bcb4441a3ad143b5a3d646189d15ba806340c52530ba9b5ef4e19f30e0c59e47` |
| provider_a/mint_authorization_a.py | `1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec` |
| provider_a/provider_a_issuance_private.pem | `37f808b6901f5020fb7b68924217d76f7923d898e44913a6338008d85ac15fd8` |
| provider_a/provider_a_issuance_public.pem | `a52276369981962b878311ec4e33186af25ac10cd359fafbc760e118e607ad71` |
| provider_a/provider_a_private.pem | `f4fb81ff6901b6f9ef8ea4f870430760cf7cdc2eb28dff74125e277fa6465ff9` |
| provider_a/provider_a_public.pem | `4f9f01b0296f75a7acf8c3fd11bf7f27d75f0526e7912a02d0a725b1e6fbaa19` |
| provider_b/mint_authorization_b.py | `1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb` |
| provider_b/provider_b_issuance_private.pem | `fb450986458ee062e1747471cfef731a743b6d3915b1d86bbf0f4c2e7e1e3433` |
| provider_b/provider_b_issuance_public.pem | `07ba26931a6112826f39fdc9a286562f608f394b4f8de4d26f48751855d8fe64` |
| provider_b/provider_b_private.pem | `02e145e18080e3a2dc230d70c6de71f33fa4ff7ec7fed829f313292a845b95d7` |
| provider_b/provider_b_public.pem | `bcb4441a3ad143b5a3d646189d15ba806340c52530ba9b5ef4e19f30e0c59e47` |

## Complete current file tree

Includes earlier CHECK_ME reports and retained synthetic helper fixtures, which are not simulation/scored evidence.

```text
.gitattributes
BUILD_HANDOFF.md
CHECK_ME/MP005_HASH_CORRECTION_CONFIRMED_20261019.txt
CHECK_ME/MP005_LOCAL_SIMULATION_ENVIRONMENT_20261019.txt
CHECK_ME/MP005_PHASE1_BUILD_NOTES_20261019.txt
CHECK_ME/MP005_PHASE1_BUILD_SCOPE_20261019.txt
CHECK_ME/MP005_SOURCE_IDENTITY_ISSUE_20261019.txt
README.md
association/association_recorder.py
association/provider_registry.json
association/trust/provider_a_public.pem
association/trust/provider_b_public.pem
configs/MP005_CONTRACT.md
configs/MP005_DRAFT_SHA256SUMS.txt
configs/MP005_HARNESS_MANIFEST.json
configs/MP005_IMPLEMENTATION_MANIFEST.json
configs/MP005_RUN_MANIFEST.json
configs/MP005_SOURCE_MANIFEST.json
harness/common.py
harness/launch_provider.py
harness/launch_service.py
harness/live_case.py
harness/preflight.py
harness/test_helpers.py
intermediary/nuvl_multi_relay.py
notes/MP005_IMPLEMENTATION_FACTS.json
notes/MP005_IMPLEMENTATION_INSPECTION.md
operator/LIVE_RUNBOOK.md
operator/authorization.example.json
operator/build_checks/PHASE1_BUILD_CHECKS.json
operator/build_checks/helper_fixtures/91c5eee08a554f2d9ce2c77f1c29d6df/association.jsonl
operator/build_checks/helper_fixtures/edf82a7d69d0454ca72b8770cee8d64d/snapshot/execution.jsonl
operator/build_checks/helper_fixtures/edf82a7d69d0454ca72b8770cee8d64d/snapshot/snapshot.json
operator/build_checks/helper_fixtures/edf82a7d69d0454ca72b8770cee8d64d/snapshot/spent_state.json
operator/build_checks/helper_fixtures/edf82a7d69d0454ca72b8770cee8d64d/state.json
provider_a/mint_authorization_a.py
provider_a/provider_a.py
provider_a/provider_a_issuance_private.pem
provider_a/provider_a_issuance_public.pem
provider_a/provider_a_private.pem
provider_a/provider_a_public.pem
provider_b/mint_authorization_b.py
provider_b/provider_b.py
provider_b/provider_b_issuance_private.pem
provider_b/provider_b_issuance_public.pem
provider_b/provider_b_private.pem
provider_b/provider_b_public.pem
requirements.txt
simulation/engine.py
simulation/launch_relay.py
simulation/run.py
```
