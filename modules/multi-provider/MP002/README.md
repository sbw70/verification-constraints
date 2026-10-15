# MP002 — Multi-Provider Policy Divergence

MP002 extends the physically distributed multi-provider baseline established in MP001.

The test asks a narrower question:

**Can two independently controlled providers receive the same distributed operation with valid provider-specific authorization and still make different execution decisions without another provider or shared component overriding either one?**

The scored result was:

**PASS**

Provider A permitted and executed.

Provider B denied under Provider B's own local policy.

The relay did not override Provider B.

Provider A did not override Provider B.

The association did not convert Provider B's denial into approval.

Provider-local judgment remained provider-local.

---

## Architecture

The tested path was:

    Requester
        |
        v
    NUVL relay
       / \
      v   v
     A     B
      \   /
       v v
    Association

The roles remain deliberately separated.

### Provider A

Provider A controls:

- Provider A authorization issuance;
- Provider A authorization validation;
- Provider A spent state;
- Provider A execution;
- Provider A boundary evidence.

### Provider B

Provider B independently controls:

- Provider B authorization issuance;
- Provider B authorization validation;
- Provider B local policy;
- Provider B spent state;
- Provider B execution;
- Provider B boundary evidence.

### NUVL relay

The relay transports the request and provider-specific authorization material.

It does not originate or enlarge provider authority.

It does not decide whether Provider A or Provider B may execute.

### Association

The association verifies and preserves signed provider boundary evidence.

It does not authorize execution.

It does not override provider decisions.

It does not create a distributed transaction result on behalf of the providers.

---

## Relationship to MP001

MP001 established the physically distributed multi-provider baseline.

It demonstrated that the roles could be split across independent hosts while retaining provider-specific authorization and execution state.

MP002 keeps that baseline and changes one substantive behavior:

**Provider B gains a deterministic provider-local policy gate.**

The tested policy denies when the verified context is:

`CTX_MP002_DIVERGE`

The Provider B policy check occurs before authorization consumption.

This makes it possible to test whether Provider B can independently refuse execution even when:

- the request is valid;
- the Provider B authorization is valid;
- Provider A independently approves the same distributed operation.

The exact MP001-to-MP002 Provider B source difference is published in:

`provider_b/MP001_TO_MP002_PROVIDER_B.diff`

---

## Scored campaign

Scored session:

`MP002_SCORED_20261013`

The scored campaign contained two cases.

### B01_CONTROL

Both providers received the same request under:

`CTX_ALPHA`

Both received valid provider-specific authorization.

Observed result:

    Provider A: START -> EXECUTED -> COMPLETE
    Provider B: START -> EXECUTED -> COMPLETE

Result:

**PASS**

This establishes the normal control path for MP002.

### D01_POLICY_DIVERGENCE

Both providers received the same request under:

`CTX_MP002_DIVERGE`

Both received valid provider-specific authorization.

Provider A permitted the request.

Observed result:

    Provider A: START -> EXECUTED -> COMPLETE

Provider B applied its local policy.

Observed result:

    Provider B: DENY policy_denied

Provider B did not:

- consume the D01 authorization;
- emit `START`;
- execute;
- emit `COMPLETE`.

Result:

**PASS**

---

## Final scored state

After B01 and D01:

### Provider A

    executions = 2
    spent authorizations = 2

Provider A executed:

- B01
- D01

### Provider B

    executions = 1
    spent authorizations = 1

Provider B executed:

- B01

Provider B did not execute D01.

For the D01 authorization:

    D01_PROVIDER_A_AUTHORIZATION_CONSUMED=True
    D01_PROVIDER_B_AUTHORIZATION_CONSUMED=False

The counts reconcile with the two scored cases.

---

## What D01 demonstrates

D01 demonstrates independent provider-local judgment.

Both providers participated in the same distributed operation.

Both possessed valid provider-specific authorization.

They reached different decisions.

Provider A's decision remained authoritative only for Provider A.

Provider B's decision remained authoritative only for Provider B.

No shared component became the authority over both.

That is the property MP002 was designed to test.

---

## Provider B policy scope

The Provider B policy used in MP002 is deliberately simple.

It is a deterministic test condition:

`CTX_MP002_DIVERGE`

This test does not attempt to demonstrate:

- sophisticated policy evaluation;
- dynamic risk scoring;
- adaptive authorization;
- production policy-engine behavior.

The claim is narrower:

**when Provider B makes a local deny decision, nothing else in the tested path overrides that decision and causes Provider B to execute.**

---

## Authorization remains provider-scoped

Provider A and Provider B use separate provider-specific authorization.

Provider A's authorization does not become Provider B authority.

Provider B's authorization does not become Provider A authority.

The relay transports authorization but does not gain equivalent authority merely by carrying it.

The association verifies provider-produced evidence but does not become the source of provider authority.

The tested authority boundary remains:

    Provider-issued authority
            |
            v
    provider validation
            |
            v
    provider-local decision
            |
            v
    provider-local consequence

Shared infrastructure may transport or verify information associated with that authority.

It does not originate or enlarge it.

---

## Unconsumed Provider B authorization

Provider B's D01 policy denial occurs before durable authorization consumption.

As a result, the valid Provider B D01 authorization remained unspent at the end of the scored campaign.

