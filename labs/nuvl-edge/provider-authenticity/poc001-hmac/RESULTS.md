# POC-001 Results

## Summary

POC-001 evaluated bounded disconnected authority during temporary provider unavailability using HMAC-SHA256 authenticated artifacts.

The test exercised a provider-first normal path and a bounded disconnected path in which a previously issued artifact could authorize one matching request while the provider was unavailable.

The original test was performed on July 11, 2026.

## Test Sequence

The recorded sequence exercised:

1. provider-reachable baseline;
2. provider unavailable with a valid bounded artifact;
3. replay of the consumed artifact;
4. missing artifact;
5. wrong-context artifact;
6. wrong-action artifact;
7. expired artifact;
8. provider restoration.

## Results

| Test condition | Expected | Observed |
|---|---|---|
| Provider reachable baseline | ACCEPT | ACCEPT |
| Provider unavailable with valid, unexpired, unused artifact | ACCEPT once | ACCEPT |
| Replay of consumed artifact | DENY | DENY |
| Missing artifact | DENY | DENY |
| Wrong context | DENY | DENY |
| Wrong action | DENY | DENY |
| Expired artifact | DENY | DENY |
| Provider restored | ACCEPT | ACCEPT |

**Overall result: PASS**

All recorded POC-001 conditions produced the expected behavior.

## Provider-Reachable Baseline

With the provider reachable, the request followed the normal provider-first path.

The configured action and context were evaluated by the provider.

**Observed result: ACCEPT**

This established the provider-backed baseline before disconnected operation was exercised.

## Provider-Unavailable — Valid Bounded Artifact

A bounded artifact was issued before provider loss.

The artifact included authenticated constraints for:

- action;
- context;
- nonce;
- issuance time;
- expiration time;
- maximum use count;
- request representation.

The provider was then made unavailable.

A matching request was submitted while the artifact remained valid and unused.

**Observed result: ACCEPT**

The bounded-path response reported:

    decision=accepted
    reason=bounded_artifact_valid_once
    path=provider_unavailable_bounded_window

The artifact was admitted for one matching request during provider unavailability.

## Replay

The same artifact was submitted again after successful use.

**Observed result: DENY**

The response reported:

    reason=artifact_replay

This established single-use behavior during the lifetime of the running boundary process.

## Missing Artifact

A request was submitted during provider unavailability without a bounded artifact.

**Observed result: DENY**

The response reported:

    reason=missing_artifact
    path=provider_unavailable_fail_closed

Provider unavailability alone did not authorize the request.

## Wrong Context

An artifact was presented for a context different from the context encoded in the artifact.

**Observed result: DENY**

The response reported:

    reason=artifact_wrong_context

## Wrong Action

An artifact was presented for an action different from the action encoded in the artifact.

**Observed result: DENY**

The response reported:

    reason=artifact_wrong_action

## Expired Artifact

An artifact was presented after expiration.

**Observed result: DENY**

The response reported:

    reason=artifact_expired

## Provider Restoration

Provider service was restored after the disconnected-path conditions.

Normal provider-backed validation resumed.

**Observed result: ACCEPT**

The test therefore returned from bounded disconnected operation to the normal provider-first path without introducing a permanent local authorization mode.

## Fail-Closed Assessment

The recorded test directly established denial for:

- replayed artifact;
- missing artifact;
- wrong context;
- wrong action;
- expired artifact.

The surviving boundary implementation contains additional denial paths for malformed or otherwise inadmissible artifacts.

Those implementation paths are not claimed as separately exercised POC-001 results unless supported by the contemporaneous test record.

## Single-Use Assessment

The tested artifact specified a maximum use count of one.

After successful disconnected acceptance, subsequent use of the same artifact was denied as replay.

This supports single-use enforcement during the running boundary process.

POC-001 does not establish persistence of spent state across boundary restart or power loss.

## Provider-Unavailable Assessment

The provider-unavailable condition did not create general local acceptance authority.

Observed behavior was:

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

Acceptance during provider loss therefore depended on previously issued bounded authority rather than provider unavailability itself.

## HMAC Trust Limitation

POC-001 used a shared HMAC secret.

The provider used that secret to authenticate bounded artifacts, and the Raspberry Pi boundary possessed the same secret in order to validate them.

This architecture does not establish exclusive provider cryptographic issuance authority because the boundary possessed cryptographic material capable of generating valid HMAC authentication values.

This limitation affects the authority-separation claim, not the observed bounded-disconnected behavior.

POC-002 subsequently replaced the shared-secret relationship with Ed25519 provider signing and public-key verification at the boundary.

## Evidence Status

The original interactive terminal transcript from the July 11, 2026 execution was not retained.

The behavioral results documented here derive from the contemporaneous NUVL hardware laboratory record.

No reconstructed terminal output is represented as original runtime evidence.

Artifact identity, cross-host correspondence, and publication status are documented separately in `PROVENANCE.md`.

## Supported Result

POC-001 demonstrated, within the tested HMAC architecture:

- provider-backed acceptance during normal availability;
- one-time acceptance of valid bounded authority during provider unavailability;
- replay denial;
- denial when no artifact was supplied;
- context binding;
- action binding;
- expiration enforcement;
- fail-closed behavior when valid bounded authority was absent;
- restoration of provider-backed operation after provider recovery.

## Claim Boundary

POC-001 does not establish:

- exclusive provider signing authority;
- asymmetric provider authenticity;
- persistent replay protection across restart or power loss;
- crash-safe spent-state persistence;
- multi-boundary double-spend resistance;
- endpoint-local cryptographic verification;
- exactly-once physical execution;
- protection against arbitrary privileged compromise of the Raspberry Pi boundary.

Those properties require separate evidence.
