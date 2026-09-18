# ESP-LOCAL-006 Evidence

This directory contains preserved evidence artifacts associated with the ESP-LOCAL-006 hostile-relay / compromised-forwarder test series.

The material includes:

- relay transaction logs,
- endpoint and witness terminal transcripts,
- relay-host baseline information,
- raw persistent-state partition captures,
- the preserved tested endpoint runtime binary,
- the preserved Authority #1 provisioner binary,
- the preserved Authority #2 provisioner binary.

The evidence set is intended to support correlation across provider artifacts, relay handling, endpoint decisions, persistent authority state, and independent physical-command observation.

## Artifact Classes

### Relay-Host Baseline

`ESP_LOCAL_006_PI3_BASELINE.txt`

Preserved baseline information for the Raspberry Pi 3 used as the ESP-LOCAL-006 hostile relay host.

This artifact records the relay-side environment before execution of the scored test matrix.

Original SHA-256:

```text
14a18fc971b79cb479751e88ad39bde3391c0d40bdab49d7d40becd40b9e49d5
```

### Auth1 Relay Transactions

`ESP_LOCAL_006_RELAY_AUTH1.jsonl`

JSONL transaction record for the Authority #1 phase.

The preserved relay-side sequence includes activity associated with:

- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` enlargement,
- untouched Auth1 positive control,
- replay-related activity,
- transport failures encountered during the test sequence.

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

Error records preserve corresponding exception information.

The Auth1 relay file contains eight preserved records.

Original frozen SHA-256:

```text
ccac98462da0708a463ecc1328a5c01cd0b77f0566e1260f9e70237b0f43b659
```

The file includes scored authority transactions plus non-authority probe/connectivity records.

Empty probes are not treated as scored authority attempts.

### Auth2 Relay Transactions

`ESP_LOCAL_006_RELAY_AUTH2.jsonl`

JSONL transaction record for the Authority #2 phase.

The preserved sequence contains three pass-through transactions:

1. wrong-provider signature submission,
2. trusted-provider positive control over the same canonical authority bytes,
3. replay of the consumed trusted-provider request.

For each request, relay ingress and egress hashes are preserved.

Matching ingress and egress hashes establish byte-preserving forwarding at the relay for those pass-through controls.

Original frozen SHA-256:

```text
27a63a71289a49e9b44df57acce8a065d4f1cba2a5b697e4314b4cbf2982a0da
```

## Endpoint Terminal Transcript

`ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt`

Curated transcript of terminal output observed from the ESP-LOCAL-006 endpoint during the live test sequence.

The transcript preserves selected events associated with:

- mutation rejection,
- trusted Auth1 acceptance,
- Auth1 replay denial,
- Auth2 runtime startup,
- wrong-provider signature rejection,
- trusted Auth2 acceptance,
- Auth2 replay denial.

The file is a curated derivative reconstructed from preserved interactive terminal output.

It is not represented as a raw redirected serial log.

Publication-stage SHA-256:

```text
17d7c4f5c1c8aff3bd5beac42116d92ed7b7c431d4bc78fac10bb12b909524ca
```

## Independent Witness Transcript

`ESP_LOCAL_006_WITNESS_COM8_CURATED.txt`

Curated transcript of terminal output observed from the independent GPIO4 witness during the live test sequence.

The transcript preserves measured PWM pulse widths associated with:

- accepted Auth1 execution,
- accepted trusted Auth2 execution,
- replay controls,
- wrong-provider negative control.

The Auth1 witness session preserved:

```text
49 servo-valid pulses
observed pulse widths: 1998–2001 µs
two isolated 1 µs transients
no second servo-valid replay burst
```

The Auth2 witness session preserved:

```text
49 servo-valid pulses
observed pulse widths: 1999–2001 µs
no servo-valid PWM burst for wrong-provider submission
no second servo-valid replay burst
```

The isolated `1 µs` Auth1 observations are retained in the evidence rather than removed.

They did not form a servo-valid PWM burst.

The transcript is a curated derivative and is not represented as a raw redirected serial log.

Publication-stage SHA-256:

```text
5b768366307449d2c6694a15a50c271b2ccc217fa7c0aee0ba9f451ee209c378
```

The witness establishes observed electrical PWM issuance on the monitored command line.

It does not independently establish guaranteed mechanical servo movement.

## Persistent-State Captures

The authority-state `.bin` files are raw reads of the dedicated ESP32-S3 `nuvl_state` partition.

Tested partition:

```text
label:   nuvl_state
offset:  0x110000
size:    0x6000
length:  24576 bytes
```

These files are raw binary partition images and should not be interpreted as text files.

### `ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin`

Final persistent-state partition capture after Authority #1 had been accepted and consumed.

The parsed record identified Authority #1 and showed:

```text
state = SPENT
```

SHA-256:

```text
6cd54795b1a346e8c4c87a0ecd044bc64025e49ba55d2f170e9b03ff74306c9f
```

### `ESP_LOCAL_006_AUTH2_UNSPENT.bin`

Persistent-state partition capture after Authority #2 provisioning and before the wrong-provider / trusted-provider control sequence.

Parsed record:

```text
state = 01 / UNSPENT

