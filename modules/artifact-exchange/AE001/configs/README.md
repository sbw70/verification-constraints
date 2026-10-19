# AE001 Configuration

This directory contains the AE001 campaign definition, source identities, execution manifest, and scored-run lock.

```text
configs/
├── AE001_CONTRACT.md
├── AE001_CONTRACT_DRAFT.md
├── AE001_LOCK_SHA256SUMS.txt
├── AE001_RUN_MANIFEST.json
└── AE001_SOURCE_MANIFEST.json
```

The configuration files distinguish the original campaign proposal from the definition that was actually locked and executed.

## `AE001_CONTRACT_DRAFT.md`

This is the pre-execution draft of the AE001 campaign.

It records the intended property, proposed topology, four-case matrix, expected outcomes, evidence requirements, and initial scope before the live environment had been fully established.

The draft explicitly identifies itself as unfrozen.

It is preserved as planning provenance.

It is not the scored contract.

The draft also records several constraints that remained part of the final campaign design, including:

- reuse of the existing MP003 provider protocol;
- no replacement of provider authorization semantics;
- Provider B as the target provider;
- Provider A `auth_missing` events as background evidence;
- preservation of original and altered artifacts;
- no inference of authorization from relay HTTP `204`;
- distinct PASS, FAIL, and INCOMPLETE outcomes; and
- retention of preflight misfires.

## `AE001_CONTRACT.md`

This is revision 1 of the final AE001 campaign contract.

It was locked before scored execution.

The contract defines the tested property:

> request-bound provider-issued verification material traverses an intermediary without making the intermediary the evaluator or execution authority.

Within the tested architecture:

- the target provider evaluates the authorization material;
- the target provider controls software execution;
- the target provider generates authenticated execution-boundary signals; and
- the association recorder may preserve those signals without acquiring execution authority.

The contract also fixes the topology, implementation relationship, binding model, four-case sequence, evidence requirements, PASS/FAIL/INCOMPLETE criteria, and scope limits.

## Final Topology

The locked topology was:

| Role | Host | Address / Port |
|---|---|---|
| Requester / scoring | Xer0trust, Windows | `192.168.1.102` |
| Relay | nuvl-relay, Raspberry Pi | `192.168.1.100:18080` |
| Association recorder | nuvl-relay, Raspberry Pi | `192.168.1.100:19191` |
| Provider A | Xer0trust-3, Linux | `192.168.1.118:19090` |
| Provider B | Xer0trust2, Linux | `192.168.1.107:19090` |

The relay and association recorder shared a host but ran as separate processes.

No stronger host-isolation claim is made.

## Four-Case Matrix

The locked campaign executed exactly four cases, in order:

| Case | Issuer | Target | Expected Provider B result |
|---|---|---|---|
| B01 | Provider B | Provider B | `START`, one software execution, `COMPLETE` |
| N01 | Provider B | Provider B | `DENY auth_bad_sig`, no execution/state consumption |
| N02 | Provider A | Provider B | `DENY auth_provider_mismatch`, no execution/state consumption |
| B02 | Provider B | Provider B | `START`, one software execution, `COMPLETE` |

The contract also required one authenticated Provider A `DENY auth_missing` event for each case because no Provider A authorization header was supplied.

Those Provider A events are background path evidence, not additional AE001 cases.

## Existing Binding Model

AE001 reused the existing MP003 binding scheme.

The contract defines:

```text
request_repr = SHA256(exact request bytes)
```

```text
binding = SHA256(
    UTF8("NUVL_BIND_V1|" + request_repr + "|" + context)
)
```

```text
operation_id = SHA256(
    UTF8("NUVL-MP-OP-v1|" + binding)
)
```

The campaign did not introduce a new request-binding mechanism.

## `AE001_SOURCE_MANIFEST.json`

The source manifest identifies the preserved implementation snapshot inspected for AE001.

It records:

- source paths;
- SHA-256 identities;
- corresponding published Git blob identities where available; and
- the inspected repository commit.

