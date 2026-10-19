# AE001 — Provider-Controlled Artifact Exchange

AE001 tests whether request-bound, provider-issued verification material can traverse an intermediary without transferring authorization authority to that intermediary.

Scored run:

**AE001_SCORED_20261018_R1 — PASS**

The tested result is bounded:

> the intermediary transported the request and provider authorization material, while the target provider retained control over authorization evaluation, software execution, authorization consumption, and authenticated execution-boundary signaling.

AE001 does not claim that transport is authority.

## Property Under Test

A requester submits an operation request together with provider-issued verification material.

The intermediary may:

- receive the request;
- derive the existing request representation and binding;
- carry provider-specific artifact bytes;
- forward the request to providers; and
- record transport evidence.

The intermediary does not thereby gain authority to:

- issue provider authorization;
- determine that a provider should execute;
- consume provider authorization state;
- substitute one provider's authority for another's; or
- generate provider-authenticated execution boundaries.

The target provider independently evaluates the presented material.

If the provider accepts it, the provider initiates its own software execution and generates authenticated boundary signals.

If the provider rejects it, transport alone does not create authority.

## Result

The locked four-case scored campaign passed every defined criterion.

| Case | Material presented to Provider B | Provider B result | Outcome |
|---|---|---|---|
| B01 | Valid fresh Provider B authorization bound to the request | `START` → one software execution → `COMPLETE` | PASS |
| N01 | Valid Provider B authorization with one signature byte altered | `DENY auth_bad_sig`; no execution or state consumption | PASS |
| N02 | Valid fresh Provider A authorization presented to Provider B | `DENY auth_provider_mismatch`; no execution or state consumption | PASS |
| B02 | Fresh valid Provider B authorization after both negative cases | `START` → one software execution → `COMPLETE` | PASS |

Final scored state:

```text
Provider A:
  executions: 0
  spent authorizations: 0

Provider B:
  executions: 2
  spent authorizations: 2
```

Only B01 and B02 produced Provider B software execution.

N01 and N02 left Provider B execution and spent-authority state unchanged.

## Why N02 Matters

N02 tested provider scope directly.

A legitimate Provider A authorization artifact was placed in the Provider B transport header.

The intermediary transported it.

Provider B rejected it with authenticated:

```text
DENY auth_provider_mismatch
```

The artifact was valid Provider A-issued material.

It was not Provider B authority.

Transport did not enlarge it.

## Why N01 Matters

N01 tested whether the intermediary needed to become the authorization evaluator in order for invalid material to be stopped.

It did not.

The relay transported the altered artifact.

Provider B independently evaluated the artifact and returned authenticated:

```text
DENY auth_bad_sig
```

No execution occurred and no Provider B authority was consumed.

## Positive Bookends

B01 established that valid Provider B authority worked before the negative cases.

B02 established that fresh valid Provider B authority still worked afterward.

This prevents a passing negative test from being explained merely by a broken provider or unusable path.

## Architecture

The tested topology was:

```text
Requester / Scoring
Xer0trust — Windows
192.168.1.102
        |
        v
Relay
nuvl-relay — Raspberry Pi
192.168.1.100:18080
        |
        +----------------------+
        |                      |
        v                      v
Provider A                 Provider B
Xer0trust-3                Xer0trust2
Linux                      Linux
192.168.1.118:19090        192.168.1.107:19090
        |                      |
        +----------+-----------+
                   |
                   v
        Association Recorder
        separate process
        192.168.1.100:19191
```

The relay and association recorder ran as separate processes on the same Raspberry Pi host.

No stronger host-isolation claim is made.

## Authority Roles

### Requester

The requester constructs the operation request and transports already-issued authorization material.

Possession or transport of that material is not itself provider execution authority.

### Relay

The relay performs request derivation and transport.

It does not decide provider admission.

Relay HTTP `204` is a transport result only.

It is not treated as evidence that provider execution occurred.

### Provider A

Provider A remains an independent provider authority.

No Provider A authorization header was supplied in the four normal campaign requests, so Provider A produced authenticated background:

```text
DENY auth_missing
```

events.

