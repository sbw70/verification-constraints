# ESP-LOCAL-008 Firmware

## Purpose

ESP-LOCAL-008 firmware implements the endpoint-side enforcement path for signed target binding and the explicit provisioner used to establish the local one-use authority state before scored execution.

The property under test is:

> A valid provider-issued authority scoped to one endpoint must not become usable at another endpoint.

The endpoint runtime verifies the provider signature and authority semantics, evaluates the signed `device_id` against the local endpoint identity, and rejects a wrong-target authority before persistent authority state is consulted or modified.

For a correctly targeted authority, the runtime continues through local authority-state validation, durable consumption, fresh persistent-state reread, and the PWM execution boundary.

The provider authority model is unchanged. Endpoint firmware may transport, verify, recognize, and enforce provider-issued authority, but cannot originate or enlarge provider authority.

## Repository Layout

The published firmware tree is:

    firmware/
    |-- README.md
    |
    |-- endpoint-runtime/
    |   `-- project/
    |       |-- CMakeLists.txt
    |       |-- partitions.csv
    |       |-- sdkconfig
    |       |
    |       |-- components/
    |       |   `-- monocypher/
    |       |       |-- CMakeLists.txt
    |       |       |-- monocypher.c
    |       |       |-- monocypher.h
    |       |       |-- monocypher-ed25519.c
    |       |       `-- monocypher-ed25519.h
    |       |
    |       `-- main/
    |           |-- CMakeLists.txt
    |           `-- ESP_LOCAL_008_ENDPOINT.c
    |
    `-- provisioner/
        `-- project/
            |-- CMakeLists.txt
            |-- partitions.csv
            |-- sdkconfig
            `-- main/
                |-- CMakeLists.txt
                `-- ESP_LOCAL_008_PROVISIONER.c

The repository publishes the endpoint enforcement implementation, state-record implementation, provisioner, cryptographic dependency, partition definition, and ESP-IDF project configuration.

## Endpoint Hardware

Two Seeed XIAO ESP32-S3 endpoints participated in the final test matrix.

    Servo #1
      device_id: esp32-xiao-servo-01
      IP:        192.168.0.81
      MAC:       1c:db:d4:45:11:e8
      TCP port:  19081
      PWM GPIO:  5

    Servo #2
      device_id: esp32-xiao-servo-02
      IP:        192.168.0.186
      MAC:       1c:db:d4:45:10:a4
      TCP port:  19081
      PWM GPIO:  5

Endpoint identity and MAC address were used to distinguish the two DUTs.

COM-port assignments were bench interfaces and were not treated as endpoint identity.

## Endpoint Runtime

Primary source:

    endpoint-runtime/project/main/ESP_LOCAL_008_ENDPOINT.c

The runtime is derived from the preceding ESP-LOCAL endpoint enforcement path with an explicit target-binding stage added ahead of persistent-state access.

The evaluated request path is:

    receive request
        |
        v
    decode authority and signature
        |
        v
    verify provider Ed25519 signature
        |
        v
    semantic admissibility
        |
        v
    signed target/device_id comparison
        |
        +---- mismatch ----> target_id_mismatch
        |                   no authority-state access
        |                   no PWM command
        |
        v
    SHA-256 authority binding
        |
        v
    persistent-state validation
        |
        v
    exact authority-id match
        |
        v
    UNSPENT check
        |
        v
    durable transition to SPENT
        |
        v
    fresh persistent-state reread
        |
        v
    PWM command boundary
        |
        v
    accepted / executed

The target comparison is therefore performed before the `nuvl_state` partition is opened for the request.

That ordering is the central firmware property tested by ESP-LOCAL-008.

## Provider Trust Anchor

The endpoint verifies provider authority using the trusted Ed25519 public key:

    48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1

The provider private key is not required by the endpoint.

The endpoint cannot generate a valid provider signature from the public trust anchor.

## Semantic Context

ESP-LOCAL-008 advances the signed authority context to:

    esp_local_008

The tested action is:

    move_servo

The tested bounded-use value is:

    max_uses = 1

The signed authority includes the target `device_id`.

Target identity is evaluated separately from the target-agnostic semantic admissibility stage so a valid authority for another endpoint produces an explicit:

    target_id_mismatch

rather than a generic semantic denial.

## Target-Gate Markers

A valid provider-signed authority presented to the wrong endpoint produces the scored sequence:

    008_CLIENT_REQUEST_RECEIVED
    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH
    008_CLIENT_COMPLETE ... result=target_id_mismatch

A wrong-target path must not subsequently emit:

    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The target endpoint's persistent-state image is also compared before and after the presentation.

## Correct-Target Markers

A valid authority presented to its intended endpoint proceeds through:

    008_CLIENT_REQUEST_RECEIVED
    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

A TCP `accepted` response alone is not treated as sufficient evidence.

The final positive cases also require:

- durable SPENT state;
- the expected endpoint serial sequence;
- one independently observed physical control-signal burst.

## Endpoint Build Selector

The endpoint source uses:

    #define ENDPOINT_INSTANCE 1

to select the local identity at build time.

The two configurations are:

    ENDPOINT_INSTANCE 1
      device_id:  esp32-xiao-servo-01
      servo GPIO: 5

    ENDPOINT_INSTANCE 2
      device_id:  esp32-xiao-servo-02
      servo GPIO: 5

The checked-in source snapshot currently contains:

    #define ENDPOINT_INSTANCE 1

A Servo2 build requires the selector value:

    #define ENDPOINT_INSTANCE 2

The selector changes local endpoint identity; it does not change the provider trust anchor or target-binding semantics.

## Historical Source Comments

Some comments in `ESP_LOCAL_008_ENDPOINT.c` still refer to the original planning-stage `AUTH-X` and `AUTH-Y` labels.

The final scored matrix used later frozen authorities:

    Servo1 positive:       AUTH-X3
    Servo2 positive:       AUTH-Y2
    Servo2 wrong-target:   AUTH-X2
    Servo1 wrong-target:   AUTH-Y3

The retained X/Y comments are historical source commentary and do not define the final scored evidence.

The executable endpoint identity selector, frozen authority records, final presenter records, state images, and endpoint logs define the final tested configuration.

## Persistent Authority State

ESP-LOCAL-008 uses a dedicated NVS partition:

    name:   nuvl_state
    type:   data
    subtype:nvs
    offset: 0x110000
    size:   24K / 0x6000

The partition table is:

    nvs,data,nvs,0x9000,24K,
    phy_init,data,phy,0xf000,4K,
    factory,app,factory,0x10000,1M,
    nuvl_state,data,nvs,,24K,

The runtime uses:

    partition: nuvl_state
    namespace: nuvl_auth
    key:       state

The stored record contains:

    uint32_t magic
    uint16_t version
    uint8_t  state
    uint8_t  reserved
    uint8_t  authority_id[32]
    uint32_t crc32

Record size:

    44 bytes

Magic:

    0x4E55564C

Version:

    1

State values:

    UNSPENT = 1
    SPENT   = 2

The state record binds local spend state to one SHA-256 authority ID.

## Durable Consumption

A correctly targeted authority must match the locally provisioned authority ID and must be UNSPENT.

Before the PWM command boundary, the runtime:

1. transitions the authority to SPENT;
2. commits the NVS update;
3. closes and reopens the persistent-state path;
4. performs a fresh reread;
5. validates the record structure, CRC, authority ID, and SPENT state;
6. emits `008_DURABLE_SPENT_REREAD_PASS`;
7. only then crosses `008_PWM_COMMAND_BEGIN`.

This preserves the established consume-before-command ordering used by the ESP-LOCAL test series.

## Raw NVS Evidence

Raw `nuvl_state` partition images are retained under:

    evidence/state/

Because NVS is append/update storage, an earlier UNSPENT record may remain visible in the raw partition after a later SPENT record is committed.

The presence of an older state=1 record is therefore not by itself evidence that the authority remained unspent.

The latest valid record for the authority ID determines the durable state.

## Provisioner

Primary source:

    provisioner/project/main/ESP_LOCAL_008_PROVISIONER.c

The provisioner establishes one local UNSPENT authority-state record for the selected endpoint.

It:

- selects an endpoint configuration at build time;
- binds a frozen authority ID to that endpoint;
- initializes the dedicated `nuvl_state` partition;
- refuses to silently replace an existing authority state;
- writes one UNSPENT record;
- commits the record;
- deinitializes and reinitializes the partition;
- performs a fresh readback;
- validates record structure, authority ID, CRC, and state;
- emits PASS only after durable UNSPENT readback succeeds.

Representative success markers are:

    008_PROVISION_ENDPOINT=<device_id>
    008_PROVISION_LABEL=<authority label>
    008_AUTH_ID=<authority_id>
    008_DURABLE_UNSPENT_VERIFIED
    008_PROVISION_PASS

If existing state is already present, provisioning fails closed rather than silently resetting it.

## Provisioner Build Selector

The provisioner also uses:

    #define ENDPOINT_INSTANCE 1

The final definitions in the source are:

    ENDPOINT_INSTANCE 1
      endpoint:  esp32-xiao-servo-01
      authority: AUTH-X3
      authority_id:
        5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

    ENDPOINT_INSTANCE 2
      endpoint:  esp32-xiao-servo-02
      authority: AUTH-Y2
      authority_id:
        3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519

The checked-in source snapshot currently selects instance 1 / AUTH-X3.

The same source contains the instance 2 / AUTH-Y2 configuration used for Servo2 when built with `ENDPOINT_INSTANCE` set to 2.

## Historical Provisioner Comments

The introductory comment in `ESP_LOCAL_008_PROVISIONER.c` retains earlier references to `AUTH-X` and `AUTH-Y`.

The active preprocessor definitions below that comment contain the final X3/Y2 authority IDs.

The historical comment is retained as source provenance.

The active definitions and scored evidence define the final tested configuration.

## Final Authority Configuration

The final positive authority mappings were:

    Servo #1
      authority: AUTH-X3
      authority_id:
        5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

    Servo #2
      authority: AUTH-Y2
      authority_id:
        3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519

The final wrong-target mappings were:

    AUTH-X2
      signed target: Servo #1
      presented to: Servo #2

    AUTH-Y3
      signed target: Servo #2
      presented to: Servo #1

## Recorded Runtime Build Identities

The exact scored endpoint application binaries were identified during testing by SHA-256.

Servo #1 corrected runtime binary:

    C743FBE3D03BF3267B3BDFE9BD84FFE5D31E5335875F4FFADDD39E705E7A6A7E

Servo #2 corrected runtime binary:

    8CEB6B65C08885173C007D859AEE9F134F6DC97FF2E55518A811AB9E1FC88EE0

The current GitHub firmware tree publishes source and ESP-IDF project material. These tested application binaries are identified by hash but are not present in the current firmware directory.

## Recorded Test-Time Source Configurations

The two endpoint builds were created from the same selector-based implementation with different `ENDPOINT_INSTANCE` values.

Bench-recorded SHA-256 identities for the two test-time source configurations were:

    Servo #1 / ENDPOINT_INSTANCE 1:
    873A15DB09DF51D4A8BF430DF5C11AE51CFCFC31DAEFDA7BFF4A8F27D6DCEED3

    Servo #2 / ENDPOINT_INSTANCE 2:
    DECB8F04A4B7B36CC3366D7302F41E7F76B9F81217548C925CED443FA65CCA0E

These values identify the test-time selector configurations. They are not presented as SHA-256 hashes of two separate source files currently stored in the repository.

The repository contains one selector-based endpoint source file.

## Recorded X3 Provisioner Identity

The final Servo1 AUTH-X3 provisioner source configuration was recorded as:

    SHA-256:
    1917B7CBCB872DE0C1AB9270668B2E6A26F03FCFDCE4925456BD416E6D5A9CAC

The corresponding frozen provisioner application binary was recorded as:

    SHA-256:
    FF68964B8156BEAFAED632B9F6AB4738048CF66EAA07CBA8F466E21E34F29CFC

The frozen binary size was:

    191600 bytes

These values identify the scored bench artifacts. They do not imply that the binary is currently present in the GitHub firmware tree.

## X3 State Transition

For the final Servo1 positive case, the X3 authority state after provisioning and restoration of the endpoint runtime was recorded as:

    SHA-256:
    588C34697B132DF7B82E79BC6A06A2DD973938A446AEFF199726CA5F0F4BEF36

The record was UNSPENT.

After `X3_S1_ACCEPT_001`, the state image was recorded as:

    SHA-256:
    F2193B58041E1BFAFB2DB2A97463C4833AA2EAE196F84102DAB3A26DF6144873

The raw post-run image contains the earlier state=1 record and a later state=2 record for the same authority ID.

## Y2 State Transition

Servo2's Y2 state remained unchanged across the X2 wrong-target denial.

Pre-denial / post-denial SHA-256:

    3CF11DBE7EA19F45E6194451AB2D5B1C94627FAAD6574A9BB566D7BEFC562E76

After the correctly targeted `Y2_S2_ACCEPT_001` execution:

    SHA-256:
    A443EE0C0DEB23DE73A4F08F3A6BE20C5231DCFF131AE4A026C1A3D4DBF1C29B

The positive case therefore changed the locally bound authority state, while the preceding wrong-target case did not.

## Servo1 Wrong-Target State Check

For `Y3_S1_DENY_001`, the Servo1 state images immediately before and after presentation were byte-for-byte identical.

The wrong-target authority was rejected before the persistent-state path and produced no state change.

## GPIO Configuration

The final endpoint runtime uses:

    Servo #1 PWM GPIO: 5
    Servo #2 PWM GPIO: 5

Pre-scored validation identified an incorrect Servo #2 actuator GPIO mapping; the configuration was corrected before scored execution.

Independent witness wiring is separate from the endpoint PWM GPIO number:

    witness GPIO4 -> Servo #2 signal
    witness GPIO5 -> Servo #1 signal

The witness GPIO identifies the witness input channel, not the endpoint's local LEDC GPIO numbering.

## Wi-Fi Configuration

The endpoint source includes:

    #include "local_wifi_config.h"

The real local Wi-Fi credential header is not checked into the repository.

The endpoint runtime reuses the established ESP-LOCAL Wi-Fi macro names:

    ESP_LOCAL_006_WIFI_SSID
    ESP_LOCAL_006_WIFI_PASSWORD

A local reproduction header can be placed at:

    endpoint-runtime/project/main/local_wifi_config.h

with the form:

    #pragma once

    #define ESP_LOCAL_006_WIFI_SSID     "<TEST_WIFI_SSID>"
    #define ESP_LOCAL_006_WIFI_PASSWORD "<TEST_WIFI_PASSWORD>"

The Wi-Fi password is local bench configuration and is not part of the tested authority model.

## Cryptographic Dependency

The endpoint project includes the Monocypher source used for Ed25519 verification:

    components/monocypher/monocypher.c
    components/monocypher/monocypher.h
    components/monocypher/monocypher-ed25519.c
    components/monocypher/monocypher-ed25519.h

The cryptographic verification dependency is therefore included with the endpoint source rather than represented only as an external package reference.

## Build

The endpoint runtime and provisioner are ESP-IDF projects targeting ESP32-S3.

Typical build entry point:

    idf.py build

The endpoint project name is:

    ESP_LOCAL_008_ENDPOINT

The factory application partition begins at:

    0x10000

The dedicated authority-state partition begins at:

    0x110000

Application-only replacement can therefore preserve `nuvl_state` when the state partition is not erased or reflashed.

Exact toolchain versions should be taken from retained build/bench evidence where recorded. The repository does not rely on an unverified claim that every ESP-LOCAL-008 application artifact was built by one exact ESP-IDF version.

## Final Firmware Matrix

| Run | Authority Scope | Endpoint | Firmware Result |
|---|---|---|---|
| `X2_S2_DENY_001` | Servo1 | Servo2 | `target_id_mismatch` before state access |
| `Y3_S1_DENY_001` | Servo2 | Servo1 | `target_id_mismatch` before state access |
| `X3_S1_ACCEPT_001` | Servo1 | Servo1 | target match, durable spend, one PWM execution |
| `Y2_S2_ACCEPT_001` | Servo2 | Servo2 | target match, durable spend, one PWM execution |

The two wrong-target cases produced no physical target-line control signal in the corresponding independent witness capture.

The two correct-target cases crossed one PWM control-signal boundary and were independently observed as one corresponding pulse burst.

## Evidence Model

Firmware log output is not treated as the sole proof of the property.

ESP-LOCAL-008 combines:

- provider-signed frozen authority artifacts;
- provider trust-anchor verification;
- endpoint enforcement markers;
- raw persistent-state images;
- presenter JSON records;
- endpoint serial logs;
- independent RMT witness capture;
- recorded source and binary identities.

For a wrong-target case, a TCP denial alone is insufficient.

For a correct-target case, a TCP acceptance alone is insufficient.

The scored property is established from agreement between the authority scope, endpoint enforcement path, persistent-state evidence, and the independent physical witness.

## Scope

ESP-LOCAL-008 establishes signed endpoint directionality for the tested two-endpoint configuration.

It demonstrates that provider-issued authority bound to one endpoint did not become executable authority at the other endpoint.

It also demonstrates the positive counterpart: correctly targeted authority was accepted, durably consumed, and observed at the physical control-signal boundary once.

ESP-LOCAL-008 does not independently re-run every property established elsewhere in the ESP-LOCAL series, including:

- hostile-relay mutation resistance;
- wrong-provider-key rejection;
- reboot persistence;
- full power-loss persistence;
- malformed-state failure behavior;
- crash-window behavior;
- concurrent-requester contention.

Those properties are covered by their respective ESP-LOCAL test packages.
