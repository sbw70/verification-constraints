# MH001 — Provenance and Evidence Integrity

**Project:** Xer0trust / Neutral Unified Verification Layer (NUVL)

**Experiment:** MH001 — Multi-Hub Authority Persistence

**Implementation:** R4.3

**Scored session:** `MH001_R43_RUN001`

**Execution dates:** November 7–8, 2026 UTC

**Recorded functional result:** Provider A PASS / Provider B PASS

**Procedural qualification:** Two frozen scoring checkpoints were not separately documented.

## 1. Purpose

This document establishes the source, configuration, signing-key, execution, and evidence provenance for MH001.

MH001 tested whether previously consumed provider-controlled execution authority could be restored by changing the request's forwarding path.

The provenance record identifies:

- Frozen implementation sources.
- Earlier MP005 implementation dependencies.
- Local validation history.
- Reviewed configuration identities.
- Provider signing-key identities.
- Operator startup approval records.
- Original authorization and request artifacts.
- Hub forwarding and provider-ingress observations.
- Provider-controlled persistent state.
- Independent signed-event evidence.
- Original file-integrity manifests.
- Supplemental historical test-key publication.

Provenance establishes the identity and relationships of preserved artifacts.

It does not independently prove that every reported experimental observation occurred or that the implementation is secure under conditions outside the test.

The experimental findings are documented separately in [RESULTS.md](RESULTS.md).

## 2. Repository Location

Repository:

https://github.com/sbw70/verification-constraints

Experiment directory:

`modules/multi-hub/MH001/`

Scored-run directory:

`modules/multi-hub/MH001/MH001_R43_RUN001/`

Primary documentation:

- [Experiment overview](README.md)
- [Experimental results](RESULTS.md)
- [Scored-run documentation](MH001_R43_RUN001/README.md)
- [Original deployment review](MH001_R43_RUN001/REVIEW.md)
- [Frozen operator gates](MH001_R43_RUN001/frozen_R43/OPERATOR_GATES.md)
- [Original scored evidence](MH001_R43_RUN001/evidence/)
- [Original test signing keys](original_host_test_keys/)

The original scored files remain in their session-specific locations.

Documentation added after the experiment is not represented as contemporaneous scored evidence.

## 3. Source Lineage

### Original Provider Implementation

MH001 builds on the multi-provider implementation previously used by MP005.

The recorded provider-source reference commit is:

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

The source reference is associated with:

`modules/multi-provider/MP005/`

The preserved provenance records are:

- [github_source_text.json](MH001_R43_RUN001/frozen_R43/provenance/github_source_text.json)
- [github_support_text.json](MH001_R43_RUN001/frozen_R43/provenance/github_support_text.json)

These records preserve the source text and original repository locations of the provider and supporting implementations.

The corresponding published provider-source copies are under:

`MH001_R43_RUN001/frozen_R43/provenance/published/`

### Frozen R4.3 Implementation

The frozen R4.3 package contains:

- Hub forwarding implementation.
- Static route validation.
- HTTP framing and transport.
- Requester preparation and transmission.
- Provider A and Provider B implementations.
- Provider authorization-issuance tools.
- Provider consumption-ledger helpers.
- Original offline tests.
- Historical validation records.
- Original source and configuration inventories.

The frozen package is located at:

`MH001_R43_RUN001/frozen_R43/`

The scored-run `BASELINE.json` records 41 frozen source/support identities, including the two reused observer-support helpers.

The original R4.3 source was preserved rather than rewritten to implement the MH001 deployment integration.

### MH001-Specific Integration

The additional scored-run code is located at:

`MH001_R43_RUN001/`

It includes:

| File | Responsibility |
|---|---|
| `deployment.py` | Source, configuration, trust, and startup approval checks |
| `provider_launcher.py` | Provider-specific inspection and gated startup |
| `observer.py` | Independent signed-event and provider-state correlation |
| `observer_launcher.py` | Observer inspection, startup, checkpoint, and verification |
| `test_deployment.py` | Additional offline deployment and evidence tests |
| `validate_review.py` | Guarded local validation runner |

These components adapt the frozen implementation to the MH001 deployment and evidence workflow.

They do not introduce a new provider authorization algorithm or transfer authority to the hubs.

## 4. Frozen Source Identities

Selected original SHA-256 values:

