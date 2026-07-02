# NUVL Challenge

This is a live endurance challenge for a provider-isolated verification boundary.

The challenge is not to prove that invalid traffic can be rejected once. The challenge is to test whether the denial path stays closed while the admissible provider control path remains intact under continuous hostile or invalid traffic.

## What You're Looking At

### `nuvl.py`

Stateless verification boundary.

NUVL receives requests and forwards provider-bound artifacts, but does not authorize, does not hold provider signing material, and does not decide outcomes.

### `provider.py`

The only authority in the system.

The provider validates request structure, token binding, context, replay state, and execution admissibility.

### `client.py`

Reference implementation of a valid request path.

Use this to understand what an admissible request is supposed to look like.

### `attacker.py`

Attack harness and boundary-check tool.

Use it to test how the boundary responds when request fields are malformed, stale, replayed, mismatched, or incorrectly signed.

## Architecture

`client / attacker → NUVL → provider`

NUVL forwards requests but does not decide outcomes.

The provider performs all verification.

The provider is not publicly exposed.

## Objective

Cause the provider to print:

`INITIATED`

That is the success condition.

If this occurs, the provider has accepted the request as admissible inside its own boundary.

## Constraints

You do not have the provider signing key.

There is no identity system to exploit.

NUVL does not authorize anything.

NUVL does not mint provider tokens.

NUVL does not hold provider signing material.

All execution authority exists behind the provider boundary.

Replay attempts are detected and rejected.

## Attack Harness: Check the Boundary

The included attack harness is a check-your-work tool.

Start with a valid provider-side artifact. Break one variable at a time. Confirm that the request is denied in the expected bucket.

The purpose is not only to reject invalid traffic. The purpose is to confirm that the boundary fails closed and that denial attribution remains stable.

Examples:

- bad signature should produce `bad_signature`
- expired artifact should produce `expired`
- malformed expiry should produce `bad_expiry`
- wrong context should produce `bad_context`
- missing required field should produce `missing_fields`
- malformed token should produce `malformed`
- replayed nonce should produce `replay`

If changing only one field causes the wrong denial bucket, the implementation is not attributing the failure cleanly.

If an invalid artifact reaches downstream provider activation before denial, the boundary is not holding.

## Endurance Behavior

The live challenge is also an endurance test.

Most traffic is expected to be invalid and denied. The relevant question is whether NUVL can continue rejecting invalid/default-denied traffic while preserving the admissible provider control path.

The useful signal is not raw denial count.

The useful signal is:

The denial path stays closed.

The control path stays intact.

## Observability

The provider tracks:

- total attempts
- initiated operations
- denied requests
- denial reasons
- control-stream completion
- timeouts
- internal errors
- performance metrics
- system load

Stats update continuously.

Traffic appears in real time on the live control plane.

## What Has Already Been Tried

The included harness covers:

- malformed tokens
- signature guessing
- replay attacks
- context swapping
- body mutation
- invalid encodings
- burst traffic
- sustained load

You can modify the harness to test additional cases against your own implementation or against the live challenge endpoint.

## Notes

This is not a simulation.

The boundary is real.

The provider enforces all decisions.

NUVL can carry the request, but it cannot authorize execution.

## Live Endpoint

Endpoint: https://challenge.xer0trust.com

Explore the rest of the repository for the full architecture and additional demos.
