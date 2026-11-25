# MD001 — Multi-Domain Stateless Verification

**Organization:** Xer0trust LLC  
**Experiment:** MD001  
**Technology:** Multi-Domain Stateless Verification (MDSV)  
**Scored date:** November 19, 2026  
**Status:** THREE PHYSICAL-NETWORK SCORED CASES COMPLETED

---

## 1. Overview

MD001 evaluates whether an assertion originating in one technical domain can be independently verified in another domain without requiring shared operational state, shared authorization authority, or continued availability of the originating provider.

The experiment uses:

- A local operation performed by Domain A.
- An Ed25519-signed assertion describing the operation.
- A mechanical intermediary that transports the assertion.
- A receiving domain that independently verifies the assertion.
- Locally provisioned public-key trust.
- Recorded packet, artifact, process, and verification evidence.

The experiment separates assertion verification from operation authorization.

The intermediary does not issue authority, determine whether the operation was permitted, or execute the operation.

The receiving domain independently determines whether the assertion satisfies its verification criteria.

### Core Property

> A signed assertion can cross a technical-domain boundary without transferring the originating domain's signing authority or requiring the originating domain to remain online during subsequent verification.

MD001 evaluates this property within a defined laboratory configuration.

---

## 2. Publication Records

| Record | Purpose |
|---|---|
| [RESULTS.md](RESULTS.md) | Consolidated physical scored results, supporting observations, and experimental limitations |
| [PROVENANCE.md](PROVENANCE.md) | Source identities, evidence origins, runtime conditions, historical integrity records, and publication exclusions |
| [ORIGINAL_HASH_REFERENCES.tsv](ORIGINAL_HASH_REFERENCES.tsv) | Individual historical checksum coverage classifications for all 110 scored evidence files |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Consolidated 602-entry publication-time SHA-256 inventory |

The publication records consolidate retained experimental evidence without replacing the original observations.

Historical checksum references and publication-time checksums serve different purposes.

Historical references document previously recorded artifact and file identities. Publication-time checksums establish byte consistency against the selected publication inventory.

Publication-time checksums do not establish retrospective collection-time integrity.

---

## 3. Architecture

```text
DOMAIN A — PRODUCER
Dell
10.10.10.10
       |
       | Execute LOCAL_SORT_V1
       | Generate signed assertion
       |
       v
MECHANICAL RELAY
Raspberry Pi
30.30.30.30:18081
       |
       | Forward signed assertion
       | No signing authority
       |
       v
DOMAIN B — INGRESS
HP
40.40.40.40:18443
       |
       | Forward to local verifier
       |
       v
DOMAIN B — VERIFIER
127.0.0.1:18444
       |
       | Resolve locally provisioned key
       | Verify Ed25519 signature
       | Evaluate assertion criteria
       |
       v
VERIFICATION RESULT
```

### Responsibility Separation

| Component | Responsibility |
|---|---|
| Domain A | Performs the local operation and signs its assertion |
| Mechanical relay | Transports the signed assertion |
| Domain B ingress | Receives the assertion and forwards it to the verifier |
| Domain B verifier | Independently evaluates the signed assertion |
| Operator | Controls deployment, scoring, and evidence collection |

The relay does not require the producer's private key.

The verifier does not require access to Domain A's operational database or live execution environment.

The experiment does not introduce a shared authorization ledger.

---

## 4. Operation Under Test

Domain A performs a local sorting operation.

```text
Operation: LOCAL_SORT_V1

Input:
[9, 1, 4, 2]

Output:
[1, 2, 4, 9]
```

After completing the operation, Domain A creates a signed assertion.

The assertion identifies:

```text
version
producer_id
key_id
artifact_id
event_id
outcome
```

The experiment uses:

```text
producer_id = DOMAIN_A
event_id = LOCAL_SORT_V1
outcome = SUCCESS
```

The assertion is signed using Ed25519.

Domain B evaluates the assertion using its locally provisioned public-key trust.

A valid signature establishes authenticity relative to the provisioned key.

It does not independently prove that the underlying operation occurred.

---

## 5. Experimental Questions

MD001 evaluates three primary questions.

### B01 — Valid Cross-Domain Verification

Can a valid signed assertion travel from Domain A through the mechanical relay and be independently accepted by Domain B?

### N01 — Modification Detection

If a signed field is modified after signing, will Domain B reject the assertion even though the original signature remains attached?

### B02 — Producer-Unavailable Verification

Can Domain B verify the original assertion after Domain A has been physically disconnected from power?

These are separate experimental conditions.

Each has its own scored evidence directory.

---

## 6. Scored Results

