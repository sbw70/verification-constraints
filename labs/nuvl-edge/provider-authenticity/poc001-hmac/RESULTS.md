# POC-001 Results

## Summary

POC-001 tested bounded disconnected authority during provider unavailability using HMAC-SHA256 authenticated artifacts.

The test established a provider-first normal path and a bounded fallback path in which a previously issued artifact could authorize one matching request while the provider was unavailable.

The original test was performed July 11, 2026.

## Test Sequence

The recorded test sequence exercised:

1. provider-reachable baseline;
2. provider unavailable with a valid bounded artifact;
3. replay of the consumed artifact;
4. missing artifact;
5. wrong-context artifact;
6. wrong-action artifact;
7. expired artifact;
8. provider restoration.

## Provider-Reachable Baseline

With the provider reachable, the request followed the normal provider-first path.

The configured action and context were evaluated by the provider.

**Observed result: ACCEPT.**

This established the normal provider-backed baseline before testing disconnected behavior.

## Provider Unavailable — Valid Bounded Artifact

A provider-issued artifact was obtained before provider loss.

The artifact contained authenticated constraints including:

```text
action
context
nonce
issued_at
expires_at
max_uses=1
request_repr
```

The provider was then made unavailable.

A request matching the artifact's action and context was submitted through the Raspberry Pi boundary while the artifact remained unexpired and unused.

The boundary validated the artifact through the bounded provider-unavailable path.

**Observed result: ACCEPT.**

The accepted bounded-path condition corresponded to:

```text
decision=accepted
reason=bounded_artifact_valid_once
path=provider_unavailable_bounded_window
```

## Replay

The same bounded artifact was submitted again after its successful use.

The artifact nonce had already been entered into the boundary's used-nonce state.

**Observed result: DENY.**

The replay condition corresponded to:

```text
reason=artifact_replay
```

The artifact therefore produced one accepted disconnected use during the running boundary process.

## Missing Artifact

A request was submitted during provider unavailability without a bounded artifact.

**Observed result: DENY.**

The missing-artifact condition corresponded to:

```text
reason=missing_artifact
path=provider_unavailable_fail_closed
```

Provider unavailability alone did not produce acceptance.

## Wrong Context

A bounded artifact was presented against a context outside the context encoded into the artifact.

**Observed result: DENY.**

The context mismatch corresponded to:

```text
reason=artifact_wrong_context
```

## Wrong Action

A bounded artifact was presented against an action outside the action encoded into the artifact.

**Observed result: DENY.**

The action mismatch corresponded to:

```text
reason=artifact_wrong_action
```

## Expired Artifact

A bounded artifact was presented after its validity window had expired.

**Observed result: DENY.**

The expiration condition corresponded to:

```text
reason=artifact_expired
```

## Provider Restoration

Provider service was restored after the provider-unavailable test conditions.

Normal provider-backed validation resumed.

**Observed result: ACCEPT.**

The test therefore returned from the bounded disconnected path to the normal provider-first path after provider availability was restored.

## Consolidated Results

| Test condition | Expected | Observed |
|---|---|---|
| Provider reachable baseline | ACCEPT | ACCEPT |
| Provider unavailable + valid unexpired unused artifact | ACCEPT once | ACCEPT |
| Replay of consumed artifact | DENY | DENY |
| Missing artifact | DENY | DENY |
| Wrong context | DENY | DENY |
| Wrong action | DENY | DENY |
| Expired artifact | DENY | DENY |
| Provider restored | ACCEPT | ACCEPT |

**Result: PASS for all recorded POC-001 conditions.**

## Fail-Closed Conditions

The surviving boundary implementation contains explicit denial paths for:

```text
missing_artifact
artifact_decode_failed
artifact_signature_invalid
artifact_wrong_action
artifact_wrong_context
artifact_request_binding_invalid
artifact_expired
artifact_not_single_use
artifact_missing_nonce
artifact_replay
```

Not every implementation-level denial reason above was a separately recorded POC-001 test case.

The recorded behavioral test set specifically established denial for:

- replay;
- missing artifact;
- wrong context;
- wrong action;
- expired artifact.

The remaining implementation paths are documented as surviving source behavior rather than claimed as independently exercised POC-001 results.

## Single-Use Result

The bounded artifact specified:

```text
max_uses=1
```

After successful validation, its nonce was recorded in the boundary's in-memory used-nonce state.

A second use was denied.

This result supports single-use enforcement during the running boundary process.

It does not establish persistent single-use enforcement after boundary restart or power loss.

## Provider-Unavailable Result

The provider-unavailable condition did not create a general local acceptance mode.

The boundary accepted only when the previously issued bounded artifact passed the required validation checks.

Without an admissible artifact, the provider-unavailable path denied the request.

The tested behavior was therefore:

```text
provider reachable
        |
        v
provider-backed validation
        |
        v
ACCEPT


provider unavailable
        |
        v
valid bounded artifact
        |
        v
ACCEPT ONCE


provider unavailable
        |
        v
missing / invalid / expired /
mismatched / replayed artifact
        |
        v
DENY
```

## HMAC Authority Limitation

POC-001 used a shared HMAC secret.

The provider used that secret to authenticate bounded artifacts.

The Raspberry Pi boundary possessed the same secret in order to validate them.

Consequently, the POC-001 cryptographic arrangement did not restrict artifact origination exclusively to the provider.

The boundary possessed cryptographic material sufficient to calculate valid HMAC authentication values.

This does not invalidate the behavioral result of the bounded disconnected test.

It limits the authority-separation claim that can be made from POC-001.

POC-002 subsequently replaced this shared-secret arrangement with Ed25519 provider signing and public-key verification at the boundary.

## Evidence Status

The original interactive terminal transcript from the July 11, 2026 execution is not included in this package.

The behavioral results in this document are preserved from the contemporaneous NUVL hardware laboratory record.

The surviving implementation artifacts include:

```text
ddil_provider.py
ddil_boundary.py
```

The provider implementation is included in the public package.

The boundary implementation remains outside the public package.

The original boundary source survives independently on the Windows test host and Raspberry Pi with matching SHA-256:

```text
7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d
```

The original provider source has SHA-256:

```text
97aad386e48813488047503030de277d165a4a9040d758d7679d330a7ba0ebeb
```

See `PROVENANCE.md` for artifact-level provenance.

## Interpretation

POC-001 demonstrated that a previously issued, time-limited, request-bound artifact could provide narrowly bounded authority during temporary provider unavailability.

The recorded test established:

- normal provider-backed acceptance;
- acceptance of a valid bounded artifact during provider loss;
- denial of artifact replay;
- denial without an artifact;
- denial for wrong context;
- denial for wrong action;
- denial after artifact expiration;
- restoration of normal provider-backed acceptance.

The experiment also identified a material trust-placement limitation: HMAC verification required the boundary to possess the same secret used to authenticate artifacts.

POC-001 therefore established the bounded disconnected behavior but did not establish exclusive provider cryptographic issuance authority.

## Claim Boundary

POC-001 supports a bounded disconnected-authority behavioral result under the tested HMAC architecture.

It does not establish:

- exclusive provider signing authority;
- asymmetric provider authenticity;
- persistent replay protection across boundary restart;
- replay protection across power loss;
- crash-safe spent-state persistence;
- multi-boundary double-spend resistance;
- direct cryptographic verification at the ESP32;
- exactly-once physical execution;
- security after arbitrary privileged compromise of the Raspberry Pi boundary.

Those properties require separate evidence.
