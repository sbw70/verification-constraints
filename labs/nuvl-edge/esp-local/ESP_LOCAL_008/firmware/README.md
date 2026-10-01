# ESP-LOCAL-008 Firmware

## Purpose

The ESP-LOCAL-008 firmware implements the endpoint side of the signed target-binding test and the explicit authority-state provisioner used to prepare the endpoints for scored execution.

ESP-LOCAL-008 tests one narrow property:

> A valid provider-issued authority scoped to one endpoint must not become usable at another endpoint.

The endpoint runtime verifies the provider signature and authority semantics, compares the signed `device_id` with the local endpoint identity, and rejects a wrong-target authority before persistent authority state is consulted or modified.

For a correctly targeted authority, the runtime continues through local authority-state validation, durable consumption, fresh state reread, and the physical PWM command boundary.

The provider model is unchanged. Endpoint firmware may transport, verify, recognize, and enforce provider-issued authority, but it cannot originate or enlarge provider authority.

## Layout

    firmware/
    |-- README.md
    |
    |-- endpoint-runtime/
    |   `-- project/
    |       |-- CMakeLists.txt
    |       |-- partitions.csv
    |       |-- sdkconfig*
    |       `-- main/
    |           |-- CMakeLists.txt
    |           `-- <endpoint runtime source>
    |
    `-- provisioner/
        `-- project/
            |-- CMakeLists.txt
            |-- partitions.csv
            |-- sdkconfig*
            `-- main/
                |-- CMakeLists.txt
                `-- ESP_LOCAL_008_PROVISIONER.c

Build-output directories are not required for source review. Frozen binaries used during testing are identified by SHA-256 in the repository evidence and hash records.

## Endpoint Identities

Two XIAO ESP32-S3 endpoints were used.

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

Hardware identity was established from the endpoint identity and MAC address. COM-port assignments were treated only as bench interfaces.

## Endpoint Runtime

The endpoint runtime accepts one authority request over TCP and evaluates it through an ordered enforcement path.

The scored path is:

    request received
        |
        v
    provider signature verification
        |
        v
    semantic admissibility
        |
        v
    signed target/device_id comparison
        |
        +---- mismatch ----> DENY: target_id_mismatch
        |                   no authority-state access
        |                   no PWM execution
        |
        v
    local authority-state validation
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

The target comparison therefore occurs before the persistent authority-state path.

This ordering is the central ESP-LOCAL-008 enforcement property.

## Target-Gate Markers

A valid authority presented to the wrong endpoint produces the following scored sequence:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH
    008_CLIENT_COMPLETE ... result=target_id_mismatch

The denial must occur without later markers indicating authority-state success, durable consumption, PWM execution, or acceptance.

The corresponding endpoint persistent-state image must remain byte-for-byte unchanged.

## Correct-Target Markers

A valid authority presented to its intended endpoint proceeds through the full execution path:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The scored positive cases also required an independent hardware witness to observe one corresponding servo-control signal burst.

## Authority State

ESP-LOCAL-008 uses a dedicated NVS partition:

    partition: nuvl_state
    offset:    0x110000
    size:      0x6000
    namespace: nuvl_auth
    key:       state

The stored authority-state record contains:

    magic
    version
    state
    reserved
    authority_id[32]
    crc32

State values used by the firmware are:

    UNSPENT = 1
    SPENT   = 2

A correct-target authority must be UNSPENT before execution.

Consumption occurs before the physical command is accepted as complete. The runtime then performs a fresh reread and requires the stored state to be SPENT before crossing the PWM execution boundary.

NVS update behavior can leave an earlier UNSPENT record and a later SPENT record in the raw partition image. Scored state evidence therefore uses the latest valid record rather than assuming that the earlier record disappears.

## Provisioner

`ESP_LOCAL_008_PROVISIONER.c` prepares the dedicated `nuvl_state` partition with one frozen authority ID in UNSPENT state.

The provisioner:

- selects an endpoint instance;
- binds the expected endpoint identity;
- embeds the expected authority ID;
- initializes the dedicated NVS partition;
- refuses to overwrite an existing authority state;
- writes one UNSPENT record;
- commits the record;
- rereads the stored record;
- validates its structure, authority ID, CRC, and state;
- emits a durable provisioning PASS only after successful readback.

Representative success markers are:

    008_PROVISION_ENDPOINT=<device_id>
    008_PROVISION_LABEL=<authority label>
    008_AUTH_ID=<authority id>
    008_DURABLE_UNSPENT_VERIFIED
    008_PROVISION_PASS

Existing state causes provisioning to fail closed rather than silently reset or replace the authority.

## Final Servo1 Provisioning Variant

The replacement Servo1 positive run used AUTH-X3.

    endpoint:
      esp32-xiao-servo-01

    authority_id:
      5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

Frozen provisioner source SHA-256:

    1917B7CBCB872DE0C1AB9270668B2E6A26F03FCFDCE4925456BD416E6D5A9CAC

Frozen provisioner binary SHA-256:

    FF68964B8156BEAFAED632B9F6AB4738048CF66EAA07CBA8F466E21E34F29CFC

The X3 state image after provisioning and after restoring the endpoint runtime was identical:

    588C34697B132DF7B82E79BC6A06A2DD973938A446AEFF199726CA5F0F4BEF36

The raw record decoded as:

    magic:    4c56554e
    version:  1
    state:    1
    reserved: 0

After the scored X3 execution, the raw state image contained both the original state=1 record and a later state=2 record for the same authority ID.

Post-accept state SHA-256:

    F2193B58041E1BFAFB2DB2A97463C4833AA2EAE196F84102DAB3A26DF6144873

## Frozen Endpoint Runtime Builds

Servo #1 corrected runtime:

    SHA-256:
    C743FBE3D03BF3267B3BDFE9BD84FFE5D31E5335875F4FFADDD39E705E7A6A7E

Servo #2 corrected runtime:

    SHA-256:
    8CEB6B65C08885173C007D859AEE9F134F6DC97FF2E55518A811AB9E1FC88EE0

Servo #1 source configuration SHA-256:

    873A15DB09DF51D4A8BF430DF5C11AE51CFCFC31DAEFDA7BFF4A8F27D6DCEED3

Servo #2 source configuration SHA-256:

    DECB8F04A4B7B36CC3366D7302F41E7F76B9F81217548C925CED443FA65CCA0E

The endpoint application was flashed independently of the dedicated `nuvl_state` partition so runtime replacement did not reset the scored authority state.

## Final Directionality Results

The firmware participated in four final evidence cases.

| Run | Authority Scope | Endpoint | Firmware Result |
|---|---|---|---|
| `X2_S2_DENY_001` | Servo1 | Servo2 | target mismatch before state access |
| `Y3_S1_DENY_001` | Servo2 | Servo1 | target mismatch before state access |
| `X3_S1_ACCEPT_001` | Servo1 | Servo1 | target match, durable spend, one execution |
| `Y2_S2_ACCEPT_001` | Servo2 | Servo2 | target match, durable spend, one execution |

The two wrong-target cases left the target endpoint's persistent state unchanged.

The two correct-target cases crossed one PWM execution boundary and were independently observed at the corresponding physical signal line.

## GPIO Correction

Pre-scored validation identified an incorrect Servo #2 actuator GPIO mapping; the configuration was corrected before scored execution.

The final endpoint runtime used GPIO5 for the servo PWM signal on both endpoint boards.

Independent witness wiring was separate:

    witness GPIO4 -> Servo #2 signal
    witness GPIO5 -> Servo #1 signal

## Build Environment

The scored endpoint and provisioner firmware were built with ESP-IDF for ESP32-S3 targets.

Observed toolchain environment included:

    ESP-IDF 6.1
    esptool 5.3.1
    target: ESP32-S3

Typical project build entry point:

    idf.py build

Application-only flashing was used where preservation of the dedicated authority-state partition was required.

The generated flash command placed the application image at:

    0x10000

The dedicated authority-state partition remained at:

    0x110000

## Evidence Boundary

Firmware logs are not treated as the sole proof of execution.

ESP-LOCAL-008 combines:

- endpoint runtime markers;
- raw persistent-state images;
- provider authority artifacts;
- presenter JSON records;
- independent RMT witness capture;
- frozen source and binary hashes.

A TCP `accepted` response by itself is insufficient for a positive PASS.

A TCP `denied` response by itself is insufficient for a wrong-target PASS.

The scored result requires agreement between the endpoint enforcement path, persistent-state evidence, and the independent physical witness appropriate to the case.

## Scope

ESP-LOCAL-008 establishes signed target binding for the tested two-endpoint configuration.

It does not independently re-establish every property tested elsewhere in the ESP-LOCAL series, including crash-window persistence, reboot persistence, replay resistance, hostile-relay mutation resistance, or concurrent-requester contention.
