# Provider B Final State

This directory contains the final retained local state from Provider B at the end of the MP001 scored campaign.

It records two distinct provider-local facts:

- executions Provider B recorded as completed
- authorization identifiers Provider B had durably consumed

These files are Provider B local evidence. They are not association records and they are not physical-execution witness evidence.

## Files

### `provider_b_execution.jsonl`

Append-only local execution records retained by Provider B.

Each record includes:

- `provider_id`
- `operation_id`
- `authorization_id`
- `local_execution_seq`
- provider-local monotonic time
- provider-local UTC time
- execution result
- record version

The final file contains **13 execution records**.

`local_execution_seq` is local to the running Provider B process. Provider B was restarted during the campaign, so the sequence value resets in the final record.

Provider-local timestamps are evidence from Provider B's own runtime. They are not used to establish globally synchronized chronology across Provider A, Provider B, the intermediary, or the association.

### `provider_b_spent_state.json`

Final durable authorization-consumption state retained by Provider B.

The `spent` object maps each consumed `authorization_id` to its associated authorization nonce.

The final state contains **14 spent authorizations**.

An authorization appearing in this file has been consumed by Provider B and cannot subsequently be treated as unused by that provider runtime.

## Final state

Provider B finished the retained campaign state with:

- **13 local execution records**
- **14 spent authorizations**

The difference is intentional and preserved.

During the initial N05 attempt, the intended Provider-B-unavailable precondition was not actually satisfied. Provider B remained running and consumed the authorization, but no corresponding local execution record was produced.

That attempt was retained as a misfire rather than deleted or normalized.

A fresh authorization was then created for `N05_RETRY_001` after Provider B unavailability was verified, and the retry was scored separately.

Relevant campaign records include:

- `../MP001_SCORECARD.txt`
- `../requester_N05.log`
- `../requester_N05_RETRY_001.log`

## Integrity

The final retained hashes are recorded in `../final_provider_hashes.txt`.

`provider_b_execution.jsonl`

SHA-256:

`da1eba172b0194c71d1ff81960e56be073c7c1c9b170a8bd5a85303c12c4769a`

`provider_b_spent_state.json`

SHA-256:

`84c79f21b91861c377645b85a411158b00bbb8809a097977228e6253ae1c4aab`

These files are also covered by the scored campaign integrity manifest in `../SHA256SUMS.txt`.

## Scope

This directory establishes the final local execution and authorization-consumption state retained by Provider B for MP001.

It does not by itself establish:

- physical actuation
- globally synchronized event ordering
- association verification
- Provider A state
- intermediary behavior
- behavior outside the scored MP001 campaign

Those properties are documented by the corresponding evidence elsewhere in the campaign directory.
