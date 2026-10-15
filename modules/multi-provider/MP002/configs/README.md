# Configuration

This directory contains the locked MP002 contract and run manifest used to define the scored campaign before execution.

These files establish the test rules, expected cases, implementation hashes, and claim boundaries against which the scored evidence is interpreted.

## Contents

- `MP002_CONTRACT.md` — normative test contract for MP002.
- `MP002_RUN_MANIFEST.json` — machine-readable description of the scored campaign, expected cases, fixed implementation hashes, and declared claim boundaries.

## Locked contract

`MP002_CONTRACT.md` defines the behavior expected from the multi-provider path.

Its SHA-256 is:

`e795f55172ea27d8ee434679ab9ea4a1b07e1154a708dfd5ad846fdd0f4ab18d`

The contract defines the authorization and boundary-event formats, provider validation path, durable authorization consumption, signed provider evidence, and Provider B's MP002 local-policy condition.

For MP002, the relevant Provider B ordering is:

valid provider-specific authorization  
→ request/context validation  
→ provider-local policy evaluation  
→ `DENY policy_denied` if the divergence condition applies  
→ otherwise require unspent authorization  
→ durable consumption  
→ `START`  
→ execution  
→ durable execution evidence  
→ `COMPLETE`

The policy denial therefore occurs before authorization consumption.

## Run manifest

`MP002_RUN_MANIFEST.json` defines the specific scored campaign.

Its SHA-256 is:

`3f4b317e3c3fc8f34e579941ec79f0f0191fcef122be320973a88b84e5750845`

The manifest defines two scored cases.

### B01_CONTROL

Verification context:

`CTX_ALPHA`

Expected result:

- Provider A: `START`, execution, `COMPLETE`
- Provider B: `START`, execution, `COMPLETE`

This is the control case showing the normal path when both providers independently permit the request.

### D01_POLICY_DIVERGENCE

Verification context:

`CTX_MP002_DIVERGE`

Expected result:

- Provider A: `START`, execution, `COMPLETE`
- Provider B: `DENY policy_denied`
- no Provider B execution
- no Provider B authorization consumption

This is the scored policy-divergence case.

## Fixed implementation inputs

The scored campaign used fixed implementations and configuration identified by hash.

Among the locked components were:

- association recorder;
- provider registry;
- NUVL relay;
- Provider A runtime;
- Provider A mint utility;
- Provider B runtime;
- Provider B mint utility.

The deployed hashes are also preserved with the scored evidence in:

`../evidence/scored/deployed_implementation_hashes.txt`

The manifest and deployed-hash record allow the published evidence to be tied back to the implementations used during the scored campaign.

## Relationship to MP001

MP002 is an extension of the MP001 multi-provider baseline.

Several components were intentionally reused unchanged, including:

- the relay;
- Provider A runtime;
- Provider A mint utility;
- Provider B mint utility;
- association recorder;
- provider registry.

Provider B was changed to add the deterministic local-policy gate used by D01.

The source-level difference is published under:

`../provider_b/MP001_TO_MP002_PROVIDER_B.diff`

This keeps the MP002 experimental delta narrow and inspectable.

## Claim boundaries

The manifest explicitly does not claim that MP002 tests:

- physical witness behavior;
- globally synchronized cross-host timing;
- implementation diversity;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- compromised-provider containment;
- independent association re-verification.

Those properties are outside the scored MP002 campaign.

MP002 is specifically a test of provider-local policy divergence within the distributed multi-provider path.

## Cross-provider atomicity

The MP002 contract does not require all providers to approve before another provider executes.

Accordingly, D01 permits the observed result:

- Provider A executes.
- Provider B denies.

This demonstrates independent provider judgment.

It does not demonstrate an all-or-nothing distributed transaction.

A design requiring every necessary provider to approve before any consequence occurs would require a separate composition, quorum, or pre-execution gating mechanism and is not tested here.

## Locked evidence copies

Copies of both configuration files are preserved inside the scored evidence directory:

`../evidence/scored/MP002_CONTRACT.md`

`../evidence/scored/MP002_RUN_MANIFEST.json`

Those copies were verified byte-for-byte against the files in this directory during publication staging.

The duplicate copies exist so the scored evidence set remains self-contained while the canonical publication copies remain available here.

## Integrity discipline

The contract and manifest were fixed before the scored campaign.

They were not rewritten after observing the result.

Interpretive material added later in `RESULTS.md`, `PROVENANCE.md`, or the folder documentation does not alter the test conditions encoded in these locked files.

This distinction is intentional:

the configuration defines the test;  
the evidence records what happened;  
the documentation explains what the evidence supports.

## Related material

Scored evidence:

`../evidence/scored/`

Provider A implementation:

`../provider_a/`

Provider B implementation and MP001-to-MP002 diff:

`../provider_b/`

Association implementation:

`../association/`

Relay implementation:

`../intermediary/`