| Case | Condition | Expected | Observed | Result |
|---|---|---|---|---|
| B01 | Original signed assertion | Accept | Accepted | PASS |
| N01 | Modified signed field | Reject | Rejected | PASS |
| B02 | Original assertion after producer power loss | Accept | Accepted | PASS |

**Overall scored result: 3/3 cases passed.**

The individual evidence directories preserve the observations supporting each result.

### B01 — Valid Assertion

The producer generated a valid signed assertion.

The artifact traveled through the relay and was received by Domain B.

The recorded artifact SHA-256 was:

```text
61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a
```

The artifact identity was preserved across the four designated observation points.

The verifier returned:

```text
HTTP 200
accepted = true
reason = accepted
signature_checks = 1
```

**B01: PASS**

[Review B01 evidence](evidence/B01_SCORED_20261119_223940/)

### N01 — Modified Assertion

The original B01 assertion was resubmitted.

Domain B ingress changed:

```text
event.outcome

SUCCESS -> FAILURE
```

The original signature was retained.

The modified artifact SHA-256 was:

```text
bae4f84d46d91e3b805890d8e683d9800798c4927343f4d266670824a9b21594
```

The verifier returned:

```text
HTTP 422
accepted = false
reason = invalid_signature
signature_checks = 1
```

**N01: PASS**

[Review N01 evidence](evidence/N01_SCORED_20261119_224654/)

### B02 — Producer-Unavailable Verification

The original B01 artifact was preserved outside Domain A.

The retained operator record documents shutdown initiation, physical power disconnection, and subsequent producer unavailability.

The recorded observations include:

```text
Shutdown initiation:
2026-11-19 22:52:33 EST

Producer connectivity failure observation:
2026-11-19 22:55:07 EST
```

The original assertion was resubmitted through the relay.

A fresh verifier process accepted it after performing an independent signature check.

The artifact SHA-256 remained:

```text
61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a
```

**B02: PASS**

[Review B02 evidence](evidence/B02_SCORED_20261119_225126/)

The consolidated results and associated observations are documented in [RESULTS.md](RESULTS.md).

---

## 7. Evidence Index

The primary evidence is organized under:

```text
evidence/
|
|-- B01_SCORED_20261119_223940/
|
|-- N01_SCORED_20261119_224654/
|
|-- B02_SCORED_20261119_225126/
|
`-- support/
    |
    |-- PREFLIGHT_EXPORT_20261119_213249/
    |
    |-- NEGATIVE_PREFLIGHT_20261119_221616/
    |
    `-- SUPPORT_EXPORT_20261119_231556/
```

### Primary Scored Evidence

| Directory | Contents | Retained files |
|---|---|---:|
| `B01_SCORED_20261119_223940` | Valid assertion, packet capture, artifact comparisons, verification response | 31 |
| `N01_SCORED_20261119_224654` | Modified assertion, signature rejection, packet capture, artifact comparisons | 34 |
| `B02_SCORED_20261119_225126` | Original assertion, producer shutdown observations, fresh verification, packet capture | 45 |
| **Total** | | **110** |

### Supporting Evidence

| Directory | Contents |
|---|---|
| `PREFLIGHT_EXPORT_20261119_213249` | Positive application preflight |
| `NEGATIVE_PREFLIGHT_20261119_221616` | Modified-assertion rejection preflight |
| `SUPPORT_EXPORT_20261119_231556` | Host runtime, relay, configuration, and supporting process evidence |

[Open the evidence index](evidence/)

---

## 8. Implementation

The MD001 implementation is preserved in the project directory.

