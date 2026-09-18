# ESP-LOCAL-006 Evidence

This directory contains preserved evidence artifacts associated with the ESP-LOCAL-006 hostile-relay / compromised-forwarder test series.

The material includes relay transaction logs, endpoint and witness terminal transcripts, relay-host baseline information, and raw persistent-state partition captures used to support independent inspection of the completed test matrix.

## Artifact Classes

### Relay-Host Baseline

`ESP_LOCAL_006_PI3_BASELINE.txt`

Preserved baseline information for the Raspberry Pi 3 used as the ESP-LOCAL-006 hostile relay host.

This artifact records the relay-side environment before execution of the scored test matrix.

### Auth1 Relay Transactions

`ESP_LOCAL_006_RELAY_AUTH1.jsonl`

JSONL transaction record for the Authority #1 phase.

The preserved records include the relay mutation and pass-through activity associated with:

- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` enlargement,
- untouched Auth1 positive control,
- replay-related activity,
- transport errors encountered during the test sequence.

Each completed relay record may contain:

- UTC timestamp,
- requester peer,
- relay mode,
- endpoint target,
- ingress byte count,
- egress byte count,
- ingress SHA-256,
- egress SHA-256,
- endpoint response,
- endpoint-response SHA-256.

Error records preserve the corresponding exception type and detail.

The Auth1 relay log contains the complete preserved relay-side sequence, including attempts that were not scored as authorization results because the endpoint validation path was not reached.

### Auth2 Relay Transactions

`ESP_LOCAL_006_RELAY_AUTH2.jsonl`

JSONL transaction record for the Authority #2 phase.

The preserved sequence contains three scored pass-through transactions:

1. wrong-provider signature submission,
2. trusted-provider positive control over the same canonical authority bytes,
3. replay of the consumed trusted-provider request.

For each request, relay ingress and egress hashes are preserved.

Matching ingress and egress hashes establish byte-preserving forwarding at the relay for those pass-through controls.

### Endpoint Terminal Transcript

`ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt`

Curated transcript of terminal output observed from the ESP-LOCAL-006 endpoint during the live test sequence.

The transcript preserves selected endpoint events associated with:

- successful mutation rejection,
- trusted Auth1 acceptance,
- Auth1 replay denial,
- Auth2 runtime startup,
- wrong-provider signature rejection,
- trusted Auth2 acceptance,
- Auth2 replay denial.

The file is explicitly a curated transcript reconstructed from terminal output preserved during the live session.

It is not represented as a raw redirected serial log.

### Independent Witness Transcript

`ESP_LOCAL_006_WITNESS_COM8_CURATED.txt`

Curated transcript of terminal output observed from the independent GPIO4 witness during the live test sequence.

The transcript preserves the measured PWM pulse widths associated with:

- accepted Auth1 execution,
- accepted trusted Auth2 execution,
- replay controls,
- wrong-provider negative control.

The Auth1 witness session recorded:

- 49 servo-valid pulses,
- observed pulse widths from 1998 µs to 2001 µs,
- two isolated 1 µs transients,
- no second servo-valid burst after replay.

The Auth2 witness session recorded:

- 49 servo-valid pulses,
- observed pulse widths from 1999 µs to 2001 µs,
- no PWM burst for the wrong-provider submission,
- no second servo-valid burst after trusted replay.

The transcript is explicitly curated and is not represented as a raw redirected serial log.

The witness establishes observed electrical PWM issuance on the monitored command line. It does not independently establish guaranteed mechanical servo movement.

## Persistent-State Captures

The `.bin` files in this directory are raw reads of the dedicated ESP32-S3 `nuvl_state` partition.

The tested partition was:

```text
label:   nuvl_state
offset:  0x110000
size:    0x6000
length:  24576 bytes
```

These files are binary partition captures and should not be interpreted as text files.

### `ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin`

Final persistent-state partition capture after Authority #1 had been accepted and consumed.

This file preserves the post-Auth1 state associated with the mutation, positive-control, and replay sequence.

### `ESP_LOCAL_006_AUTH2_UNSPENT.bin`

Persistent-state partition capture after Authority #2 provisioning and before the wrong-provider / trusted-provider control sequence.

The parsed record showed:

```text
state = 01 / UNSPENT
authority_id =
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
```

The NVS page CRC32 was reported as valid.

### `ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin`

Final persistent-state partition capture after trusted Authority #2 execution and replay testing.

The parsed record showed:

```text
state = 02 / SPENT
authority_id =
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
```

The NVS page CRC32 was reported as valid.

## State-Transition Interpretation

The pre-test and post-test Auth2 partition images have different SHA-256 values.

That difference establishes that the partition images are not identical.

The partition-hash difference alone does not establish that only the authority-state field changed.

The specific observed transition is supported by the parsed state records:

```text
UNSPENT = 01
SPENT   = 02
```

together with:

- the preserved Authority #2 identifier,
- valid NVS page CRC32 results,
- endpoint execution logs,
- replay denial,
- independent witness output.

## Curated Versus Original Evidence

The relay JSONL files, raw NVS partition captures, and Pi baseline are preserved test artifacts.

The COM15 endpoint and COM8 witness text files are curated derivatives created from terminal output preserved during the live test session.

They are intentionally labeled `CURATED` in the filenames and contents.

A curated derivative does not inherit the hash of any original terminal stream or session that was not captured directly to file.

Its SHA-256 identifies the published curated artifact itself.

## Evidence Relationships

The evidence set supports correlation across four distinct observation points:

```text
provider-issued request
        ↓
relay transaction record
        ↓
endpoint decision record
        ↓
persistent authority state
        ↓
independent PWM witness
```

No single artifact is treated as sufficient by itself to establish the entire execution result.

The relay logs establish request handling at the intermediary.

The endpoint transcript preserves observed validation and execution decisions.

The persistent-state captures preserve authority-consumption state.

The witness transcript preserves independent electrical observation of PWM command issuance.

## Transport Anomaly

The Auth1 relay record includes timeout behavior encountered during the `mutate-max-uses` phase while the Pi-to-endpoint path exhibited elevated latency.

Those timeout attempts were not treated as successful authorization denials merely because no command occurred.

The case was rerun with a longer transport timeout until the mutated request reached the endpoint and exercised the endpoint validation path.

Only the completed endpoint rejection was scored as the authorization result.

The complete interpretation of this anomaly is documented in:

```text
../RESULTS.md
```

## Related Material

Provider authority artifacts are stored in:

```text
../provider/
```

The hostile relay implementation is stored in:

```text
../relay/
```

The independent witness implementation is stored in:

```text
../witness/
```

Observed test outcomes are documented in:

```text
../RESULTS.md
```

Artifact lineage and publication relationships are documented in:

```text
../PROVENANCE.md
```

Published artifact hashes are recorded in:

```text
../SHA256SUMS.txt
```