The inspected repository commit is:

```text
292c1c38b08b007592aab8fc14a97755367143e5
```

The source snapshot includes:

- MP003 relay;
- MP003 association recorder;
- provider registry;
- provider public trust keys;
- Provider A runtime, mint, and laboratory keys;
- Provider B runtime, mint, and laboratory keys; and
- the architectural `AEBS.py` reference.

The source manifest is an identity record.

It is not the scored result.

## `AE001_RUN_MANIFEST.json`

The run manifest pins the actual revision-1 execution configuration.

It records:

- campaign name and revision;
- host mapping;
- ports;
- association-recorder URL;
- source repository revision;
- source and campaign-script SHA-256 values;
- the four-case expectations;
- expected provider submission count;
- runtime dependency versions;
- source-manifest identity;
- contract identity; and
- lock status.

Its status is:

```text
LOCKED_BEFORE_SCORED
```

## Pinned Runtime Versions

The manifest records:

| Role | Python | `cryptography` |
|---|---:|---:|
| Requester / scoring | 3.12.14 | 50.0.2 |
| Providers | 3.12.3 | 41.0.7 |
| Relay / association host | 3.13.5 | 43.0.0 |

These are the versions recorded for the executed AE001 environment.

They are provenance data, not a claim that AE001 requires only those versions.

## Expected Submission Count

The locked manifest requires:

```text
expected_submissions = 10
```

That count consists of:

- four Provider A `DENY auth_missing` submissions;
- two Provider B events for B01;
- one Provider B event for N01;
- one Provider B event for N02; and
- two Provider B events for B02.

The association session also records session boundary records separately.

## `AE001_LOCK_SHA256SUMS.txt`

This file freezes the scored definition by recording SHA-256 values for:

```text
AE001_CONTRACT.md
AE001_RUN_MANIFEST.json
AE001_SOURCE_MANIFEST.json
```

The locked identities are:

```text
36ec6e78c979a2cbbf420d42139698aebf598525fc28110f04b2f8724f5ff4a1  AE001_CONTRACT.md
25983fd30859537ebc5d9a870cf50bd64a4a1350f37ea83854627628ef5b80f3  AE001_RUN_MANIFEST.json
932afc0413be685d728a61b06d945f95ca14b7c9609b0e3b5e5f8fb26ac0e739  AE001_SOURCE_MANIFEST.json
```

For scored execution, `scripts/run_ae001.py` verifies these locked identities before proceeding.

A mismatch stops the scored campaign instead of silently executing a changed definition.

## Locking Boundary

The lock covers the contract, run manifest, and source manifest.

The run manifest in turn pins the campaign scripts and tested source files by SHA-256.

This creates a traceable relationship between:

- the claim under test;
- the expected outcomes;
- the source implementation;
- the orchestration scripts; and
- the scored evidence.

It does not constitute an external timestamp or third-party signature.

## Draft vs. Final

The draft and final contract are both retained intentionally.

The draft shows what was proposed before live setup was fully resolved.

The final contract shows what was actually frozen before scoring.

Differences between planning and execution are therefore visible rather than being rewritten out of the record.

The scored evidence uses the final contract and locked run manifest.

## Relationship to Evidence

Each completed run preserves its own copies of the contract and run manifest inside the evidence directory.

The scored copies are under:

`../evidence/scored/AE001_SCORED_20261018_R1/`

The campaign harness records the identities of those inputs in:

`input_identity.json`

This allows the scored output to be tied back to the locked campaign definition.

## Scope

These files define and identify the AE001 campaign.

They do not independently prove the tested property.

The scored result depends on:

- the locked configuration;
- preserved source;
- actual campaign execution;
- provider-generated signed boundary packages;
- provider state;
- execution evidence;
- relay delivery evidence; and
- the final scorecard.

The campaign-level result is summarized in:

`../RESULTS.md`

Execution and source provenance are documented in:

`../PROVENANCE.md`