That behavior is intentional in the tested implementation:

    valid authorization
            |
            v
    local policy check
            |
            +--> DENY -> authorization remains unconsumed
            |
            v
    durable consume
            |
            v
    START
            |
            v
    execution
            |
            v
    COMPLETE

MP002 did not subsequently change Provider B's policy and present the same authorization again.

No claim is therefore made about later:

- acceptance;
- expiration;
- revocation;
- restart behavior;
- subsequent reuse.

---

## Association evidence

The association recorder received and verified signed provider boundary events.

For B01 it recorded valid:

- Provider A `START`
- Provider B `START`
- Provider A `COMPLETE`
- Provider B `COMPLETE`

For D01 it recorded valid:

- Provider B `DENY policy_denied`
- Provider A `START`
- Provider A `COMPLETE`

All scored provider submissions passed signature verification.

The association does not calculate an authoritative cross-provider result such as:

- `1/2`;
- `2/2`;
- quorum;
- distributed commit;
- overall authorization.

It records and verifies what the independent providers reported.

Higher-level interpretation of those records remains separate from provider execution authority.

---

## Cross-provider atomicity

MP002 does not provide cross-provider atomic execution.

In D01:

- Provider A executed.
- Provider B denied.

Provider A does not wait for Provider B.

Provider B does not wait for Provider A.

That is consistent with the architecture under test.

MP002 therefore demonstrates:

**independent provider judgment**

not:

**all-or-nothing distributed execution**

A system requiring every necessary provider to approve before any consequence occurs would require a separate composition, quorum, or pre-execution gating mechanism.

That behavior is outside MP002.

---

## Evidence

The publication separates pre-scored validation from scored evidence.

### `evidence/smoke/`

Contains the retained smoke-test material used to validate the deployment before scoring.

Smoke evidence is preserved for provenance and troubleshooting.

It is not substituted for the scored campaign.

### `evidence/scored/`

Contains the scored MP002 evidence, including:

- locked contract;
- locked run manifest;
- exact B01 request and authorization artifacts;
- exact D01 request and authorization artifacts;
- association log;
- final Provider A state;
- final Provider B state;
- deployed implementation hashes;
- scorecard;
- SHA-256 integrity manifest.

The staged scored evidence was verified byte-for-byte against the source scored directory before publication staging.

All entries in the scored `SHA256SUMS.txt` verified.

---

## Integrity

Final association record hash:

`7002cd90fcf586dd145c6156ca3ed5da18f267138796099f536c4df53798013a`

SHA-256 of the scored `association.jsonl`:

`d3025b6b55331dfe4505f0a1ddc82fdb1776f5dcc30449b77f683b7ed258d9e8`

Locked contract SHA-256:

`e795f55172ea27d8ee434679ab9ea4a1b07e1154a708dfd5ad846fdd0f4ab18d`

Locked run-manifest SHA-256:

`3f4b317e3c3fc8f34e579941ec79f0f0191fcef122be320973a88b84e5750845`

Detailed implementation hashes are preserved in:

`evidence/scored/deployed_implementation_hashes.txt`

---

## Repository layout

    MP002/
    ├── README.md
    ├── RESULTS.md
    ├── PROVENANCE.md
    ├── configs/
    ├── intermediary/
    ├── provider_a/
    ├── provider_b/
    ├── association/
    └── evidence/
        ├── smoke/
        └── scored/

### `configs/`

Locked contract and run manifest.

### `intermediary/`

NUVL multi-provider relay.

### `provider_a/`

Provider A runtime, mint utility, and laboratory keys.

### `provider_b/`

Provider B runtime, mint utility, laboratory keys, and the MP001-to-MP002 runtime diff.

### `association/`

Association recorder, provider registry, and public trust anchors.

### `evidence/`

Smoke and scored evidence.

---

## Laboratory keys

The provider directories include the private and public keys used for these laboratory tests.

The private keys are intentionally published so the test implementation can be inspected and reproduced.

They are laboratory-only credentials.

They are not production keys.

Publishing them after the test does not change which components exercised authority during the scored campaign.

---

## What MP002 establishes

Within the tested implementation, MP002 demonstrates that:

1. Two independently controlled providers can participate in the same distributed operation.
2. Each provider can receive its own valid provider-specific authorization.
3. Each provider can retain its own execution judgment.
4. Provider A can approve while Provider B denies.
5. Provider A's approval does not cause Provider B to execute.
6. Provider B's denial does not become authority over Provider A.
7. The relay can transport both paths without becoming provider authority.
8. The association can verify divergent provider evidence without becoming execution authority.
9. Provider B can deny before authorization consumption, leaving the valid authorization unspent.

---

## What MP002 does not establish

MP002 does not establish:

- cross-provider atomicity;
- quorum-gated execution;
- all-provider approval before consequence;
- globally synchronized chronology across hosts;
- implementation diversity between providers;
- later behavior of Provider B's unconsumed D01 authorization;
- compromised-provider containment;
- independent association re-verification as part of the scored run;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- physical actuation;
- independent hardware-witness evidence.

Those properties require separate tests.

---

## Result summary

MP001 demonstrated physically separate provider authority domains.

MP002 adds a stronger condition:

**the providers disagree.**

Both received the same distributed operation.

Both had valid provider-specific authorization.

Provider A executed.

Provider B denied.

Neither provider's judgment became authority over the other.

The relay remained transport.

The association remained evidence.

Provider authority remained provider-scoped.

That is the MP002 result.