authority_id =
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

NVS page CRC32 = OK
```

SHA-256:

```text
7529911ee67a9702f2769bb5afdcaf40481bf3c8e601f0e508baa62478f4d80c
```

### `ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin`

Final persistent-state partition capture after trusted Authority #2 execution and replay testing.

Parsed record:

```text
state = 02 / SPENT

authority_id =
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

NVS page CRC32 = OK
```

SHA-256:

```text
f807bc6493e7d2f2ce33eb72a550e5f9eca2597c3dd83ee9ab0d60e721ea528c
```

## State-Transition Interpretation

The pre-test and final Authority #2 partition images have different SHA-256 values.

That establishes that the complete binary images differ.

The hash difference alone does not establish that only the authority-state field changed.

The specific observed transition is supported by:

```text
UNSPENT = 01
SPENT   = 02
```

together with:

- the preserved Authority #2 identifier,
- valid NVS page CRC32 results,
- endpoint execution observations,
- replay denial,
- independent witness output.

## Preserved Tested Runtime Binary

`ESP_LOCAL_006_RUNTIME.bin`

This is the preserved endpoint application binary corresponding to the runtime used during the scored ESP-LOCAL-006 hostile-relay matrix.

Recorded tested SHA-256:

```text
21376cdd12d63d2f0e8362c969c7268be56a701ecb3c78bac712564d5fbe5e75
```

Corresponding published source:

```text
../firmware/main/ESP_LOCAL_006.c
```

Recorded tested source SHA-256:

```text
4bd962535c61c17ad093973dbb720a99cd709d626d3e9eeff1ad51b6e6e6aaff
```

The binary was recovered from the original local build output and matched the previously recorded tested-runtime SHA-256.

It is therefore preserved as the tested application binary rather than represented as a later reproduction build.

## Preserved Authority #1 Provisioner Binary

`ESP_LOCAL_006_PROVISIONER.bin`

This is the preserved Authority #1 provisioning application used to establish the Authority #1 `UNSPENT` persistent record.

Recorded tested SHA-256:

```text
de134f4c8b69e5b8627b952098d601d769fcc4de2f27f9d4cc517f12837675fc
```

Corresponding published source:

```text
../firmware/main/ESP_LOCAL_006_PROVISIONER.c
```

Recorded source SHA-256:

```text
4f461509b5a17f333f43a58f536313cd2647a630aab5a873ca7c7e116a8f04bb
```

## Preserved Authority #2 Provisioner Binary

`ESP_LOCAL_006_AUTH2_PROVISIONER.bin`

This is the preserved Authority #2 provisioning application used to establish the Authority #2 `UNSPENT` persistent record.

Recorded tested SHA-256:

```text
d465219f6460dee4a69381221f93ede09bd2d82c67025425b2b5e9515864c0d8
```

Corresponding published source:

```text
../firmware/main/ESP_LOCAL_006_AUTH2_PROVISIONER.c
```

Recorded source SHA-256:

```text
eff601f71e71db9aed8fc6e6849a4cd6db238cb2f3faed75f14e4be52b2e3f2c
```

## Tested Binary Versus Reproduction Build

The three application binaries in this directory are preserved tested binaries:

```text
ESP_LOCAL_006_RUNTIME.bin
ESP_LOCAL_006_PROVISIONER.bin
ESP_LOCAL_006_AUTH2_PROVISIONER.bin
```

A later binary rebuilt from the published source is a reproduction build unless its SHA-256 exactly matches the corresponding preserved tested binary.

Compiler, ESP-IDF, dependency, configuration, or build-environment differences may produce a different binary even when application behavior is functionally equivalent.

## Spend-Before-Command Evidence Relationship

The published endpoint implementation and preserved endpoint observations establish the following accepted-request ordering:

```text
trusted signature valid
        ↓
