# AE001 Campaign Scripts

This directory contains the AE001 campaign harness and deployment launcher.

```text
scripts/
├── launch_role.py
└── run_ae001.py
```

The scripts orchestrate the campaign around the preserved MP003 implementation.

They do not replace the provider authorization logic being tested.

## `run_ae001.py`

`run_ae001.py` is the AE001 campaign harness.

It performs the end-to-end preflight or scored run, including:

- locked source/configuration identity checks;
- isolated remote deployment;
- role startup;
- fresh authorization minting;
- four-case execution;
- provider state snapshots;
- execution snapshots;
- raw boundary-package collection;
- independent provider-signature verification;
- relay delivery inspection;
- association-record collection;
- final state collection;
- canonical MP003 state bookends;
- scorecard generation; and
- per-run SHA-256 checksum generation.

## Required Arguments

The harness accepts:

```text
--root
--identity
--known-hosts
--phase
--run-id
```

`--phase` must be either:

```text
preflight
scored
```

The run ID must begin with:

```text
AE001_
```

Each run uses a new evidence directory and fresh remote runtime directory.

Existing run directories are not silently reused.

## Scored Lock Enforcement

For a scored run, the harness verifies the files listed in:

`../configs/AE001_LOCK_SHA256SUMS.txt`

before proceeding.

It also verifies the source/configuration hashes defined in:

`../configs/AE001_RUN_MANIFEST.json`

A source or locked configuration mismatch stops the campaign rather than silently running a different test definition.

## Deployment

The harness deploys campaign material over SSH to the configured Linux hosts.

Each remote run uses:

```text
/home/seth/ARTIFACT_EXHANGE/RUN_ID
```

The deployment contains only the files required by that role.

Provider A and Provider B receive their own provider source and laboratory key material.

The relay host receives the relay and association-recorder sources plus public provider trust material.

The campaign initializes fresh runtime state only inside the new AE001 run directory.

Canonical MP003 runtime state is not used as the campaign's writable state.

## Four-Case Sequence

The harness executes the cases in this fixed order:

```text
B01
N01
N02
B02
```

### B01

Creates a fresh Provider B authorization matching a fresh request.

Required Provider B result:

```text
START
COMPLETE
```

with exactly one new software execution and one newly spent authorization.

### N01

Creates a fresh valid Provider B authorization, preserves the original, then alters one decoded signature byte in the transmitted copy.

Required Provider B result:

```text
DENY auth_bad_sig
```

with Provider B execution and spent state unchanged.

### N02

Creates a fresh valid Provider A authorization and presents it in the Provider B authorization header.

Required Provider B result:

```text
DENY auth_provider_mismatch
```

with Provider B execution and spent state unchanged.

### B02

Creates another fresh valid Provider B authorization after both negative cases.

Required Provider B result:

```text
START
COMPLETE
```

with exactly one additional software execution and one additional spent authorization.

## Independent Boundary Verification

For each provider boundary package, the harness:

1. decodes the raw signed package;
2. selects the provider-specific public boundary key;
3. verifies the Ed25519 signature;
4. derives the raw public key bytes;
5. computes the expected key ID as SHA-256 of those raw bytes;
6. checks the package key ID; and
7. checks the request binding.

The association recorder's own verification fields are not used as the independent signature-verification oracle.

## Provider A Background Events

The relay contacts both configured providers.

The defined AE001 requests do not contain a Provider A authorization header.

Provider A therefore produces:

```text
DENY auth_missing
```

for each case.

The harness requires those authenticated Provider A denials as background path evidence.

They are not counted as additional AE001 cases.

## State Checks

The harness snapshots Provider A and Provider B state before and after every case.

For negative cases, Provider B state and execution evidence must remain byte-identical.

For positive cases, the harness requires:

- exactly one new spent authorization;
- exactly one new execution record;
- matching authorization ID; and
- matching operation ID.

Provider A state and execution must remain unchanged throughout the four-case campaign.

## Canonical MP003 Noninterference

Before campaign execution, the harness records hashes of relevant existing MP003 state files on the provider hosts.

After the run, those files are hashed again.

The campaign requires the before and after identities to match.

This check supports the claim that AE001 used isolated campaign state rather than modifying the canonical MP003 runtime state.

## Evidence Collection

Each run produces an evidence directory under:

```text
../evidence/<phase>/<run-id>/
```

The harness writes or collects:

- contract copy;
- run-manifest copy;
- input identity;
- deployment identities;
- per-case request;
- original authorization;
- transmitted authorization;
- mint output;
- requester delivery record;
- relay delivery record;
- raw provider boundary packages;
- association records;
- provider state snapshots;
- provider execution snapshots;
- state-presence/hash metadata;
- final runtime logs;
- canonical state bookends;
- `SCORECARD.json`; and
- `SHA256SUMS.txt`.

## Status Model

The harness distinguishes three campaign outcomes.

### PASS

All defined case criteria and final evidence requirements were satisfied.

### FAIL

A tested property failed.

For example, an authenticated unexpected provider admission during a rejection case is a property failure.

### INCOMPLETE

The campaign could not establish a scored outcome because of missing evidence, deployment failure, broken precondition, collection failure, or another test-harness/environment problem.

This distinction prevents infrastructure failures from being silently reported as property failures.

## `launch_role.py`

`launch_role.py` starts one preserved MP003 role using AE001-specific runtime configuration.

Supported roles are:

```text
provider_a
provider_b
relay
association
```

The launcher imports the preserved MP003 source and changes deployment-specific configuration only.

## Provider Configuration

For Provider A and Provider B, the launcher configures:

- listen host;
- provider port;
- association-recorder URL;
- fresh AE001 spent-state path; and
- fresh AE001 execution-log path.

It does not replace the provider's authorization evaluation, state-consumption, execution, or boundary-signing methods.

## Relay Configuration

For the relay, the launcher configures:

- relay port;
- Provider A endpoint;
- Provider B endpoint; and
- provider-specific authorization-header names.

It also installs an observational Python audit hook for outbound `urllib.Request` construction.

The audit hook records:

```text
URL
HTTP method
outbound body bytes
```

to the relay delivery log.

It does not alter request arguments or decide provider outcomes.

## Association Configuration

For the association recorder, the launcher supplies:

- session ID;
- provider registry;
- run manifest;
- contract;
- association log path; and
- association port.

The recorder remains an evidentiary component.

It does not gain provider execution authority.

## Shutdown

The campaign harness sends interrupt signals to started roles during shutdown and then performs final evidence collection.

Shutdown or collection problems are recorded separately and may cause a run to be classified `INCOMPLETE`.

## Reproduction Example

From the AE001 root:

```bash
python scripts/run_ae001.py \
  --root . \
  --identity PATH_TO_SSH_PRIVATE_KEY \
  --known-hosts PATH_TO_KNOWN_HOSTS \
  --phase preflight \
  --run-id AE001_PREFLIGHT_FRESH1
```

A scored run uses:

```text
--phase scored
```

with a fresh scored run ID after the intended configuration has been locked.

## Scope

These scripts are campaign orchestration and evidence tooling.

They do not establish the AE001 result by themselves.

The result depends on the locked definition, preserved implementation, provider-generated evidence, provider state, execution evidence, and scored records published with the campaign.