| Component | SHA-256 |
|---|---|
| Provider A | `79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6` |
| Provider B | `618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605` |
| Hub runtime | `37bd590d23d2daf3bf8b9713139a27b09333252f62d87c94fa2a3e1477a043a2` |
| Requester | `d65db8ab4ec484be398954a315fe2da6157cc5428289c1a3abbed922080e5190` |
| Routes | `627de0618ecba71655a107a6fb6b1c8776f8a1f6983fd778470405855e0e8969` |
| HTTP transport | `8a668ab4af072ad2c24a0af5d0baca0a22f0e8946fa40f57ad92330894fac87f` |
| Ledger helper | `3f5e27dac5a8e1ae88974effb4b3e82c626ba8345ea6524e6d2c33edd8e39637` |
| Observer recorder | `fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc` |
| MH001 deployment adapter | `1e057b86db0330ab23a2e6ec92141943c375f00c9ee048ddd9910191b775574f` |
| MH001 observer adapter | `eadf9bd1d303e7810aca68956700726d775c94c66092076a96b78532cae50c80` |

The complete source identities are preserved in:

- `MH001_R43_RUN001/BASELINE.json`
- `MH001_R43_RUN001/HASHES.json`
- `MH001_R43_RUN001/SHA256SUMS.txt`
- `MH001_R43_RUN001/evidence/MH001_FINAL_SHA256SUMS.txt`

These records identify different stages of preparation and publication.

The earlier MP005 reference commit identifies reused source lineage. It is not a claim that all MH001-specific files existed at that earlier commit.

## 5. Local Validation Provenance

MH001 preserved three local validation attempts dated November 5, 2026 UTC.

| Attempt | Original R4.3 tests | New deployment tests | Status |
|---|---|---|---|
| 001 | 1 failure, 18 errors | 23 PASS | FAILED |
| 002 | 29 PASS | 23 PASS | PASS |
| 003 | 29 PASS | 23 PASS | PASS |

The successful attempts each completed 52 tests without failures or errors.

The initial Windows socket-access failure remains preserved.

The local validation runner prohibited:

- Actual provider imports.
- New signing-key generation.
- Provider-state initialization.
- Observer startup.
- Non-loopback laboratory network contact.
- Live deployment.

The historical successful validation status was:

`LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED`

The recorded `STOP_1` status remained `ACTIVE` during local validation.

These values reflect the preparation stage.

They were not revised after the separately authorized live experiment.

The validation records are preserved at:

[validation/](MH001_R43_RUN001/validation/)

## 6. Configuration Provenance

The scored experiment used the following recorded endpoints.

| Component | Recorded address |
|---|---|
| Hub A | `192.168.1.100:18080` |
| Hub B | `192.168.1.106:18081` |
| Provider A | `192.168.1.118:18090` |
| Provider B | `192.168.1.107:18091` |
| Independent observer | `192.168.1.102:9191` |

These are historical laboratory addresses, not permanent deployment defaults.

The reviewed route configuration required:

- Hub A to forward Provider A directly.
- Hub A to forward Provider B through Hub B.
- Hub B to forward directly to both providers.
- The requester to use only explicitly approved non-loopback hub endpoints.
- No automatic retry or route substitution after a forwarding failure.

### Recorded Configuration Hashes

| File | SHA-256 |
|---|---|
| `configs/approved_hubs.json` | `4588635b63ebc1dee6ca15b3de930726edb503cd3032a93d66bf79ba8b2c54b8` |
| `configs/provider_a.json` | `4f89bc9f0f29e39393ecab26c6001b7d6d6f6b1aaaca614da71e82c6d0ddb58b` |
| `configs/provider_b.json` | `661754ab55105b4fa154b77b8cc16a5da52809269140d185115fab00888ebfcf` |
| `configs/observer.json` | `4960e35cfde9a1bd43cddb615030e0ef83b478c717c59049f59616e3d367735a` |

The frozen Hub A and Hub B route files are preserved under:

`MH001_R43_RUN001/frozen_R43/live_review_R43/`

The original configurations must not be modified to accommodate a different laboratory.

## 7. Provider Signing-Key Provenance

MH001 used independent Ed25519 signing identities for both providers.

Each provider had:

- An authorization-issuance keypair.
- A boundary-event signing keypair.

The final approved identity record is:

`MH001_R43_RUN001/trust/provider_keys.json`

Its status is:

`APPROVED_PROVIDER_HOST_KEYS`

The original pending record is preserved separately as:

`MH001_R43_RUN001/trust/provider_keys.pending.backup.json`

### Approved Key Identifiers

| Provider | Issuance key ID |
|---|---|
| A | `sha256:f80897de6f5693caedf5a63e9da63cfd683b3c9c6a42bbf6d40defed35ab1664` |
| B | `sha256:44a1f266d623faa86487cdc85244f7c95bb8fdb18aa1537e27a17a85fc704022` |

