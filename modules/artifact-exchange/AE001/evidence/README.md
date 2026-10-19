# AE001 Evidence

This directory contains the retained preflight history and the frozen scored evidence for AE001 — Provider-Controlled Artifact Exchange.

The evidence is separated by purpose so setup activity, harness corrections, and scored results are not conflated.

## Structure

```text
evidence/
├── preflight/
│   ├── AE001_PREFLIGHT_20261018_R1/
│   └── AE001_PREFLIGHT_20261018_R2/
├── retained/
│   ├── PREFLIGHT_R1/
│   └── PREFLIGHT_R2/
└── scored/
    └── AE001_SCORED_20261018_R1/
```

## Preflight

`preflight/` contains the campaign setup history.

### `AE001_PREFLIGHT_20261018_R1`

Status: **INCOMPLETE**

The first preflight stopped before deployment because the source-transfer command exceeded the Windows command-line length limit.

No AE001 case executed and no architectural conclusion is derived from that run.

### `AE001_PREFLIGHT_20261018_R2`

Status: **PASS**

R2 completed the four-case preflight after source transfer was changed to SSH standard input.

It verified that the deployment topology, provider behavior, relay transport, evidence collection, state inspection, and provider-signature verification were functioning before scored execution.

## Retained Harnesses

`retained/` preserves the earlier campaign harness versions associated with the preflight runs.

They are retained for provenance and are not substitutes for the final scored harness.

The retained versions make it possible to distinguish:

- the R1 command-length failure;
- the R2 completed preflight;
- the later pre-score classification correction; and
- the final locked harness used for scoring.

## Scored Evidence

`scored/AE001_SCORED_20261018_R1/` contains the frozen scored run.

Overall result: **PASS**

The scored matrix was:

| Case | Expected Provider B behavior | Result |
|---|---|---|
| B01 | Accept valid Provider B authorization; START, one software execution, COMPLETE | PASS |
| N01 | Reject altered Provider B signature with `auth_bad_sig`; no execution or state consumption | PASS |
| N02 | Reject Provider A authorization with `auth_provider_mismatch`; no execution or state consumption | PASS |
| B02 | Accept fresh valid Provider B authorization after negatives; START, one software execution, COMPLETE | PASS |

Provider A also generated authenticated denials because no Provider A authorization was supplied. Those events are background path evidence, not additional scored cases.

## Evidence Types

The completed runs preserve the material needed to inspect the campaign independently, including:

- contract and run manifest;
- exact request material;
- original and transmitted authorization artifacts;
- issuer output;
- relay delivery records;
- raw provider-generated boundary packages;
- association-recorder records;
- provider state snapshots;
- provider execution snapshots;
- deployment identities;
- final role logs and state;
- scorecards; and
- SHA-256 checksum lists.

## Authority Boundary

Evidence collection does not create authorization authority.

The relay transported request and authorization material but did not determine whether execution was authorized.

The association recorder preserved provider-generated evidence but did not authorize execution.

Provider execution and provider-generated authenticated boundary packages are the consequential evidence.

## Evidence Interpretation

Relay HTTP `204` responses are transport outcomes only.

They are not treated as proof of authorization or execution.

Execution is established through provider-generated boundary evidence together with provider state and execution records.

The recorder's own classifications are not used as the independent signature-verification oracle.

## Preservation

Incomplete runs, successful preflight evidence, retained harness versions, and the scored run are all preserved separately.

Earlier evidence is not rewritten to match later corrections.

This separation is intentional: a harness or setup failure is not treated as a property failure, and a successful preflight is not treated as the scored result.

## Integrity

Each completed run contains its own `SHA256SUMS.txt`.

The AE001 root also contains a publication-level checksum list covering the published campaign files.

These checksum lists establish byte identity within the publication. They are not external signatures or independent timestamps.

## Scope

The evidence supports the bounded AE001 software result only.

It does not establish:

- physical actuation;
- arbitrary host-compromise resistance;
- key-compromise resistance;
- transport confidentiality;
- crash, reboot, or power-loss behavior;
- concurrent-use behavior;
- offline or delayed delivery;
- quorum behavior;
- implementation diversity;
- global chronology;
- association-chain integrity; or
- universal rejection of all malformed inputs.

The campaign-level result is summarized in:

`../RESULTS.md`

Source, topology, and execution provenance are documented in:

`../PROVENANCE.md`
