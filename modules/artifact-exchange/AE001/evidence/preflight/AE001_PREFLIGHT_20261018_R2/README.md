# AE001 Preflight — AE001_PREFLIGHT_20261018_R2

This directory contains the completed AE001 preflight run used to validate the campaign setup before scored execution.

Run ID: **AE001_PREFLIGHT_20261018_R2**  
Phase: **preflight**  
Overall result: **PASS**

## Purpose

R2 verified that the AE001 topology, deployment process, request/artifact flow, provider behavior, boundary-signature verification, state inspection, and evidence collection all functioned as expected before the scored run was frozen.

It used the same four-case structure later used for scoring.

## Preflight Cases

| Case | Provider B outcome | Result |
|---|---|---|
| B01 | START → one software execution → COMPLETE | PASS |
| N01 | DENY `auth_bad_sig`; no execution or state consumption | PASS |
| N02 | DENY `auth_provider_mismatch`; no execution or state consumption | PASS |
| B02 | START → one software execution → COMPLETE | PASS |

Provider A also produced one authenticated `DENY` in each case because no Provider A authorization header was supplied.

Those denials are background path evidence and are not separate scored cases.

## What R2 Corrected

The earlier R1 preflight stopped before deployment because its encoded SSH source-transfer command exceeded the Windows command-line length limit.

R2 changed source transfer to use SSH standard input instead.

That correction affected the campaign transport mechanism only. It did not change:

- provider authorization logic;
- relay authorization semantics;
- provider boundary generation;
- artifact format;
- request binding;
- case definitions; or
- expected outcomes.

## Evidence

This directory preserves the full completed preflight package, including:

- contract and run manifest;
- deployment records;
- canonical state bookends;
- input identity;
- exact per-case request and authorization material;
- relay delivery records;
- raw provider-generated boundary packages;
- association-recorder records;
- provider execution and state snapshots;
- final role logs and state;
- `SCORECARD.json`; and
- `SHA256SUMS.txt`.

## Result Details

For both positive cases:

- Provider B accepted the matching fresh Provider B authorization;
- Provider B generated authenticated `START`;
- one software execution was recorded;
- Provider B generated authenticated `COMPLETE`; and
- one additional authorization entered spent state.

For N01:

- the original valid Provider B authorization was preserved separately;
- one decoded signature byte in the transmitted authorization was altered;
- Provider B returned authenticated `DENY auth_bad_sig`;
- no Provider B execution occurred; and
- Provider B spent-authority state remained unchanged.

For N02:

- a valid fresh Provider A authorization was presented to Provider B;
- Provider B returned authenticated `DENY auth_provider_mismatch`;
- no Provider B execution occurred; and
- Provider B spent-authority state remained unchanged.

## Signature Verification

The preflight harness independently verified provider-specific signatures on the raw boundary packages.

The association recorder preserved provider submissions but was not used as the signature-verification oracle and did not authorize execution.

## Relay Role

The relay transported the request and provider-specific authorization material.

It did not decide whether Provider B should execute.

Relay delivery evidence was correlated with provider-generated boundary records and provider state. HTTP `204` from the relay was treated only as a transport result.

## Canonical State

The campaign used isolated AE001 runtime directories.

Canonical MP003 state was checked before and after the preflight and remained unchanged.

## Pre-Score Harness Correction

After R2 passed, inspection identified one scoring-logic edge case in the harness: an authenticated unexpected admission during a rejection case could be encountered together with excess boundary events.

Before the scored-run freeze, that branch was corrected so such an admission is classified as **FAIL**.

The correction did not change the providers, relay, protocol, artifact format, case matrix, or expected results.

The R2 harness is retained separately at:

`../../retained/PREFLIGHT_R2/run_ae001.py`

The corrected final harness used for scoring is:

`../../../scripts/run_ae001.py`

## Integrity

`SHA256SUMS.txt` records hashes for the R2 preflight evidence package.

The checksum file establishes byte identity within the published package. It is not an external signature or timestamp.

## Status

**PASS — preflight completed successfully.**

R2 established that the campaign setup was suitable to proceed to the separately frozen scored run.
