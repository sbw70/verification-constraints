# Provider A Final State

This directory contains the final retained local state from Provider A at the end of the MP001 scored campaign.

It records:

- executions Provider A recorded locally as completed
- authorization identifiers Provider A had durably consumed

These are Provider A local records. They are not association records and they are not physical-execution witness evidence.

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

The sequence value is local to Provider A. Provider-local timestamps are not used to establish a globally synchronized chronology across Provider A, Provider B, the intermediary, or the association.

### `provider_a_spent_state.json`

Final durable authorization-consumption state retained by Provider A.

The `spent` object maps each consumed `authorization_id` to its authorization nonce.

The final state contains **14 spent authorizations**.

An authorization appearing in this file has been consumed by Provider A and is no longer available for a first use by that provider runtime.

## Final state

Provider A finished the scored campaign with:

```text
executions: 14
spent:      14