| Provider | Boundary-event key ID |
|---|---|
| A | `sha256:43938d000689ef68e298d69c19dd2b5879efc7daf27e6af8bd099f577c91c789` |
| B | `sha256:9ab1cd6d33fea596624f7d2a0e93442746bee9c97ad237d338c23b4385ebb445` |

All four key identifiers are distinct.

Each identifier uses SHA-256 over the raw Ed25519 public-key bytes.

These identifiers must not be confused with SHA-256 hashes of the PEM files themselves.

### Observer Trust

The independent observer registry is:

`MH001_R43_RUN001/association/provider_registry.json`

Its SHA-256 is:

`893cd6153db95ba93016c894adfd3f4c577921a3a3abbed922080e5190`

**Correction to the value above:** The actual preserved registry SHA-256 is:

`893cd6153db95ba93016c894adfd3f4c577921a3bd099f577c91c789`

The observer's public keys are:

- `association/trust/provider_a_public.pem`
- `association/trust/provider_b_public.pem`

Their recorded PEM-file SHA-256 values are:

| Public key | SHA-256 |
|---|---|
| Provider A | `4575b0b5fe2b4b6bf90c80313c889dc44b415e9bf73af0bcbc39b8ac1e4dee6c` |
| Provider B | `f6255b7402eeebb16b92917ce47e48cc03ecee003530816f2951e1f17b5d75af` |

Only boundary-event public keys belong in the independent observer trust registry.

The observer does not possess provider authorization-issuance authority.

## 8. Original Test-Key Publication

After the scored experiment, the original provider-host test signing keys were published under:

[original_host_test_keys/](original_host_test_keys/)

The directory contains eight PEM files:

- Provider A issuance private/public pair.
- Provider A boundary-event private/public pair.
- Provider B issuance private/public pair.
- Provider B boundary-event private/public pair.

The publication is intentional.

These are the original disposable laboratory keys used for the historical experiment, not regenerated substitutes.

Their original file bytes and SHA-256 values are preserved for independent verification and exact reproduction.

Because the private keys are publicly disclosed, they must not be treated as secret operational signing credentials.

### Inventory Boundary

The eight published test-key files are **not included** in the original 132-file scored-run manifest.

They were added separately as supplemental reproducibility material.

This separation must remain intact.

Do not replace the original test keys or alter historical signatures and hashes.

## 9. Operator Approval Provenance

The original startup approval records are preserved under:

`MH001_R43_RUN001/authorizations/`

The completed approval files are:

- `provider_a_LIVE_STARTUP_APPROVED.json`
- `provider_b_LIVE_STARTUP_APPROVED.json`
- `observer_LIVE_STARTUP_APPROVED.json`

The corresponding pending records are also preserved.

Each completed startup approval records:

- `authorized: true`
- `phase: LIVE_STARTUP`
- Session `MH001_R43_RUN001`.
- The relevant configuration SHA-256.
- The approved trust-file SHA-256.
- Eleven required source-code SHA-256 identities.

Approved provider trust SHA-256:

`d9c304ff67316c7f91b6be5225519cdd7f899a18c972edb4bf2e2fe052a14b86`

The three completed approvals reference that same trust identity.

These files represent recorded local operator startup authorization.

They are not provider-issued operation authorizations, and their JSON contents are not themselves cryptographically signed.

Control of the operator approval files is a deployment trust assumption.

Separate provider-issued authorization packages are preserved in the same `authorizations/` directory.

## 10. Original Request and Authorization Provenance

The experiment preserved original provider-issued authorizations for:

- Rehearsal.
- T01.
- T04.

The corresponding preparation artifacts are under:

- `MH001_R43_RUN001/rehearsal_inputs/`
- `MH001_R43_RUN001/rehearsal_requests/`
- `MH001_R43_RUN001/t01_inputs/`
- `MH001_R43_RUN001/t01_requests/`
- `MH001_R43_RUN001/t04_inputs/`
- `MH001_R43_RUN001/t04_requests/`

The prepared request directories contain the original HTTP request, body bytes, and requester observation.

### T03 Exact Replay

T03 did not create or mint a new authorization.

It reused the preserved T01 requests.

The requester receipts identify matching T01 and T03 request hashes.

| Provider | Original and replay request SHA-256 |
|---|---|
| A | `bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33` |
| B | `ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84` |

These hashes identify the prepared requester HTTP bytes.

The provider-ingress captures verify the received bytes after the permitted transport-level Host header rewrite.

The two T03 replayed authorizations retained their original T01 authorization IDs, nonces, signatures, and bindings.

That distinction is central to the experimental claim.

