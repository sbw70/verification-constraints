# MP001 Evidence

This directory contains the retained setup, pre-run, scored-campaign, and archive evidence for MP001.

The evidence is separated by stage so that pre-run integration work is not confused with the scored campaign.

The normative protocol and scoring definitions are outside this directory:

- `../configs/MP001_CONTRACT.md`
- `../configs/MP001_RUN_MANIFEST.json`

## Pre-deployment baseline

`MP001_PREDEPLOY_BASELINE.txt` records the host and network state captured before deployment.

The baseline identifies the machines used for the principal MP001 roles:

- coordinator / association: `Xer0trust`
- NUVL relay: `nuvl-relay`
- Provider A: `Xer0trust-3`
- Provider B: `Xer0trust2`

It also records observed network interfaces, addresses, hostnames, Python versions, Git versions, and basic reachability information.

This file is environmental evidence. It does not establish a scored result.

## Topology freeze

`MP001_TOPOLOGY_FREEZE.txt` records the role assignment and network topology fixed for the campaign.

The retained topology assigns:

- `Xer0trust` — operator, coordinator, association, and evidence collection
- `nuvl-relay` — NUVL intermediary
- `Xer0trust-3` — independent Provider A
- `Xer0trust2` — independent Provider B
- Chromebook — requester / attacker role

The baseline network is recorded as `192.168.1.0/24`.

The topology freeze documents where the roles ran. It does not make the coordinator or association authoritative over provider execution.

## Pre-run association smoke

`PRE_RUN_ASSOC_SMOKE_001.jsonl` is an early association-recorder smoke session.

It contains:

- one `SESSION_START`
- no provider submissions
- one `SESSION_END`
- `submission_count: 0`

This file verifies that the recorder could create and close a retained session at that stage of preparation.

It is not scored evidence.

## Pre-run boundary smoke 001

`PRE_RUN_BOUNDARY_SMOKE_001.jsonl` contains another early pre-run recorder session.

It also contains:

- one `SESSION_START`
- no retained provider submissions
- one `SESSION_END`
- `submission_count: 0`

No provider execution claim is made from this session.

The file is retained as part of the setup history rather than removed because it did not produce boundary submissions.

## Pre-run boundary smoke 002

`PRE_RUN_BOUNDARY_SMOKE_002.jsonl` contains two signed provider `DENY` submissions generated without provider authorization.

The retained submissions identify:

- Provider A — `DENY`, `auth_missing`
- Provider B — `DENY`, `auth_missing`

Both signatures were recorded as valid against the registered provider boundary keys.

This session used an earlier recorder build and is retained as development evidence.

It is not part of the scored campaign.

## Pre-run boundary smoke 003

`PRE_RUN_BOUNDARY_SMOKE_003.jsonl` repeats the missing-authorization boundary check using the final recorder and final run-manifest state used immediately before the full-path smoke and scored campaign.

The association retained:

- Provider A — signed `DENY`, `auth_missing`
- Provider B — signed `DENY`, `auth_missing`

Both submissions:

- matched registered providers
- passed boundary-signature verification
- contained no authorization ID or authorization nonce
- were retained in the association record chain

The session records the final association recorder SHA-256:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

and final run-manifest SHA-256:

`37f2cea056bce67c209204467fa574c1d83307ec7e6df59815fb58eae20acf54`

This remains pre-run evidence, not a scored test case.

## Full-path pre-run smoke

`PRE_RUN_FULL_PATH_001/` contains the first retained end-to-end smoke run across the complete deployed path.

It includes:

- raw request input
- Provider A authorization
- Provider B authorization
- base64url authorization transport forms
- Provider A local execution evidence
- Provider B local execution evidence
- Provider A post-run spent state
- Provider B post-run spent state
- association observation log

The run produced valid `START` and `COMPLETE` boundary statements from both providers and verified that the complete path was functioning before scoring began.

See:

`PRE_RUN_FULL_PATH_001/README.md`

This run is deliberately kept separate from the scored campaign.

## Scored campaign

`MP001_SCORED_20261009/` contains the retained scored MP001 campaign.

It includes:

- B01-B10 baseline inputs and authorizations
- negative-test request and authorization artifacts
- requester logs
- hostile-relay artifacts
- forged-boundary artifact
- duplicate-boundary artifact
- complete association log
- association counts and hashes
- Provider A final state
- Provider B final state
- deployed implementation hashes
- evidence integrity manifest
- campaign scorecard

The retained scorecard reports:

- B01-B10 — PASS
- N01 — PASS
- N02 — PASS
- N03 — PASS
- N04 — PASS
- N05 initial attempt — RETAINED_MISFIRE
- N05 retry — PASS
- N06 — PASS
- scorecard assertions — PASS

See:

`MP001_SCORED_20261009/README.md`

for the folder-specific explanation of the scored artifacts and their limits.

## Frozen scored archive

`MP001_SCORED_20261009_FINAL.tar` is the retained archive of the frozen scored campaign evidence.

Its SHA-256 is:

`029cd08f6363ee694cb93f5ecfb83c37d447a1dec8d20b86bd1a09f752c562ca`

The hash is retained separately in:

`MP001_SCORED_20261009_FINAL.tar.sha256`

The archive preserves the scored evidence package independently of later publication documentation.

README files added afterward for repository navigation and explanation are not retroactively part of the frozen scored archive.

## Evidence stages

The material in this directory should be read in the following order:

1. `MP001_PREDEPLOY_BASELINE.txt` — initial host and network state
2. `MP001_TOPOLOGY_FREEZE.txt` — fixed role assignment
3. `PRE_RUN_ASSOC_SMOKE_001.jsonl` — association-recorder startup/close smoke
4. `PRE_RUN_BOUNDARY_SMOKE_001.jsonl` — retained early boundary-path attempt
5. `PRE_RUN_BOUNDARY_SMOKE_002.jsonl` — signed missing-authorization denials using an earlier recorder state
6. `PRE_RUN_BOUNDARY_SMOKE_003.jsonl` — signed missing-authorization denials using the final recorder state
7. `PRE_RUN_FULL_PATH_001/` — successful full-path integration smoke
8. `MP001_SCORED_20261009/` — scored campaign
9. `MP001_SCORED_20261009_FINAL.tar` — frozen scored evidence archive

The pre-run files are retained to preserve the preparation history. They are not silently folded into the scored result.

## Evidence boundaries

The association evidence records what the association received and whether provider boundary signatures verified.

Provider-local files record what each provider retained locally.

Requester logs record request-path observations such as HTTP responses.

These evidence classes are related but not interchangeable.

In particular:

- HTTP 204 establishes receipt at the relevant HTTP endpoint, not provider execution by itself
- a valid provider boundary signature establishes that the boundary statement verifies under the registered provider key, not that the association authorized the action
- a provider-local execution record is software-local execution evidence, not independent physical witness evidence
- timestamps are local observations and are not used to create a globally authoritative chronology
- association records are evidence of provider statements, not provider authority

## Scope

This directory supports examination of the MP001 deployment and scored campaign.

It does not by itself establish:

- physical actuation
- independent physical witness confirmation
- provider implementation diversity
- crash-window safety
- concurrent double-spend resistance
- power-loss persistence
- globally synchronized event timing
- security of arbitrary deployments outside the tested configuration

Those claims require separate evidence and should not be inferred from MP001.
