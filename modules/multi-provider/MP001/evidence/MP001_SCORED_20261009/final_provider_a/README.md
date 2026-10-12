# Provider A Final State

This directory contains the final retained local state from Provider A at the end of the MP001 scored campaign.

It records two provider-local facts:

- executions Provider A recorded as completed
- authorization identifiers Provider A had durably consumed

These files are Provider A local evidence. They are not association records and they are not physical-execution witness evidence.

## Files

### `provider_a_execution.jsonl`

Append-only local execution records retained by Provider A.

Each record includes:

- `provider_id`
- `operation_id`
- `authorization_id`
- `local_execution_seq`
- provider-local monotonic time
- provider-local UTC time
- execution result
- record version

The final file contains **14 execution records**.

`local_execution_seq` is local to Provider A.

Provider-local timestamps are evidence from Provider A's own runtime. They are not used to establish globally synchronized chronology across Provider A, Provider B, the intermediary, or the association.

### `provider_a_spent_state.json`

Final durable authorization-consumption state retained by Provider A.

The `spent` object maps each consumed `authorization_id` to its associated authorization nonce.

The final state contains **14 spent authorizations**.

An authorization appearing in this file has been consumed by Provider A and cannot subsequently be treated as unused by that provider runtime.

## Final state

Provider A finished the retained campaign state with:

- **14 local execution records**
- **14 spent authorizations**

The counts match.

Provider A executed during both the initial N05 attempt and the later N05 retry because Provider A remained available in both cases.

The N05 scoring issue concerned the intended unavailability of Provider B. The initial attempt was retained as a misfire rather than deleted, and the retry was performed with fresh authorization after Provider B unavailability was verified.

Relevant campaign records include:

- `../MP001_SCORECARD.txt`
- `../requester_N05.log`
- `../requester_N05_RETRY_001.log`

## Integrity

The final retained hashes are recorded in `../final_provider_hashes.txt`.

`provider_a_execution.jsonl`

SHA-256:

`9cd2b26247196d867f5b1fd8cca81aacff780a53f7f0885c352a14ed4f1edbf4`

`provider_a_spent_state.json`

SHA-256:

`88d2a5a6047a3748227ae71ade63a4531af81e2d2f291c8623ac928b8ea4c550`

These files are also covered by the scored campaign integrity manifest in `../SHA256SUMS.txt`.

## Scope

This directory establishes the final local execution and authorization-consumption state retained by Provider A for MP001.

It does not by itself establish:

- physical actuation
- globally synchronized event ordering
- association verification
- Provider B state
- intermediary behavior
- behavior outside the scored MP001 campaign

Those properties are documented by the corresponding evidence elsewhere in the campaign directory.
