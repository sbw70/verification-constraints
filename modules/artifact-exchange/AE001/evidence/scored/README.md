# AE001 Scored Evidence

This directory contains scored AE001 campaign evidence.

The current scored run is:

`AE001_SCORED_20261018_R1`

Overall result: **PASS**

## Scored Run

The scored campaign used the locked AE001 contract, run manifest, source identities, and four-case matrix.

| Run | Result |
|---|---|
| `AE001_SCORED_20261018_R1` | PASS |

The run tested whether request-bound provider-issued verification material could traverse an intermediary while the target provider retained artifact evaluation, execution authority, and authenticated execution-boundary signaling.

The four scored cases were:

- **B01** — valid Provider B authorization → START, one software execution, COMPLETE.
- **N01** — altered Provider B signature → `DENY auth_bad_sig`, with no execution or state consumption.
- **N02** — valid Provider A authorization presented to Provider B → `DENY auth_provider_mismatch`, with no execution or state consumption.
- **B02** — fresh valid Provider B authorization after both negative cases → START, one software execution, COMPLETE.

## Evidence

The scored run preserves:

- the contract used for execution;
- the run manifest;
- input and source identities;
- deployment records;
- exact per-case request and authorization material;
- relay delivery records;
- raw provider-generated boundary packages;
- association-recorder records;
- provider state and execution snapshots;
- final runtime logs and state;
- the scored `SCORECARD.json`; and
- a per-run `SHA256SUMS.txt`.

The detailed evidence package is under:

`AE001_SCORED_20261018_R1/`

## Interpretation

The scored result supports the bounded AE001 property for the tested software configuration:

provider-issued authorization material traversed the intermediary without making the intermediary the authorization evaluator or execution authority.

Provider B accepted valid Provider B material, rejected altered material, rejected Provider A material, preserved state across the negative cases, and successfully executed again afterward.

The relay transported the request and authorization material. It did not determine whether execution was authorized.

The association recorder preserved provider-generated evidence but did not authorize execution.

## Scope

This scored evidence establishes a software-boundary result only.

It does not establish physical actuation, arbitrary host-compromise resistance, key-compromise resistance, crash/reboot behavior, concurrent-use behavior, offline delivery, quorum behavior, implementation diversity, global chronology, or universal malformed-input rejection.

Campaign-level results are summarized in:

`../../RESULTS.md`

Source and execution provenance are documented in:

`../../PROVENANCE.md`
