# MD-001 desktop baseline

Local build only. No Dell, HP, Pi, switch, OPNsense, or ESP deployment was performed.
See COMPLETION.md for the exact validated run, totals, hashes, and STOP status.

From the project root, using Python with `cryptography==49.0.0` installed:

```powershell
python -B MULTI_DOMAIN_001/tests/run_offline.py
python -B MULTI_DOMAIN_001/manifest.py --check
```

Each test creates a new `evidence/offline/<UTC>_<random>/` directory. Loopback socket
access is necessary. Do not run any historical reference test or deployment script.
The existing `prepare_reference.py` was used to create the byte-preserving snapshot;
rerunning it requires the same original source locations and never replaces differing
reference bytes. The baseline runs from the copied references without those originals,
but the source-integrity check additionally requires originals at their inventoried paths.

The harness starts a producer, verifier, frozen MH001 relay, and external application
taps. Domain A sorts `[9,1,4,2]`, checks `[1,2,4,9]`, and signs at completion. The
operation record stays in producer evidence. Only the defined signed assertions cross
the relay. B01 compares saved producer, relay-adjacent, and verifier artifact bytes.
N01 sends the original through an unchanged relay into a separate downstream mutation
adapter. B02 terminates the simulated producer, records a refused loopback connection,
terminates the original verifier, starts a new verifier process, and submits the exact
B01 artifact through an unchanged relay. A second request proves repeated acceptance
inside the restarted process. Every acceptance calls Ed25519 verification anew.

This is desktop process separation and loopback transport, with a single operator
controlling all processes. It does not establish physical independence or power-loss
behavior. There are three baseline simulations (B01/B02/N01); supporting checks do not
expand the scored matrix. X01 is required documentation, unscored.

`src/artifact.py` implements the assertion contract and pure verifier.
`src/service.py` contains launch and HTTP adapters. The latter is desktop test
infrastructure, restricted to loopback. Physical binding and production service
hardening require a separately reviewed deployment adapter at STOP 2.
`reference/` contains frozen, byte-identical inspection snapshots, including stateful
historical files that are never imported. Only MH001 `hub`, `wire`, and `routes` execute.
`tests/` contains orchestration. `configs/` contains a proposed, unapplied network design.
`evidence/physical/` is reserved for later authorized evidence and has no results.

Trust is provisioned out of band into the run's public-only `trust.json`. The harness
generates a disposable private test key in `test_keys/`, gives it only to the producer,
and retains it for exact-byte reproduction. Neither relay nor verifier receives that
private key. These published-style test fixtures must never become production keys.
The test preserves signed bytes, transmitted bytes, mutation, process identities,
observed decisions, UTC evidence timestamps, configurations, logs, dependency versions,
and per-run manifests. New random IDs and keys intentionally change a fresh run's hashes;
the retained key, event ID, and canonical bytes reproduce an existing signature exactly.

Read ARTIFACT_CONTRACT.md, X01_DISCLOSURE.md, SOURCE_REUSE.md, PROVENANCE.md,
DEPLOYMENT_PLAN.md, ROLLBACK.md, and PHYSICAL_EXTENSION_PLAN.md before later stages.
Verification authenticates an assertion under a trusted key. It grants no execution
authority and does not independently prove that the asserted event happened.
