# Smoke Evidence

This directory contains the retained MP002 smoke-test artifacts used to validate the distributed path before the scored campaign.

The smoke run was a pre-scored deployment check. It confirmed that the requester-to-relay-to-provider-to-association path was functioning and that the intended Provider B policy-divergence behavior was reachable before the scored state was reset.

These artifacts are preserved for provenance and troubleshooting. They are not substituted for the scored evidence under `../scored/`.

## Contents

- `MP002_SMOKE_001.jsonl` — association record produced during the smoke session.
- `MP002_SMOKE_001_SUMMARY.txt` — retained summary of the smoke results.
- `B01_CONTROL/` — request and authorization artifacts for the smoke control case.
- `D01_POLICY_DIVERGENCE/` — request, authorization, and retained post-run artifacts for the smoke divergence case.

## Smoke session

Session:

`MP002_SMOKE_001`

The smoke run exercised the same two logical cases later used in the scored campaign.

### B01_CONTROL

Both providers received the same request under:

`CTX_ALPHA`

Both providers accepted their own valid provider-specific authorization and executed.

Observed behavior:

- Provider A: `START`, `COMPLETE`
- Provider B: `START`, `COMPLETE`

Result:

**PASS**

### D01_POLICY_DIVERGENCE

Both providers received the same request under:

`CTX_MP002_DIVERGE`

Provider A permitted and executed the request.

Provider B validated its own authorization and then denied under its local policy before authorization consumption or execution.

Observed behavior:

- Provider A: `START`, `COMPLETE`
- Provider B: `DENY policy_denied`

Result:

**PASS**

## Smoke-state result

After the smoke run:

Provider A had:

- 2 execution records.
- 2 consumed authorizations.

Provider B had:

- 1 execution record.
- 1 consumed authorization.

For the smoke D01 authorization:

- Provider A authorization consumed: `True`
- Provider B authorization consumed: `False`

This matched the intended MP002 behavior before the scored run began.

## Separation from the scored campaign

The smoke run and scored campaign are separate evidence sets.

After smoke validation, the provider scored-state files were reset to clean valid state before the scored campaign.

The scored campaign used newly minted authorizations rather than reusing the smoke authorizations.

The scored association session was also started separately under:

`MP002_SCORED_20261013`

The authoritative scored evidence is preserved under:

`../scored/`

## What the smoke evidence supports

The smoke material shows that the test path and policy-divergence mechanism were exercised successfully before scoring.

It is useful for:

- deployment provenance;
- confirming the intended test condition was reachable;
- distinguishing setup validation from scored evidence;
- troubleshooting differences between pre-scored and scored operation.

## What the smoke evidence does not establish

The smoke run is not the scored basis for the MP002 result.

It does not add claims beyond the scored campaign and should not be used to substitute for:

- the scored association record;
- scored provider-local final state;
- scored authorization artifacts;
- the locked scored manifest;
- the scored contract;
- the scored integrity manifest.

It also does not establish:

- cross-provider atomicity;
- globally synchronized chronology;
- implementation diversity;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- compromised-provider containment;
- physical actuation;
- independent hardware-witness evidence.

## Related evidence

The scored campaign is preserved in:

`../scored/`

The overall evidence directory is documented in:

`../README.md`
