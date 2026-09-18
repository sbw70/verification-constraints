# ESP-LOCAL-006 Firmware

This directory contains the endpoint implementation and build material associated with the scored ESP-LOCAL-006 hostile-relay test.

Unlike the initial publication package, the tested endpoint implementation is included so that the recognition, authority-binding, persistent-consumption, and physical-command ordering can be inspected directly.

## Published Implementation

The endpoint implementation consists of three authority-specific application sources:

```text
main/ESP_LOCAL_006.c
main/ESP_LOCAL_006_PROVISIONER.c
main/ESP_LOCAL_006_AUTH2_PROVISIONER.c
```

The corresponding preserved application binaries are published under:

```text
../evidence/ESP_LOCAL_006_RUNTIME.bin
../evidence/ESP_LOCAL_006_PROVISIONER.bin
../evidence/ESP_LOCAL_006_AUTH2_PROVISIONER.bin
```

## Tested Source and Binary Identities

### Endpoint Runtime

Source:

```text
main/ESP_LOCAL_006.c
```

SHA-256:

```text
4bd962535c61c17ad093973dbb720a99cd709d626d3e9eeff1ad51b6e6e6aaff
```

Preserved tested application binary:

```text
../evidence/ESP_LOCAL_006_RUNTIME.bin
```

SHA-256:

```text
21376cdd12d63d2f0e8362c969c7268be56a701ecb3c78bac712564d5fbe5e75
```

### Authority #1 Provisioner

Source:

```text
main/ESP_LOCAL_006_PROVISIONER.c
```

SHA-256:

```text
4f461509b5a17f333f43a58f536313cd2647a630aab5a873ca7c7e116a8f04bb
```

Preserved tested application binary:

```text
../evidence/ESP_LOCAL_006_PROVISIONER.bin
```

SHA-256:

```text
de134f4c8b69e5b8627b952098d601d769fcc4de2f27f9d4cc517f12837675fc
```

### Authority #2 Provisioner

Source:

```text
main/ESP_LOCAL_006_AUTH2_PROVISIONER.c
```

SHA-256:

```text
eff601f71e71db9aed8fc6e6849a4cd6db238cb2f3faed75f14e4be52b2e3f2c
```

Preserved tested application binary:

```text
../evidence/ESP_LOCAL_006_AUTH2_PROVISIONER.bin
```

SHA-256:

```text
d465219f6460dee4a69381221f93ede09bd2d82c67025425b2b5e9515864c0d8
```

## Endpoint Runtime

`ESP_LOCAL_006.c` implements the network-facing endpoint used during the scored hostile-relay matrix.

Its evaluation path is:

```text
receive relay envelope
        ↓
strict envelope decoding
        ↓
provider Ed25519 verification
        ↓
semantic admissibility
        ↓
SHA-256 authority identifier
        ↓
persistent-state validation
        ↓
exact authority-id match
        ↓
UNSPENT check
        ↓
SPENT transition
        ↓
post-commit partition reinitialization and reread
        ↓
PWM command
```

The endpoint does not contain provider private signing material.

It recognizes authority through the configured provider public key and enforces authority that has already been established externally.

## Semantic Bounds

The runtime accepts authority in the canonical form:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "<32 lowercase hexadecimal characters>"
}
```

The nonce may vary between fresh provider-issued authorities.

The remaining authority-bearing fields are fixed by the endpoint admissibility constraint used in this test.

A valid provider signature alone is not sufficient for execution.

The signed authority must also:

- satisfy the configured semantic bounds,
- hash to the authority identifier stored in persistent state,
- correspond to a structurally valid persistent record,
- remain `UNSPENT`.

## Persistent State

The dedicated authority-state partition is defined in:

```text
partitions.csv
```

Published layout:

```text
# Name, Type, SubType, Offset, Size, Flags
nvs,data,nvs,0x9000,24K,
phy_init,data,phy,0xf000,4K,
factory,app,factory,0x10000,1M,
nuvl_state,data,nvs,,24K,
```

With the tested layout, `nuvl_state` begins at generated offset:

```text
0x110000
```

and has length:

```text
0x6000
24576 bytes
```

The authority record contains:

```text
magic
version
state
reserved
authority_id[32]
crc32
```

with a total record size of 44 bytes.

Recognized state values are:

```text
UNSPENT = 1
SPENT   = 2
```

Missing, malformed, corrupt, or otherwise invalid authority state is not converted into fresh authority.

## Provisioners

The provisioners explicitly establish an `UNSPENT` record for one provider-issued authority identifier.

They refuse provisioning if an existing authority-state record is already present.

They do not treat either an existing `UNSPENT` or existing `SPENT` record as permission to overwrite the state with a new authority.

After writing the new record, the provisioner:

```text
nvs_set_blob
        ↓