```text
MD001/
|
|-- README.md
|-- RESULTS.md
|-- PROVENANCE.md
|-- ORIGINAL_HASH_REFERENCES.tsv
|-- SHA256SUMS.txt
|
|-- md001.py
|-- observe.py
|-- requirements.txt
|
|-- runtime/
|   |-- artifact.py
|   |-- hub.py
|   |-- routes.py
|   `-- wire.py
|
|-- configs/
|   |-- ingress.json
|   |-- ingress_N01.json
|   |-- relay.json
|   `-- verifier.json
|
|-- test_local.py
|-- test_observe.py
|
|-- ORIGINAL_PROJECT_LOCK.json
|-- RUNTIME_LOCK.json
|
|-- desktop/
|-- validation/
|-- support/
`-- evidence/
```

### Application

`md001.py` provides the application entry point.

### Artifact Verification

`runtime/artifact.py` implements the signed assertion format and cryptographic verification behavior.

### Mechanical Relay

The relay uses preserved MH001-derived components:

```text
runtime/hub.py
runtime/routes.py
runtime/wire.py
```

The relay forwards requests without becoming the authority responsible for signing or validating the underlying assertion.

### Observation Utility

`observe.py` processes previously reconstructed HTTP streams and compares extracted artifact bytes.

It does not independently reconstruct TCP packets.

### Source Integrity

The project includes:

```text
ORIGINAL_PROJECT_LOCK.json
RUNTIME_LOCK.json
```

These records preserve source identities used during implementation and validation.

Additional source and runtime provenance is documented in [PROVENANCE.md](PROVENANCE.md).

---

## 9. Development and Validation History

MD001 was developed through several distinct stages.

### Original Desktop Implementation

The original desktop implementation established:

- Assertion schema.
- Canonical encoding.
- Ed25519 signing and verification.
- Mechanical relay integration.
- Local simulation.
- Initial evidence conventions.

Final original desktop validation:

```text
21 PASS
0 FAIL
```

This was non-scored loopback validation.

[Review desktop implementation](desktop/MULTI_DOMAIN_001/)

### Deployment Adapter Validation

The later adapter validation recorded:

```text
12 PASS
0 FAIL
```

Synthetic HTTP stream validation recorded:

```text
6 PASS
0 FAIL
```

These were also non-scored checks.

Earlier failed attempts remain preserved.

[Review validation history](validation/)

### Runtime Compatibility Review

The frozen application originally specified:

```text
cryptography==49.0.0
```

The Linux hosts had earlier installed versions.

A separate review evaluated the exact application APIs and proposed an explicit runtime exception without modifying the frozen source.

The desktop runtime probe recorded:

```text
18 PASS
0 FAIL
```

Saved Linux runtime probes recorded 20 successful checks on each of the Dell, Raspberry Pi, and HP hosts.

[Review runtime compatibility](support/MD001_RUNTIME_REVIEW_R1/)

### Physical Preflight

The physical preflight established application transport and verification behavior before scoring.

Positive preflight:

```text
HTTP 200
accepted = true
```

Negative preflight:

```text
HTTP 422
accepted = false
reason = invalid_signature
```

These were not scored experiments.

### Physical Scoring

The three designated physical-network cases were then performed.

```text
B01 PASS
N01 PASS
B02 PASS
```

---

## 10. Trust Provisioning

Domain B verifies assertions using locally provisioned public-key material.

A supporting trust configuration is preserved under:

```text
support/MD001_TRUST_20261118_215250/
```

The configuration maps:

```text
DOMAIN_A
```

to an Ed25519 public key identified by its SHA-256 fingerprint.

The private signing key is not required by the relay or verifier.

The trust configuration is an input to verification.

It is not an execution authorization.

The disclosed laboratory signing material is not intended for operational use.

[Review trust configuration](support/MD001_TRUST_20261118_215250/)

---

## 11. Evidence Integrity

MD001 preserves original integrity records alongside a consolidated publication inventory.

### Historical Integrity Records

The historical records include original manifests, artifact comparisons, packet capture checksum references, stream identities, and public-key material identities.

The historical coverage of the 110 scored evidence files is classified as follows:

| Historical coverage classification | Files |
|---|---:|
| Direct original manifest entry | 9 |
| Explicit historical file checksum reference | 15 |
| Shared artifact-content identity | 7 |
| Shared stream-content identity | 6 |
| Public-trust content identity | 4 |
| No historical whole-file checksum located | 68 |
| Intentional manifest self-exclusion | 1 |
| **Total** | **110** |

These classifications distinguish direct historical file checksums from shared content identities.

The absence of a located historical whole-file checksum does not establish that a file was never hashed.

Complete original scored-case collection manifests were not located during publication reconciliation.

The individual classifications and their reference sources are preserved in [ORIGINAL_HASH_REFERENCES.tsv](ORIGINAL_HASH_REFERENCES.tsv).

The associated limitations are documented in [PROVENANCE.md](PROVENANCE.md).

### Publication Integrity

The consolidated publication manifest was finalized on November 25, 2026.

[SHA256SUMS.txt](SHA256SUMS.txt) provides the consolidated checksum inventory for the selected experimental evidence, implementation files, configurations, historical records, and supporting publication documentation.

| Inventory component | Files |
|---|---:|
| Preserved original publication files | 599 |
| Additional publication documents | 3 |
| **Total consolidated checksum entries** | **602** |

The three additional publication documents included in the inventory are:

- `RESULTS.md`
- `PROVENANCE.md`
- `ORIGINAL_HASH_REFERENCES.tsv`

The consolidated manifest covers all 110 retained scored evidence files.

| Scored collection | Checksum coverage |
|---|---:|
| B01 | 31/31 |
| N01 | 34/34 |
| B02 | 45/45 |
| **Total** | **110/110** |

Repository navigation READMEs and the consolidated manifest itself are outside the defined checksum scope.

All original historical manifests remain unchanged.

The consolidated manifest does not replace the original integrity records.

### Publication Verification

The final publication verification recorded:

```text
Checksum entries: 602
Verified:         602
Missing files:      0
Mismatches:         0

