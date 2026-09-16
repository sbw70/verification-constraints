# ESP-LOCAL-005 Evidence

This directory contains preserved artifacts associated with the ESP-LOCAL-005 test series.

The material includes compiled firmware images, frozen authority metadata, authority-specific source variants, persistent-state captures, cryptographic gate artifacts, and fault-injection outputs used to support reproduction and independent inspection.

## Artifact Classes

### Ed25519 Gate

`ESP_LOCAL_005_ED25519_GATE.c`

Source for the native Ed25519 verification gate used before the persistent-authority runtime tests.

`ESP_LOCAL_005_ED25519_GATE.bin`

Compiled application image for the gate test.

### Original Runtime

`ESP_LOCAL_005_RUNTIME.bin`

Compiled normal ESP-LOCAL-005 runtime associated with the original authority.

`ESP_LOCAL_005_ORIGINAL_SPENT_NUVL_STATE.bin`

Raw persistent-state partition capture after the original authority had been consumed.

### Authority #2

The Authority #2 artifact set includes:

- authority metadata,
- provisioner source,
- provisioner binary,
- runtime source,
- runtime binary,
- resulting spent-state partition capture.

Files use the `ESP_LOCAL_005_AUTH2_*` prefix.

### Authority #3

The Authority #3 artifact set includes:

- authority metadata,
- provisioner source,
- provisioner binary,
- runtime source,
- runtime binary,
- resulting spent-state partition capture.

Files use the `ESP_LOCAL_005_AUTH3_*` prefix.

Authority #3 was used with the independent witness implementation stored in `../witness/`.

### Corrupt Persistent State

`ESP_LOCAL_005_CORRUPT_STATE_INJECTOR.bin`

Compiled injector used to create the corrupt persistent-state condition.

`ESP_LOCAL_005_CORRUPT_STATE_NUVL_STATE.bin`

Raw persistent-state partition capture containing the deliberately invalid record.

The corresponding injector source is stored in `../firmware/`.

### Truncated Persistent State

`ESP_LOCAL_005_TRUNCATED_STATE_INJECTOR.bin`

Compiled injector used to create the truncated persistent-state condition.

`ESP_LOCAL_005_TRUNCATED_STATE_NUVL_STATE.bin`

Raw persistent-state partition capture containing the deliberately truncated record.

The corresponding injector source is stored in `../firmware/`.

### Authority #4

The Authority #4 artifact set contains the material associated with the deliberate post-consumption / pre-PWM crash case.

Files include:

- authority metadata,
- provisioner binary,
- crash-runtime binary,
- resulting spent-state partition capture.

The corresponding source files are stored in `../firmware/`.

### Authority #5

The Authority #5 artifact set contains the material associated with the deliberate crash after the persistent-state write and before the explicit `nvs_commit()` call.

Files include:

- authority metadata,
- provisioner binary,
- crash-runtime binary,
- resulting persistent-state partition capture.

The corresponding source files are stored in `../firmware/`.

## Binary State Captures

Files ending in `_NUVL_STATE.bin` are raw binary reads of the dedicated ESP32-S3 persistent-state partition.

They are preserved as binary evidence and should not be interpreted as text files.

The tested partition was:

- label: `nuvl_state`
- offset: `0x110000`
- size: `0x6000`
- length: `24576` bytes

These captures preserve the storage condition associated with specific test cases.

## Compiled Application Images

Application `.bin` files are compiled ESP32-S3 firmware images retained alongside the corresponding source where applicable.

They are preserved separately because they represent the executable artifacts used during the test series.

## Authority Metadata

Authority `.txt` files preserve the provider-issued material associated with individual test cases, including:

- nonce,
- canonical authority representation,
- authority identifier,
- provider signature.

Each fresh authority represents a distinct test instance.

Previously consumed authorities are retained as evidence rather than reset and reused as fresh authority.

## Related Material

Endpoint and fault-injection source is stored in:

`../firmware/`

Independent witness source is stored in:

`../witness/`

Provider test key material is stored in:

`../provider/`

Observed outcomes are documented in:

`../RESULTS.md`

Artifact lineage is documented in:

`../PROVENANCE.md`

Published artifact hashes are recorded in:

`../SHA256SUMS.txt`