## 11. Physical Laboratory Provenance

The recorded laboratory roles were:

| Host | Responsibility |
|---|---|
| Raspberry Pi 3B+ | Hub A |
| HP Pavilion | Hub B |
| Dell Latitude | Provider A |
| HP laptop | Provider B |
| HP OmniBook | Requester, independent observer, and operator workstation |

The test used separate provider hosts and a separately hosted observer.

The providers maintained their own local persistent consumption and execution state.

The hubs maintained forwarding observations, not provider authorization-consumption ledgers.

The original host addresses and configuration records are retained in the scored-run archive.

This experiment used provider software-execution evidence.

It did not score physical actuator movement.

## 12. Evidence Collection Provenance

The completed experiment preserved independent observations from several components.

### Requester

Directory:

`MH001_R43_RUN001/evidence/requester/`

Contains:

- Eight original request transmission receipts.
- One Windows Packet Monitor ETL capture.

Requester ETL SHA-256:

`97262a251cf1430d5ac9e5e08b61599c90e490cf2448809caa2f049e8d0441c1`

The receipts identify the preserved request hashes and selected first-hop hub endpoints.

They deliberately record:

`provider_execution: NOT_INFERRED`

### Hub A and Hub B

Directory:

`MH001_R43_RUN001/evidence/final_remote/`

Original forwarding-log hashes:

| Log | SHA-256 |
|---|---|
| Hub A | `0b59483f08163e4ce216fffa5b4ec3934cb1b91eeb392c3d150a24ee9319df8c` |
| Hub B | `5f5210a34780ecc2fac9f3fecf646bab3de627d0dbcc690e6046f0ef569a76bb` |

The logs preserve ingress/egress body hashes, selected next hops, and transport results.

They do not independently prove provider authorization or execution.

### Provider-Ingress Capture

Directory:

`MH001_R43_RUN001/evidence/ingress/`

| Capture | SHA-256 |
|---|---|
| Provider A | `d5aad81b773d1f956473004e2118cc41fb965a7796cdc31e5ad81cce05cb3064` |
| Provider B | `20fda67122fde9dec0eeefc8b121cdc2f6dfe0efe6900f90e9a6f4d435618f9c` |

Both captures preserve original provider-ingress network traffic.

Each contains four incoming HTTP requests:

1. Rehearsal.
2. T01.
3. T03.
4. T04.

The original post-run verification reported eight matching provider-ingress requests.

Both providers' T01 and T03 requests were byte-identical at ingress.

### Provider Persistent State

Directory:

`MH001_R43_RUN001/evidence/final_remote/`

Each provider preserves:

- A hash-linked authorization-consumption ledger.
- A persistent spent-authority snapshot.
- A software execution log.

The final records contain three consumptions and three software executions per provider.

Their recorded phases are rehearsal, T01, and T04.

No T03 execution or consumption entry appears.

The final provider-state files are not separate before-and-after T03 snapshots. Their interpretation relies on the other preserved evidence.

## 13. Independent Observer Provenance

The completed independent observer log is:

[observer.jsonl](MH001_R43_RUN001/evidence/observer.jsonl)

Original SHA-256:

`e4b6e09413081e0d5f932a8485acfd1f27e1c79e43dbfc290c7f01cc3f9ea5dd`

The session contains 16 records:

| Record type | Count |
|---|---:|
| SESSION_START | 1 |
| Provider START | 6 |
| Provider COMPLETE | 6 |
| Provider DENY | 2 |
| SESSION_END | 1 |

All 14 provider submissions recorded:

- `sig_valid: true`
- `registry_match: true`
- `verification_code: ok`

The original observer record chain begins with a 64-character zero hash.

The completed session ends with record hash:

`df02d012c01efa7c9e12a4b86020c4af34d25474b7b09bc0ad54510309c4f9b4`

### T03 Signed Denials

| Observer sequence | Provider | Signed result |
|---|---|---|
| 10 | A | DENY / auth_spent |
| 11 | B | DENY / auth_spent |

Each denial identifies the corresponding original T01 authorization and ledger sequence 2.

Independent verification requires checking the original signed envelope against the approved Ed25519 public key.

The observer's recorded verification fields are evidence, not substitutes for recalculating the signatures.

### Earlier Incomplete Observer Attempt

An earlier observer startup produced a one-record incomplete session.

It is preserved at:

`MH001_R43_RUN001/evidence/incomplete_startup/`

That attempt was excluded from scored provider-event correlation.

Its historical record must not be merged with the completed 16-record observer session.

## 14. Original File-Integrity Manifests

Two distinct inventories are preserved.