Provider A also issued the legitimate artifact used for the N02 wrong-provider case.

### Provider B

Provider B was the target provider under test.

It independently evaluated the material presented to it and controlled:

- provider-identity checks;
- authorization-ID checks;
- issuance-signature verification;
- request and context matching;
- spent-state checks;
- authorization consumption;
- software execution; and
- authenticated boundary signaling.

### Association Recorder

The association recorder receives and preserves provider-generated boundary packages.

It does not authorize provider execution.

The scored harness independently verified the raw provider signatures instead of relying on the recorder's own verification fields as the signature oracle.

## Binding Model

AE001 reused the existing MP003 binding mechanism.

No new binding scheme was introduced.

The request representation is:

```text
request_repr = SHA256(exact request bytes)
```

The binding is:

```text
binding = SHA256(
    UTF8("NUVL_BIND_V1|" + request_repr + "|" + context)
)
```

The operation identity is:

```text
operation_id = SHA256(
    UTF8("NUVL-MP-OP-v1|" + binding)
)
```

Authorization artifacts and boundary evidence are correlated to those identities.

## Provider Keys

Each provider has two distinct Ed25519 key roles.

### Authorization issuance keys

These sign provider-issued authorization artifacts.

The corresponding public key is used by that provider to verify incoming authority.

### Boundary-signing keys

These sign provider-generated:

```text
START
COMPLETE
DENY
```

packages.

The two key roles are separate.

Provider A and Provider B also use separate provider-specific key material.

The laboratory private keys are intentionally published with the test package for reproducibility.

They are not production credentials.

Because those laboratory private keys are public, AE001 does not claim post-publication historical authenticity against a party possessing them.

## Scored Boundary Evidence

The scored run produced ten authenticated provider submissions:

```text
Provider A:
  4 × DENY auth_missing

Provider B:
  B01 → START, COMPLETE
  N01 → DENY auth_bad_sig
  N02 → DENY auth_provider_mismatch
  B02 → START, COMPLETE
```

The association session also contains its own session boundary records.

## Independent Signature Verification

The scored harness independently verifies each raw provider package by:

1. selecting the provider-specific public boundary key;
2. verifying the Ed25519 signature;
3. obtaining the raw 32-byte public key;
4. computing its SHA-256 key identifier;
5. comparing that value with the package key ID; and
6. checking the request binding.

Provider-generated evidence is therefore checked independently of the association recorder's interpretation.

## State Evidence

Each case preserves Provider A and Provider B state before and after execution.

For negative cases, Provider B state and execution evidence were required to remain byte-identical.

For positive cases, the harness required exactly:

- one new spent authorization; and
- one new software execution record.

The final Provider B count was therefore two executions and two spent authorizations.

Provider A remained unchanged throughout.

## Canonical MP003 Noninterference

AE001 used isolated campaign runtime directories.

The relevant existing MP003 state files were hashed before and after the campaign.

Their hashes matched.

The scored campaign therefore did not use canonical MP003 state as writable AE001 state.

## Preflight History

AE001 preserves its preflight history rather than rewriting it away.

### R1

`AE001_PREFLIGHT_20261018_R1`

Status:

**INCOMPLETE**

The first preflight stopped before deployment because an encoded SSH source-transfer command exceeded the Windows command-line length limit.

No AE001 case executed.

This is retained as a harness/setup failure, not reported as a failure of the tested property.

### R2

`AE001_PREFLIGHT_20261018_R2`

Status:

**PASS**

Source transfer was changed to SSH standard input and all four preflight cases completed successfully.

After R2, one scoring-logic edge case was corrected before the scored freeze so authenticated unexpected admission in a rejection case is classified as `FAIL` even when excess boundary events are also present.

The provider implementations, relay behavior, protocol, four-case matrix, and expected outcomes did not change.

Earlier harness versions are retained under:

`evidence/retained/`

## Repository Layout

