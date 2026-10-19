# AE001 Scored Run — AE001_SCORED_20261018_R1

This directory contains the complete evidence package for the locked AE001 scored run.

Run ID: **AE001_SCORED_20261018_R1**  
Phase: **scored**  
Overall result: **PASS**

The run tested whether request-bound provider-issued verification material could traverse an intermediary while leaving artifact evaluation, execution authority, and authenticated execution-boundary signaling under provider control.

## Scored Cases

| Case | Presented material | Provider B outcome | Result |
|---|---|---|---|
| B01 | Valid fresh Provider B authorization bound to the request | START → one software execution → COMPLETE | PASS |
| N01 | Provider B authorization with one signature byte altered | DENY `auth_bad_sig`; no execution or state consumption | PASS |
| N02 | Valid Provider A authorization presented to Provider B | DENY `auth_provider_mismatch`; no execution or state consumption | PASS |
| B02 | Fresh valid Provider B authorization after both negative cases | START → one software execution → COMPLETE | PASS |

Provider A also produced one authenticated `DENY` in each case because no Provider A authorization header was supplied. Those four denials are background path evidence, not additional scored cases.

The scorecard records ten authenticated provider submissions across the session: four Provider A denials and six Provider B boundary events.

## Directory Structure

```text
AE001_SCORED_20261018_R1/
├── AE001_CONTRACT.md
├── AE001_RUN_MANIFEST.json
├── SCORECARD.json
├── SHA256SUMS.txt
├── input_identity.json
├── canonical_state_before.json
├── canonical_state_after.json
├── provider_a_deployment.json
├── provider_b_deployment.json
├── relay_deployment.json
├── B01/
├── N01/
├── N02/
├── B02/
└── final/
```

## Case Evidence

Each case directory preserves the material needed to reconstruct and inspect that case, including:

- exact request representation;
- original and transmitted authorization material;
- issuer output;
- relay delivery evidence;
- raw provider-generated boundary packages;
- association-recorder output;
- provider execution snapshots;
- provider state snapshots; and
- state-presence and hash metadata.

The case directories are evidence records. `SCORECARD.json` summarizes the scored interpretation of those records.

## Provider-Signed Boundary Evidence

The scored harness independently verified provider-specific signatures on the raw boundary packages.

For the positive cases, Provider B produced authenticated:

- `START`
- `COMPLETE`

For the negative cases, Provider B produced authenticated:

- `DENY auth_bad_sig` for N01
- `DENY auth_provider_mismatch` for N02

The association recorder preserved provider submissions but did not supply authorization authority and was not used as the independent signature-verification oracle.

## Execution and State Result

Provider B executed exactly twice during the campaign:

- once for B01;
- once for B02.

Provider A executed zero times.

The final expected state was therefore:

- Provider A: zero spent authorizations, zero executions;
- Provider B: two spent authorizations, two executions.

The N01 and N02 negative cases left Provider B execution and spent-authority state unchanged.

## Relay Role

The relay transported the request and provider-specific authorization header values.

It mechanically derived the request representation and binding used by the existing MP003 protocol, but did not:

- decode provider authorization semantics;
- determine whether execution was authorized;
- generate provider boundary packages; or
- receive provider authority.

Relay HTTP `204` responses are transport results only and are not treated as evidence that execution occurred.

Execution is established through provider-generated evidence and provider state.

## Canonical State Bookends

`canonical_state_before.json` and `canonical_state_after.json` are byte-identical for the canonical MP003 state checked by the campaign.

AE001 used isolated run directories rather than modifying the canonical MP003 runtime state.

## Deployment Records

The three deployment records identify the exact code and runtime environment used for:

- Provider A;
- Provider B; and
- the relay/association host.

The locked source and campaign identities are defined by the run manifest and the campaign-level source manifest.

## Final Evidence

The `final/` directory contains end-of-run records from the deployed roles, including:

- Provider A console and final spent state;
- Provider B console, final execution log, and final spent state;
- relay console and delivery log; and
- association-recorder console and complete association log.

These files preserve the final runtime state of the scored session.

## Integrity

`SHA256SUMS.txt` records SHA-256 hashes for the scored evidence package using paths relative to this run directory.

The checksum list provides byte-integrity verification of the published files. It is not an external signature or independent timestamp.

## What This Run Establishes

Within the tested four-case software configuration, the evidence shows that:

- request-bound provider-issued authorization material traversed the intermediary;
- the intermediary did not become the authorization evaluator;
- Provider B independently accepted valid Provider B material;
- Provider B rejected altered material;
- Provider B rejected authorization issued for Provider A;
- rejected material did not consume Provider B state or produce software execution;
- valid authority still worked after both negative cases; and
- authenticated execution-boundary signals were generated by the provider.

## Limits

AE001_SCORED_20261018_R1 does not establish:

- physical actuation or mechanical consequence;
- resistance to arbitrary provider-host compromise;
- resistance to relay-host compromise;
- key-compromise resistance;
- transport confidentiality;
- crash, reboot, or power-loss behavior;
- concurrent-use behavior;
- delayed or offline delivery behavior;
- quorum behavior;
- implementation diversity;
- global event chronology;
- association-chain integrity; or
- universal rejection of every malformed input.

This is a bounded artifact-exchange and software-boundary result.

The campaign-level interpretation is summarized in `../../../RESULTS.md`, with source and execution provenance in `../../../PROVENANCE.md`.