### Local Deployment-Review Manifest

File:

`MH001_R43_RUN001/SHA256SUMS.txt`

Contains:

**65 original file entries.**

This inventory belongs to the earlier local deployment-review package.

It does not include the later scored evidence.

### Final Scored-Run Manifest

File:

`MH001_R43_RUN001/evidence/MH001_FINAL_SHA256SUMS.txt`

Contains:

**132 original file entries.**

The published post-run verification reported:

**132/132 files matched their recorded SHA-256 values.**

The final manifest includes source, configuration, trust, authorization, request, validation, and scored evidence files.

The manifest itself is not one of its own entries.

Its recorded SHA-256 is:

`b86996ae2b7a50754ddccf41a688130814689f907e57bbbb6f7e4b516a4cf005`

### Verify Original Scored Files

From the `MH001_R43_RUN001/` directory on Linux:

```bash id="ajv1ch"
sha256sum -c evidence/MH001_FINAL_SHA256SUMS.txt
```

Expected result: 132 successful file checks.

This verifies byte identity against the published manifest.

It does not independently establish execution, network delivery, or the truth of operator observations.

Documentation added later is not included in the original scored inventory.

## 15. Evidence Correlation Requirements

An independent reviewer should correlate the following records.

| Evidence | Required relationship |
|---|---|
| Approved configuration | Matches reviewed endpoints and routing |
| Provider trust | Matches provider signing-key identities |
| Authorization packages | Valid signatures and provider-bound identities |
| T01 request files | Match original requester receipt hashes |
| T03 requester receipts | Reuse exact T01 request hashes |
| Hub forwarding logs | Preserve request bodies and intended next hops |
| Provider-ingress PCAPs | Show actual T01/T03 provider receipt and byte equality |
| Observer events | Authenticate the provider's START, COMPLETE, and DENY statements |
| Provider consumption ledgers | Show the original authorizations as spent |
| Provider execution logs | Show no additional T03 execution |
| T04 records | Show separate fresh authorization and one new execution per provider |

The relevant state and signed-event identities must agree.

A hub's HTTP response does not establish successful provider execution.

A valid provider signature does not independently prove which forwarding path was used.

A final state snapshot does not independently establish every intermediate state.

The complete result depends on agreement between the separately collected records.

## 16. Historical and Procedural Limitations

The frozen operator procedure required specific checkpoints before replay and fresh-authority execution.

Two were not separately documented:

1. An immediate pre-T03 observer cursor checkpoint establishing the absence of an earlier matching denial.
2. An immediate pre-T04 confirmation that the designated Hub A process and listener remained absent.

The completed observer record, provider-ingress captures, forwarding logs, and final provider histories support the functional replay-denial conclusion.

However, these missing procedural observations cannot be represented as completed.

The original provider-state files also preserve final histories rather than separate scored before-and-after T03 snapshots.

The recorded result is therefore distinguished from a claim of perfect procedural completeness.

### Other Limits

MH001 does not establish:

- Physical actuator execution.
- Security under arbitrary hub or provider compromise.
- Security following provider signing-key compromise.
- Operation under every possible network topology.
- Global event chronology based on synchronized host clocks.
- Complete absence of undetected network anomalies.
- Provider-outcome relay through hubs.

Provider-outcome relay through the hubs was outside MH001 scoring.

## 17. Publication and Preservation

The historical source, configuration, authorization, transport, observer, and provider-state files are preserved for independent examination.

The original 132-file scored inventory must remain unchanged.

The eight original provider-host test signing keys are preserved separately as supplemental reproducibility material.

The publication includes original failures and incomplete attempts rather than replacing them with later successful records.

Do not:

- Rewrite original source or configuration.
- Replace original signing keys.
- Alter authorization packages or signatures.
- Normalize original request bytes.
- Modify packet captures.
- Reset provider consumption state.
- Rewrite observer or forwarding logs.
- Delete failed validation attempts.
- Merge separate observer sessions.
- Regenerate historical manifests to include later documentation.

New reproductions must establish their own run identities, signing trust, persistent state, and evidence inventories.

This document is supplemental publication documentation and not an original scored-run artifact.

## Conclusion

MH001 preserves a traceable chain from frozen provider source and approved configuration through original authorization issuance, mechanical forwarding, independent provider ingress, signed provider decisions, and persistent execution state.

The recorded evidence supports the conclusion that both providers rejected their previously consumed authority after the forwarding path changed, while continuing to accept new, separately issued authority.

The two undocumented procedural checkpoints remain explicit limitations.

**The historical evidence is preserved to permit independent verification without transferring authority to the forwarding or observation layers.**