Result: PASS
```

This verification was performed during publication reconciliation, separately from the physical scored experiments.

No experiment was rerun and no original evidence or implementation file was modified during manifest finalization.

### Independent Checksum Verification

From the MD001 directory, a reviewer using GNU coreutils can check the listed files with:

```bash
sha256sum -c SHA256SUMS.txt
```

The expected result is successful verification of all 602 listed files.

Successful checksum verification establishes consistency with the publication inventory.

It does not independently validate the experimental conclusions, authenticate the historical collection process, or establish complete collection-time checksum coverage.

---

## 12. Independent Evidence Review

A reviewer can examine the published evidence without deploying the application.

Recommended sequence:

1. Review [RESULTS.md](RESULTS.md) for the consolidated scored observations.
2. Review [PROVENANCE.md](PROVENANCE.md) for source identities, collection conditions, and limitations.
3. Verify the selected publication files against [SHA256SUMS.txt](SHA256SUMS.txt).
4. Review [ORIGINAL_HASH_REFERENCES.tsv](ORIGINAL_HASH_REFERENCES.tsv) for historical checksum coverage.
5. Review the original B01 artifact and accepted decision.
6. Compare the B01 artifact at the recorded observation points.
7. Review the N01 mutation and retained original signature.
8. Confirm the N01 invalid-signature rejection.
9. Review the B02 producer shutdown and connectivity observations.
10. Confirm B02 reused the original B01 artifact.
11. Confirm the B02 verification result and fresh signature check.
12. Review the supporting preflight and runtime evidence.
13. Compare the recorded source and configuration identities.

The individual evidence directories provide additional details.

The recorded packet captures and extracted artifacts are preserved for independent examination.

---

## 13. What MD001 Demonstrates

Within the recorded laboratory configuration, MD001 demonstrates three properties.

### Independent Verification

Domain B accepted a valid assertion signed by Domain A using locally provisioned public-key trust.

### Modification Detection

Domain B rejected an assertion whose signed content was modified without replacing the original signature.

### Producer Independence

Domain B accepted the previously issued valid assertion after Domain A was physically disconnected from power.

These observations support separation between assertion production, mechanical transport, and subsequent verification.

---

## 14. What MD001 Does Not Demonstrate

MD001 does not establish:

- Authorization to perform the original operation.
- Truth of the underlying asserted event independently of the producer.
- Prevention of repeated verification.
- Prevention of repeated execution.
- Durable single-use authority consumption.
- Resistance to producer signing-key compromise.
- General resistance to compromised provider hosts.
- Transport confidentiality.
- Physical actuation enforcement.
- Production deployment readiness.

The experiment deliberately does not introduce an artifact-consumption ledger.

A valid assertion can be verified more than once.

That is consistent with the stateless verification design.

Verification of an assertion must not be confused with authorization to execute an operation.

---

## 15. Relationship to MDSV

MD001 evaluates a specific implementation of Multi-Domain Stateless Verification.

The experiment examines whether verification material can cross a domain boundary while preserving separation between:

- The originating domain.
- The transport intermediary.
- The receiving verifier.
- The underlying authorization and execution systems.

The intermediary does not become the source of authority.

The receiving domain does not need to reproduce the originating domain's operational state.

The experiment supports the narrower proposition that a signed assertion can be independently verified under the tested conditions.

It does not establish every possible implementation or application of the broader MDSV architecture.

---

## 16. Evidence Preservation

The scored experiment directories are historical evidence records.

Original artifacts, packet captures, process records, verification responses, and integrity records should remain unchanged.

Additional testing should use separately identified evidence directories.

Documentation added after the experiments should not be represented as contemporaneous scored evidence.

The project preserves unsuccessful local validation attempts alongside successful results.

Publication reconciliation preserves the distinction between original evidence, historical integrity references, and subsequently generated publication checksums.

This maintains the distinction between implementation development, preflight, scored observations, and publication documentation.

---

## 17. Conclusion

MD001 completed three physical-network scored experiments.

```text
B01 — PASS
N01 — PASS
B02 — PASS
```

The experiments demonstrated that:

1. A valid signed assertion could be transported and independently verified across the designated laboratory path.
2. Modification of signed assertion content caused verification rejection.
3. A previously issued valid assertion remained independently verifiable after the originating producer was physically disconnected.

The mechanical intermediary transported the assertion without possessing the producer's signing authority.

The receiving domain performed its own verification using locally provisioned trust.

**MD001 demonstrates bounded cross-domain assertion verification without requiring shared authorization state or continued producer availability during subsequent verification.**