```text
AE001/
├── README.md
├── RESULTS.md
├── PROVENANCE.md
├── SHA256SUMS.txt
├── configs/
│   ├── README.md
│   ├── AE001_CONTRACT.md
│   ├── AE001_CONTRACT_DRAFT.md
│   ├── AE001_LOCK_SHA256SUMS.txt
│   ├── AE001_RUN_MANIFEST.json
│   └── AE001_SOURCE_MANIFEST.json
├── evidence/
│   ├── README.md
│   ├── preflight/
│   ├── retained/
│   └── scored/
├── scripts/
│   ├── README.md
│   ├── launch_role.py
│   └── run_ae001.py
└── source/
    ├── README.md
    ├── MP003/
    │   ├── association/
    │   ├── intermediary/
    │   ├── provider_a/
    │   └── provider_b/
    └── reference/
        └── AEBS.py
```

## Configuration Lock

The scored definition was frozen before execution.

`configs/AE001_LOCK_SHA256SUMS.txt` locks:

- `AE001_CONTRACT.md`;
- `AE001_RUN_MANIFEST.json`; and
- `AE001_SOURCE_MANIFEST.json`.

The run manifest additionally pins the campaign scripts and tested source files by SHA-256.

For scored execution, the campaign harness checks those identities before running.

A mismatch stops the campaign.

## Source Relationship

AE001 has two source categories.

### Architectural reference

`source/reference/AEBS.py`

This is the compact architectural reference for provider-controlled artifact exchange and boundary signaling.

It illustrates the intended separation but is not the complete scored implementation.

### Tested implementation

`source/MP003/`

AE001 reused the established MP003 implementation for:

- provider-specific authorization;
- request binding;
- provider evaluation;
- spent state;
- software execution;
- authenticated boundary signaling; and
- evidence recording.

The scored result depends on this actual implementation and the published evidence, not on `AEBS.py` alone.

## Evidence

Scored evidence is under:

`evidence/scored/AE001_SCORED_20261018_R1/`

It includes:

- locked contract copy;
- locked run-manifest copy;
- input identities;
- deployment identities;
- exact request material;
- original and transmitted authorization artifacts;
- issuer output;
- relay delivery records;
- raw provider-signed boundary packages;
- association records;
- provider before/after state;
- provider before/after execution records;
- final runtime logs and state;
- canonical-state bookends;
- scorecard; and
- per-run SHA-256 checksums.

`RESULTS.md` gives the concise campaign result.

`PROVENANCE.md` records implementation identity, topology, execution environment, evidence lineage, and reproduction information.

## Reproduction

A fresh preflight can be run from the AE001 root with:

```bash
python scripts/run_ae001.py \
  --root . \
  --identity PATH_TO_SSH_PRIVATE_KEY \
  --known-hosts PATH_TO_KNOWN_HOSTS \
  --phase preflight \
  --run-id AE001_PREFLIGHT_FRESH1
```

The SSH identity and `known_hosts` file are external operator access material and are not included in the publication.

A scored run should use:

```text
--phase scored
```

with a fresh run ID after the intended configuration has been frozen.

Existing run directories and consumed authority should not be reused.

## What AE001 Establishes

Within the tested four-case software configuration, AE001 provides evidence that:

- provider-issued authorization material can traverse an intermediary;
- intermediary transport does not itself become provider authorization;
- altered Provider B material is rejected by Provider B;
- valid Provider A authority does not become Provider B authority;
- rejected material does not consume Provider B state or produce Provider B software execution;
- valid Provider B authority works both before and after the negative cases;
- provider execution remains provider-controlled; and
- provider boundary signals can be recorded downstream without granting that recorder execution authority.

## What AE001 Does Not Establish

AE001 does not test or claim:

- physical actuation or mechanical consequence;
- arbitrary provider-host compromise resistance;
- arbitrary relay-host compromise resistance;
- private-key compromise resistance;
- transport confidentiality;
- denial-of-service resistance;
- crash recovery;
- reboot behavior;
- power-loss behavior;
- concurrent-use behavior;
- delayed delivery;
- offline delivery;
- quorum behavior;
- implementation diversity;
- global chronology;
- association-chain integrity;
- secure external timestamping; or
- rejection of every possible malformed input.

AE001 is a bounded software artifact-exchange campaign.

The result should not be generalized beyond the evidence actually produced.
