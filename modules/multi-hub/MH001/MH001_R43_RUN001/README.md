# MH001 R4.3 — Scored Multi-Hub Experiment

## Purpose

This directory contains the frozen implementation, configuration records, prepared requests, and collected evidence for the MH001 R4.3 multi-hub experiment.

**Session:** `MH001_R43_RUN001`

**Live experiment:** November 7–8, 2026 UTC

**Functional outcome:** PASS, with two procedural documentation limitations disclosed below.

### Question Tested

Can changing the forwarding path cause a provider to accept an authorization that it has already consumed?

MH001 tested this using two independent providers, two separate forwarding hubs, and an independent observer.

The recorded result was:

- Both providers executed valid T01 requests.
- Their original authorizations became spent.
- Hub A was terminated.
- The exact T01 requests were replayed through Hub B.
- Both providers returned signed `DENY / auth_spent`.
- Neither provider recorded another execution or consumption for the replay.
- Both providers subsequently accepted distinct, freshly issued T04 authorizations.

**Changing the forwarding path did not restore consumed authority.**

## 1. Experiment Architecture

```text
                    REQUESTER
                        |
                  INITIAL ROUTE
                        |
                      HUB A
                     /     \
                    v       v
              PROVIDER A   HUB B
                              |
                              v
                          PROVIDER B


                  ALTERNATE ROUTE

                    REQUESTER
                        |
                        v
                      HUB B
                     /     \
                    v       v
              PROVIDER A   PROVIDER B


              INDEPENDENT EVIDENCE

               PROVIDER A    PROVIDER B
                    \          /
                     v        v
                       OBSERVER
```

Each provider independently controls its authorization decisions, signing keys, persistent consumption state, and execution records.

The hubs forward requests. They cannot originate provider authorization or restore spent authority.

The observer verifies signed provider events but cannot authorize execution.

## 2. Directory Map

```text
MH001_R43_RUN001/
├── README.md
├── BASELINE.json
├── HASHES.json
├── REVIEW.md
├── SHA256SUMS.txt
├── deployment.py
├── provider_launcher.py
├── observer.py
├── observer_launcher.py
├── test_deployment.py
├── validate_review.py
├── frozen_R43/
├── configs/
├── trust/
├── association/
├── observer_support/
├── authorizations/
├── rehearsal_inputs/
├── rehearsal_requests/
├── t01_inputs/
├── t01_requests/
├── t04_inputs/
├── t04_requests/
├── validation/
└── evidence/
```

### Where to Start

| Objective | Directory or file |
|---|---|
| Understand the frozen implementation | `frozen_R43/README.md` |
| Examine source provenance | `frozen_R43/provenance/` |
| Review original deployment requirements | `REVIEW.md` and `frozen_R43/OPERATOR_GATES.md` |
| Inspect original network configuration | `configs/` |
| Verify signing identities | `trust/` and `association/` |
| Examine provider-issued authority | `authorizations/` |
| Reconstruct prepared requests | `rehearsal_requests/`, `t01_requests/`, `t04_requests/` |
| Inspect local validation | `validation/` |
| Verify live outcomes | `evidence/README.md` |

The README in each subdirectory documents its own files and verification procedures.

## 3. Original Test Sequence

| Phase | Action | Recorded outcome |
|---|---|---|
| Rehearsal | Valid authority through initial routes | Both providers executed once |
| T01 | New single-use authority through Hub A | Both providers executed once |
| T02 | Terminate designated Hub A process | Alternate Hub B route used subsequently |
| T03 | Replay exact T01 requests through Hub B | Both providers denied `auth_spent` |
| T04 | Submit freshly authorized requests through Hub B | Both providers executed once |

### Important Distinction

T03 did **not** use newly prepared authorization packages.

It reused the original T01 requests preserved under:

`t01_requests/`

No separate `t03_requests/` directory is required.

T04 used newly issued authorization packages preserved under:

`authorizations/`

The distinction between exact replay and fresh authority is necessary to reproduce the test correctly.

## 4. Preserved Implementation