semantic admissibility
        ↓
authority-id binding
        ↓
persistent state valid
        ↓
UNSPENT
        ↓
write SPENT
        ↓
nvs_commit
        ↓
nvs_close
        ↓
nvs_flash_deinit_partition
        ↓
nvs_flash_init_partition
        ↓
fresh reread
        ↓
same authority-id + SPENT
        ↓
006_DURABLE_SPENT_REREAD_PASS
        ↓
PWM command
```

The post-commit reread is performed after closing the NVS handle and deinitializing and reinitializing the authority partition.

This is stronger than a same-handle cached read.

It does not independently establish survival across every possible immediate power-loss point or resolve the exact physical ESP-IDF/NVS persistence boundary.

Those limitations remain documented separately in the ESP-LOCAL-005 persistence work.

## Curated Versus Original Evidence

The following are preserved test artifacts:

```text
ESP_LOCAL_006_RELAY_AUTH1.jsonl
ESP_LOCAL_006_RELAY_AUTH2.jsonl
ESP_LOCAL_006_PI3_BASELINE.txt
ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin
ESP_LOCAL_006_AUTH2_UNSPENT.bin
ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin
ESP_LOCAL_006_RUNTIME.bin
ESP_LOCAL_006_PROVISIONER.bin
ESP_LOCAL_006_AUTH2_PROVISIONER.bin
```

The following are curated derivatives:

```text
ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt
ESP_LOCAL_006_WITNESS_COM8_CURATED.txt
```

The curated files were assembled from terminal output preserved during the interactive live sessions.

They are intentionally labeled `CURATED`.

A curated derivative does not inherit the hash of an original terminal stream that was not captured directly to file.

Its SHA-256 identifies the published curated artifact itself.

## Evidence Relationships

The evidence set supports correlation across distinct observation layers:

```text
provider-issued authority
        ↓
relay transaction record
        ↓
endpoint decision observation
        ↓
persistent authority state
        ↓
independent PWM witness
```

The source and tested binaries add a separate implementation-verification layer:

```text
published source
        ↓
recorded tested source identity
        ↓
preserved tested application binary
        ↓
observed runtime behavior
```

No single artifact is treated as sufficient by itself to establish the complete result.

The relay logs establish intermediary handling.

The endpoint transcript preserves observed validation and execution decisions.

The persistent-state captures preserve authority-consumption state.

The witness transcript preserves independent electrical observation of PWM command issuance.

The published source permits inspection of the validation and spend-before-command path.

The preserved application binaries identify the exact tested application images.

## Transport Anomaly

The Auth1 relay evidence includes timeout behavior encountered during the `mutate-max-uses` phase while the Pi-to-endpoint path exhibited elevated latency.

Those timeout attempts were not treated as successful authorization denials merely because no command occurred.

The case was rerun with a longer transport timeout until the mutated request reached the endpoint and exercised the endpoint validation path.

Only the completed endpoint rejection was scored as the authorization result.

A transport timeout, lack of response, dropped request, or delivery failure is not treated as equivalent to an endpoint authorization denial.

The complete interpretation is documented in:

```text
../RESULTS.md
```

## Evidence Limitations

The independent witness establishes observed electrical PWM issuance, not guaranteed mechanical servo movement.

The curated serial transcripts are not original raw redirected terminal captures.

The partition-image hash differences establish binary-image differences but do not independently identify which logical field changed.

The runtime post-commit reread does not independently establish persistence across every possible immediate-power-loss boundary.

The evidence does not establish resistance to:

- trusted provider private-key compromise,
- complete endpoint compromise,
- denial-of-service behavior,
- secure-routing failures,
- persistent-state rollback,
- physical storage tampering,
- absence of trusted time.

## Related Material

Provider authority artifacts:

```text
../provider/
```

Published endpoint and provisioner source:

```text
../firmware/
```

Hostile relay implementation:

```text
../relay/
```

Independent witness implementation:

```text
../witness/
```

Observed test outcomes:

```text
../RESULTS.md
```

Artifact lineage and publication relationships:

```text
../PROVENANCE.md
```

Published artifact hashes:

```text
../SHA256SUMS.txt
```

`SHA256SUMS.txt` is regenerated after the final publication tree and documentation are complete.
