# ESP-LOCAL-005 Firmware

This directory contains the ESP-IDF C source used for the ESP-LOCAL-005 endpoint-local persistent-authority test series.

The files in this directory implement the normal runtime, explicit provisioning, persistent-state fault injection, and crash-injection variants used to exercise authority consumption before physical command issuance.

## Contents

### Normal Runtime

`ESP_LOCAL_005_RUNTIME.c`

Implements the standard ESP-LOCAL-005 execution path:

- verify provider Ed25519 signature,
- validate authority semantics,
- validate persistent authority state,
- require matching `UNSPENT` authority,
- transition persistent state to `SPENT`,
- verify persistent `SPENT` state,
- issue the servo PWM command.

### Provisioner

`ESP_LOCAL_005_PROVISIONER.c`

Creates the explicit persistent `UNSPENT` state for the original ESP-LOCAL-005 authority.

Persistent-state absence is not treated as fresh authority by the normal runtime.

### Persistent-State Fault Injection

`ESP_LOCAL_005_CORRUPT_STATE_INJECTOR.c`

Writes a deliberately invalid persistent authority-state record for startup fail-closed testing.

`ESP_LOCAL_005_TRUNCATED_STATE_INJECTOR.c`

Writes a deliberately truncated persistent authority-state blob for wrong-length startup validation testing.

### Authority #4 Crash Variant

`ESP_LOCAL_005_AUTH4_PROVISIONER.c`

Provisions fresh persistent state for Authority #4.

`ESP_LOCAL_005_AUTH4_POSTCOMMIT_CRASH_RUNTIME.c`

Injects a deliberate crash after persistent authority consumption and fresh `SPENT` readback but before PWM command issuance.

### Authority #5 Crash Variant

`ESP_LOCAL_005_AUTH5_PROVISIONER.c`

Provisions fresh persistent state for Authority #5.

`ESP_LOCAL_005_AUTH5_PRECOMMIT_CRASH_RUNTIME.c`

Injects a deliberate crash after the persistent state write and before the explicit `nvs_commit()` call.

## Firmware Role

All runtime variants preserve the same authority model:

Provider authority is established externally.

The endpoint may verify, constrain, consume, and enforce that authority locally.

The endpoint does not independently originate, enlarge, substitute, or regenerate provider authority.

## Related Material

Observed outcomes are documented in:

`../RESULTS.md`

Artifact lineage is documented in:

`../PROVENANCE.md`

Compiled binaries and preserved state captures are stored in:

`../evidence/`

Published artifact hashes are recorded in:

`../SHA256SUMS.txt`