nvs_commit
        ↓
nvs_close
        ↓
nvs_flash_deinit_partition
        ↓
nvs_flash_init_partition
        ↓
fresh read
        ↓
record validation
        ↓
require UNSPENT
```

Only after that sequence does provisioning report success.

## Build Environment

The tested project was built with:

```text
ESP-IDF v6.1
target: ESP32-S3
```

The exact tested ESP-IDF configuration is published as:

```text
sdkconfig
```

The project-level CMake definition is published as:

```text
CMakeLists.txt
```

## Target-Specific Main CMake Configuration

The local ESP-IDF project used the `main/CMakeLists.txt` source selector to build different application images during the test sequence.

The final retained local `main/CMakeLists.txt` corresponds to the Authority #2 provisioner and is preserved as:

```text
main/CMakeLists.AUTH2_TESTED.txt
```

It contains:

```cmake
idf_component_register(
    SRCS
        "ESP_LOCAL_006_AUTH2_PROVISIONER.c"
    INCLUDE_DIRS
        "."
    PRIV_REQUIRES
        nvs_flash
)
```

That file is preserved as the final tested project state and is not represented as the build selector for the runtime or Authority #1 provisioner.

For reproduction, an application source must be selected explicitly.

### Authority #1 Provisioner

```cmake
idf_component_register(
    SRCS
        "ESP_LOCAL_006_PROVISIONER.c"
    INCLUDE_DIRS
        "."
    PRIV_REQUIRES
        nvs_flash
)
```

### Authority #2 Provisioner

```cmake
idf_component_register(
    SRCS
        "ESP_LOCAL_006_AUTH2_PROVISIONER.c"
    INCLUDE_DIRS
        "."
    PRIV_REQUIRES
        nvs_flash
)
```

### Endpoint Runtime

The endpoint runtime additionally requires the ESP-IDF networking, NVS, cryptographic, and local Monocypher components used by `ESP_LOCAL_006.c`.

A reproduction build should declare dependencies required by the published source rather than treating `CMakeLists.AUTH2_TESTED.txt` as the runtime build selector.

Any publication-created runtime build selector should be identified as a reproduction helper rather than represented as an original preserved test-time artifact unless its byte-identical test-time form is independently recovered.

## Wi-Fi Configuration

The tested runtime included a local header:

```text
local_wifi_config.h
```

containing the test SSID and Wi-Fi password.

That original file is intentionally not published because it contains local network credentials.

Instead, the publication contains:

```text
main/local_wifi_config.example.h
```

with placeholder values:

```c
#pragma once

#define ESP_LOCAL_006_WIFI_SSID     "<TEST_WIFI_SSID>"
#define ESP_LOCAL_006_WIFI_PASSWORD "<TEST_WIFI_PASSWORD>"
```

For reproduction, create:

```text
main/local_wifi_config.h
```

from that template and supply the test-network credentials appropriate to the reproduction environment.

The sanitized template is a publication derivative and does not inherit the SHA-256 of the original credential-bearing file.

## Cryptographic Dependency

ESP-LOCAL-006 uses the same Monocypher Ed25519 implementation previously used in the ESP-LOCAL series.

Published source identities:

```text
monocypher.c
f1f838cdd483bdebe0df0ff5c5ed60535e496f769c6a2f933ac4c0b114207123

monocypher.h
fcaf6ed771358bb4f40fba016f6518ae86ec02b1b877d2cc35ad92d3a26fd7b3

monocypher-ed25519.c
ce0d2f8e32ca8f66398ba5b3456cc74327c3eff14e7b950ce7d57be9025cc453

monocypher-ed25519.h
3a3035181f991a158d0e1c7567258f0bae8ba0f1f23c5512b4a1db1b3c9730ce
```

The component-level CMake definition is also published.

## Tested Binary Versus Reproduction Build

The binaries under `../evidence/` are preserved application images from the completed ESP-LOCAL-006 test sequence.

A binary rebuilt later from the published source is a reproduction build.

It should not be represented as the original tested binary unless its SHA-256 exactly matches the corresponding preserved tested artifact.

Compiler, ESP-IDF, configuration, component, or build-environment differences may produce a different binary even when application behavior is equivalent.

## Publication Scope

The firmware publication exposes the implementation used by ESP-LOCAL-006 so that the authority-recognition and enforcement path can be inspected directly.

Publication of the implementation does not broaden the result beyond the tested configuration.

Observed test outcomes are documented in:

```text
../RESULTS.md
```

Artifact lineage is documented in:

```text
../PROVENANCE.md
```

Published artifact integrity is documented in:

```text
../SHA256SUMS.txt
```
