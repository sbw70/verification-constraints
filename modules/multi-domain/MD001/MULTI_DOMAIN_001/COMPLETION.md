# STOP 1 completion report — MD-001 R1

**MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED**

Final run: `evidence/offline/20261112T025926Z_4d05fe22/`.
All observations are desktop loopback simulations. Physical network and ESP cases
remain unscored and unperformed. STOP 2 has not begun.

1. **Sources located:** MH001_DEPLOYMENT_REVIEW_R43/frozen_R43 (R4.3),
   MP005-reference/modules/multi-provider/MP005 and MP004, MULTI_PROVIDER_006,
   and MP005-reference/labs/nuvl-edge/esp-local/ESP_LOCAL_008. Exact absolute paths,
   revisions, 34 file hashes and baseline comparisons are in
   `reference/SOURCE_INVENTORY.json`; compatibility and dependencies are in SOURCE_REUSE.md.
2. **Unchanged reuse:** MH001 hub.py, wire.py, routes.py; MP005 canonical_bytes function
   copied verbatim. Signing/verification primitive patterns are adapted; no whole
   stateful MP005/MP004 component is imported. Selected inspection references and the
   operator handoff retain original bytes. MP006 evidence conventions inform new code.
3. **New components:** assertion contract and stateless verifier, producer operation,
   loopback HTTP and relay launch adapters, external application taps, downstream-only
   mutation adapter, offline orchestration, source inventory preparation, manifest
   verification utility, public trust provisioning, X01 inventory and deployment plans.
4. **Offline tests executed:** B01 relay conveyance and independent acceptance; B02
   simulated unavailable producer and restarted verifier; N01 modified-field rejection;
   supporting signature/schema/key-binding/canonicalization/repeated-verification,
   unique-ID, no-network/file-dependency, execution-import separation, source integrity,
   saved-evidence consistency checks. Exact checks and observations are in RESULTS.json.
5. **Totals:** 21 PASS, 0 FAIL in the final run. B01/B02/N01 simulations all PASS.
   X01 documented, unscored. One prior 21/0 run is retained. Initial sandbox-blocked
   infrastructure attempt is retained separately (1 PASS, 1 harness FAIL); it did not
   reach a cryptographic case decision. No failed attempt was replaced or hidden.
6. **Evidence:** final run contains producer operation record, original envelope,
   exact signed bytes, disposable key, public-only trust configuration/provisioning,
   relay-adjacent application observations, mutated envelope and mutation description,
   verifier ingress bytes/decisions, process identities/stdout/stderr, source snapshot
   and hashes, relay configuration/logs, unavailable-producer observation and manifest.
   B02 old PID 20908, new PID 25580; process-instance identities and start timestamps
   also differ. Same artifact accepted again with one fresh Ed25519 check per request.
7. **SHA-256 identities:**

   | Object | SHA-256 |
   |---|---|
   | Original artifact / all four B01 artifact observations | `7534a478ad51ffd1ac2ca05bff2039813d0305a8e05174d572a1ffc3e021f64b` |
   | Modified artifact | `5b747613a2baa19ef6f2f69cf936c528c4f4b4c7ad9674ec014e5bda5b614b64` |
   | Final RESULTS.json | `667c676b3b90ea65e47d4a78ac62b9b605d632697a838f48f8215aed7548b6f7` |
   | Final run SHA256SUMS.txt | `9ee74d9c81c1707ccb703cfa05f5eec7373ec9cc04778d137474ab4491927484` |
   | Frozen MH001 hub.py | `37bd590d23d2daf3bf8b9713139a27b09333252f62d87c94fa2a3e1477a043a2` |
   | New src/artifact.py | `f814d37b52d0b3b64a242b0c37d5bcc9d3fe6511f4bf1e4ada2285c7cbac196b` |

   Package manifest: root SHA256SUMS.txt; its digest: MANIFEST_SHA256.txt. These are
   generated after this report to avoid a circular checksum. Verify with
   `python -B MULTI_DOMAIN_001/manifest.py --check` from the project root.
8. **Adapters / departures:** unchanged HUB_B class is launched without the incompatible
   frozen two-hub CLI. Desktop role labels and tagged artifact schema differ from
   historical provider authorization formats by design. New verifier needed because
   historical lifecycle/authority schemas do not fit assertion-only verification.
   External application taps replace physical Pi packet reconstruction only in
   simulation; this is not physical packet evidence. No added artifact fields beyond
   the proposed six assertions; signature is envelope metadata. All adaptations were
   disclosed before implementation. No expansion of scored cases or live deployment.
9. **Network prerequisites:** inspect actual interfaces/MACs, firmware, current routes,
   services, VLAN tagging, management reachability and existing MP005/MH001 topology;
   resolve conflicts and physical port availability; complete reviewed physical service
   adapters and unused route disposition. Approve exact resolved changes at STOP 2.
   Proposed port/VLAN/address/rule tables, capture method, preflight probes and rollback
   are in DEPLOYMENT_PLAN.md, configs/deployment.PROPOSED.json and ROLLBACK.md.
   Physical B01 needs exported effective rules, actual logged denied A-to-B attempt,
   approved path connectivity and reconstructed identical artifact bytes across relay.
   Physical B02 additionally needs operator power-off observation, failed producer
   connection and a documented fresh verifier process. Then STOP 3 approval is required.
10. **Physical extension prerequisites:** original ESP_LOCAL_004 test private key is
    absent; restore the established pinned fixture, never substitute the MD001 key.
    Verify endpoint identity/state and frozen firmware, witness build/pin/wiring and
    capture health; arrange functioning loaded B command capability with independent
    provider issuance and handler separation; obtain separate actuation approval.
    Require zero observed execution-triggered PWM bursts in B01/B02/N01 and exactly
    one independently authorized positive-control burst. No witness evidence exists
    for MD001. Detailed design and source inconsistencies are in PHYSICAL_EXTENSION_PLAN.md.
11. **Known blockers and limits:** no unresolved desktop-baseline blocker. Uninspected
    live network and missing established physical test key block later stages. Loopback
    processes share one operator/host and do not prove independently controlled
    physical domains. No physical power-off, firewall enforcement, Pi packet capture,
    physical execution isolation or production readiness claim. A signature authenticates
    assertions under a provisioned key, not underlying event truth. X01 defines limited
    observed disclosure and makes no absolute confidentiality claim. Desktop service
    hardening and deployment binding remain future work within a separately approved stage.
12. **Current gate:** STOP 1 complete. Stopped. No live network setting changed, remote
    host deployed, physical scored test run, authority minted or ESP command triggered.
    Do not begin STOP 2 or STOP 3 automatically. No public-facing claim is prepared.
