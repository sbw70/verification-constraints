# Provider B Final State

This directory contains the final retained local state from Provider B at the end of the MP001 scored campaign.

It records two different things:

- executions that Provider B recorded locally as completed
- authorization identifiers that Provider B had durably consumed

These files are provider-local evidence. They are not association records and they are not physical-execution witness evidence.

## Files

### `provider_b_execution.jsonl`

Append-only local execution records retained by Provider B.

Each record identifies:

- `provider_id`
- `operation_id`
- `authorization_id`
- `local_execution_seq`
- provider-local monotonic time
- provider-local UTC time
- execution result
- record version

The final file contains **13 execution records**.

`local_execution_seq` is local to the running Provider B process. It is not a campaign-wide sequence number. Provider B was restarted during the campaign, so the sequence value resets in the final record.

Provider-local timestamps are evidence from Provider B's own runtime. They are not used to establish a globally synchronized chronology across providers or the association.

### `provider_b_spent_state.json`

Final durable authorization-consumption state retained by Provider B.

The `spent` object maps each consumed `authorization_id` to its associated authorization nonce.

The final state contains **14 spent authorizations**.

An authorization appearing in this file has been consumed by Provider B and cannot be treated as unused by that provider runtime.

## Why executions and spent authorizations differ

The final counts are intentionally not equal:

```text
Provider B executions: 13
Provider B spent:      14