The original R4.3 implementation is located under:

`frozen_R43/`

It includes:

- `hub.py` — forwarding behavior.
- `routes.py` — static route validation.
- `wire.py` — HTTP transport and framing.
- `requester.py` — provider-bound request preparation and transmission.
- `providers/` — preserved provider A/B implementation and issuance tools.
- `provider_support/` — durable ledger validation helpers.
- `test_offline.py` and `test_requester.py` — original offline test suites.

The MH001 deployment and observer integration lives at this scored-run root.

The provider implementation was not rewritten to create the multi-hub behavior.

The test instead changed how requests reached the providers while preserving provider-controlled authorization and consumption enforcement.

## 5. Local Validation History

The preparation package was validated before live testing.

Records are preserved under:

`validation/`

There are three attempts.

| Attempt | Original tests | Deployment tests | Result |
|---|---|---|---|
| 001 | 1 failure, 18 errors | 23 PASS | FAILED |
| 002 | 29 PASS | 23 PASS | PASS |
| 003 | 29 PASS | 23 PASS | PASS |

The two successful attempts each completed **52/52 tests**.

The initial failed attempt remains preserved.

The historical `REVIEW.md` and `HASHES.json` contain the status:

`LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED`

That was the preparation-stage status when those records were created.

They must not be silently rewritten to describe the later live run.

The subsequent experiment's evidence is preserved separately under `evidence/`.

## 6. Historical Integrity Manifests

This directory contains two different SHA-256 inventories.

### Original Local Package Manifest

`SHA256SUMS.txt`

This contains **65 entries** covering the original deployment-review package.

It establishes the identities of the preserved source, configuration, and local-validation materials at that stage.

### Final Scored Experiment Manifest

`evidence/MH001_FINAL_SHA256SUMS.txt`

This contains **132 entries** covering the original scored-run files.

It includes the frozen preparation materials and the additional published live-session artifacts.

### Verify the Final Inventory

From the `MH001_R43_RUN001/` root on Linux:

```bash
sha256sum -c evidence/MH001_FINAL_SHA256SUMS.txt
```

Expected result:

**132 successful file checks, with no mismatches.**

This performs a file-integrity comparison. It does not rerun the experiment or independently establish the truth of every recorded observation.

The manifests are historical records. Newly added README files are supplemental documentation and are not part of the original scored inventory.

Do not regenerate either historical manifest merely to include documentation.

## 7. Independent Live Evidence

The collected experiment evidence is located at:

`evidence/`

Important artifacts include:

| Artifact | Verification purpose |
|---|---|
| `evidence/requester/` | Original send hashes and first-hop destinations |
| `evidence/ingress/` | Requests captured at provider ingress |
| `evidence/final_remote/` | Hub logs and provider consumption/execution records |
| `evidence/observer.jsonl` | Independently verified provider-signed events |
| `evidence/incomplete_startup/` | Preserved earlier incomplete observer startup |

The completed observer session contains:

- 1 SESSION_START.
- 14 provider-signed event submissions.
- 1 SESSION_END.

All 14 submissions recorded successful signature and registry verification.

The decisive T03 denial events appear at observer record sequences 10 and 11.

### T03 — Decisive Result

| Provider | Signed stage | Reason |
|---|---|---|
| PROVIDER_A | DENY | auth_spent |
| PROVIDER_B | DENY | auth_spent |

Both denials reference the originally consumed T01 authorizations.

The final provider histories show no additional T03 consumption or execution.

Each provider subsequently recorded a new T04 consumption and execution, reaching consumption ledger sequence 3.

The evidence is software-execution and provider-state evidence. It is not a physical actuator measurement.

## 8. Independent Audit Sequence

An independent reviewer should examine the original records in this order:

1. Verify the 132-file final SHA-256 manifest.
2. Verify the frozen source and provider identities.
3. Examine the approved configuration and trust records.
4. Verify the original provider-issued authorization signatures.
5. Reconstruct and compare the original T01 prepared request bytes.
6. Confirm the requester receipts identify the original requests and their forwarding destinations.
7. Compare T01 and T03 requests at the provider-ingress boundaries.
8. Independently verify the original observer hash chain and provider signatures.
9. Verify both T03 `DENY / auth_spent` events against the original T01 authorization identities.
10. Examine provider-local ledgers, spent-state records, and execution logs for unchanged T03 state.
11. Verify that distinct T04 authorizations produced one new execution and consumption per provider.
12. Review the procedural limitations in Section 10.

No single hub log, requester response, or observer record independently proves the complete result.

The experiment relies on agreement between separately collected evidence.

## 9. Reproducing the Experiment

A new live reproduction requires an independently authorized laboratory run, not reactivation of this historical directory.

The original reproduction procedure is documented in:

`frozen_R43/OPERATOR_GATES.md`

The necessary sequence is:

1. Establish isolated hosts, paths, and nonconflicting network endpoints.
2. Verify the preserved runtime source identities.
3. Establish fresh provider-controlled signing identities.
4. Initialize new persistent provider consumption state without touching historical state.
5. Establish approved provider trust and an independent observer.
6. Obtain explicit startup approval.
7. Validate the two hub routes and requester allowlist.
8. Establish independent provider-ingress capture.
9. Complete the rehearsal.
10. Execute T01 and preserve both original requests.
11. Obtain the required T02 approval before terminating the designated Hub A process.
12. Verify the intended topology change.
13. Replay the exact T01 request bytes through Hub B during T03.
14. Verify new signed `DENY / auth_spent` events and unchanged provider consumption/execution state.
15. Issue separate new authority for T04.
16. Verify one new execution and consumption per provider.
17. Preserve and hash all new evidence.

Use new output directories and a separate evidence manifest.

The published historical test keys remain available in the sibling directory:

`../original_host_test_keys/`

They support reproduction and verification of the historical cryptographic artifacts.

A new operational run must establish its own approved signing trust and isolated persistent state.

Do not overwrite the historical scored-run material.

## 10. Procedural Documentation Limitations

The original review protocol required specific operator and observer checkpoints.

Two checks were not separately documented in the final evidence:

1. An immediate pre-T03 observer cursor checkpoint independently demonstrating the absence of an earlier matching denial.
2. An immediate pre-T04 reconfirmation that the designated Hub A process and listener remained absent.

The published signed events, forwarding observations, provider-ingress captures, and persistent-state histories support the functional replay-denial result.

However, those two missing procedural records cannot be represented as completed checks.

Consequently, distinguish:

**Functional replay-denial result:** Supported by the published evidence.

**Strict completion of every frozen procedural requirement:** Not fully documented.

A future reproduction should preserve these checkpoints explicitly.

## 11. What MH001 Establishes

Within the tested implementation and environment, MH001 demonstrated:

- Two physically separate forwarding hubs.
- Two independently controlled provider authorization domains.
- Provider-specific, single-use signed authorization.
- Durable consumed-authority state.
- Exact replay through an alternate forwarding route.
- Provider-signed rejection of consumed authority.
- Continued acceptance of separately issued fresh authority.
- Independent provider-event verification and evidence correlation.

MH001 does not establish arbitrary topology tolerance, resistance to every network attacker, or security following compromise of a provider's private signing keys.

The experiment also does not grant execution authority to the requester, hubs, or observer.

## 12. Preservation Rules

The original scored artifacts are immutable historical records.

Do not modify:

- Frozen source or configuration.
- Original authorization packages.
- Original request bytes.
- Provider ledgers or spent-state snapshots.
- Provider-ingress packet captures.
- Observer records.
- Historical validation failures.
- Original SHA-256 manifests.

New documentation may be added separately without rewriting those records.

For independent reproduction, establish a new run identity and preserve new evidence under separate paths.

## Conclusion

MH001 tested whether a change in forwarding topology could restore consumed provider authority.

Both providers rejected the exact replay and subsequently accepted fresh, separately issued authority.

**The path changed. The provider-controlled execution boundary remained authoritative.**
