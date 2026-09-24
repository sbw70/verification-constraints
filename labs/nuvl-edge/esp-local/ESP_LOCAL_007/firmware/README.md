# ESP-LOCAL-007 Firmware

This directory contains the ESP-IDF endpoint firmware used for ESP-LOCAL-007 concurrent-requester testing, together with the explicit authority provisioners and build configuration required to reproduce the tested endpoint.

ESP-LOCAL-007 retains the ESP-LOCAL-006 authority-verification and enforcement path and changes the application-layer dispatch so multiple requester connections can enter that path concurrently.

## Directory contents

~~~text
firmware/
├── CMakeLists.txt
├── partitions.csv
├── sdkconfig
├── components/
│   └── monocypher/
└── main/
    ├── CMakeLists.txt
    ├── ESP_LOCAL_007_CONCURRENT.c
    ├── ESP_LOCAL_007_CONCURRENT_DIFF.txt
    ├── ESP_LOCAL_007_AUTH1_PROVISIONER.c
    ├── ESP_LOCAL_007_AUTH2_PROVISIONER.c
    └── local_wifi_config.example.h
~~~

## `ESP_LOCAL_007_CONCURRENT.c`

`ESP_LOCAL_007_CONCURRENT.c` is the endpoint runtime used to expose the existing enforcement path to genuine concurrent requester contention.

It is derived from the ESP-LOCAL-006 endpoint.

The significant ESP-LOCAL-007 change is dispatch behavior:

- the TCP listen backlog is increased;
- each accepted TCP connection is assigned its own FreeRTOS task;
- each client task sends an explicit `READY` message before reading a request;
- the listener immediately returns to `accept()` rather than processing one connection serially;
- multiple client tasks can therefore call the existing `process_request()` path concurrently.

The READY message is:

~~~json
{"ready":true,"test":"ESP_LOCAL_007"}
~~~

The coordinator waits until all intended requester connections have received this message before releasing their request bytes.

### Deliberately absent synchronization

ESP-LOCAL-007 does **not** add a contention mutex around:

- `process_request()`;
- provider verification;
- persistent-state access;
- durable consumption; or
- physical execution.

This is intentional.

Adding a serialization lock around the enforcement path would prevent the test from exercising contention at the authority-consumption boundary. The concurrent dispatcher therefore exposes the existing enforcement path to the race rather than solving the race in the test harness.

### Relationship to ESP-LOCAL-006

`ESP_LOCAL_007_CONCURRENT_DIFF.txt` records the source-level dispatch changes from `ESP_LOCAL_006.c` to `ESP_LOCAL_007_CONCURRENT.c`.

The diff shows the test-specific changes separately from the inherited enforcement implementation. The principal changes are the per-client FreeRTOS task, READY signaling, increased listen backlog, longer client socket timeout, and concurrent dispatch.

## Authority provisioners

Two explicit provisioning programs are retained in `main/`.

### `ESP_LOCAL_007_AUTH1_PROVISIONER.c`

Provisions the original ESP-LOCAL-007 AUTH1 authority state.

AUTH1 authority ID:

~~~text
5204cc275cbb67009025c7d4d84f2594b8f678b09092d091ca44576f0415a904
~~~

The provisioner writes one state record with:

~~~text
state = UNSPENT
~~~

It refuses to provision if an authority-state record already exists.

After writing and committing the record, it deinitializes and reinitializes the `nuvl_state` NVS partition, reads the record back, validates its structure and CRC, verifies the expected authority ID, and requires the state to remain `UNSPENT`.

Successful completion reports:

~~~text
007_AUTH1_DURABLE_UNSPENT_VERIFIED
007_AUTH1_PROVISION_PASS
~~~

### `ESP_LOCAL_007_AUTH2_PROVISIONER.c`

Provisions AUTH2, the fresh authority used for the final R003 contention run.

AUTH2 authority ID:

~~~text
066fd59f04ba90f1476ea388a84e125a349a54435552205c0aaa6d5adfa14545
~~~

Its behavior is the same as the AUTH1 provisioner:

- initialize the dedicated state partition;
- refuse provisioning if an existing state record is present;
- write exactly one `UNSPENT` record;
- commit it;
- deinitialize and reinitialize the partition;
- read the record back;
- validate the record, authority ID, and CRC; and
- require the reread state to be `UNSPENT`.

Successful completion reports:

~~~text
007_AUTH2_DURABLE_UNSPENT_VERIFIED
007_AUTH2_PROVISION_PASS
~~~

The provisioners are intentionally fail-closed. Existing authority state is not silently overwritten.

## Persistent-state record

The provisioners use a 44-byte state record:

~~~text
uint32_t magic
uint16_t version
uint8_t  state
uint8_t  reserved
uint8_t  authority_id[32]
uint32_t crc32
~~~

Defined values are:

~~~text
magic   = 0x4E55564C
version = 1

state:
    1 = UNSPENT
    2 = SPENT
~~~

The CRC is calculated over the record preceding the `crc32` field using reflected IEEE CRC-32.

The host-side `coordinator/decode_nuvl_state.py` utility can independently decode this record from a raw `nuvl_state` partition image.

## Partition layout

`partitions.csv` defines the endpoint layout used by this firmware:

| Name | Type | Subtype | Offset | Size |
|---|---|---|---|---|
| `nvs` | data | nvs | `0x9000` | 24K |
| `phy_init` | data | phy | `0xf000` | 4K |
| `factory` | app | factory | `0x10000` | 1M |
| `nuvl_state` | data | nvs | automatic | 24K |

Authority state is kept in the dedicated `nuvl_state` NVS partition rather than the normal application NVS partition.

Within that partition the provisioners use:

~~~text
namespace = nuvl_auth
key       = state
~~~

## Build configuration

The top-level `CMakeLists.txt` defines the project as:

~~~text
ESP_LOCAL_007_CONCURRENT
~~~

The checked-in `sdkconfig` records the ESP-IDF configuration used for the published build.

The `main/CMakeLists.txt` currently builds:

~~~text
ESP_LOCAL_007_CONCURRENT.c
~~~

with dependencies on:

- `nvs_flash`
- `esp_wifi`
- `esp_netif`
- `esp_event`
- `esp_driver_ledc`
- `lwip`
- `mbedtls`
- `monocypher`

The `components/monocypher/` directory supplies the Monocypher component used by the endpoint cryptographic implementation.

## Building a provisioner

The checked-in `main/CMakeLists.txt` selects `ESP_LOCAL_007_CONCURRENT.c`.

To build one of the provisioning programs instead, change the `SRCS` entry temporarily to the required provisioner:

~~~cmake
idf_component_register(
    SRCS
        "ESP_LOCAL_007_AUTH2_PROVISIONER.c"
    INCLUDE_DIRS
        "."
    PRIV_REQUIRES
        nvs_flash
)
~~~

After provisioning, restore `ESP_LOCAL_007_CONCURRENT.c` as the selected source and rebuild the runtime.

The provisioning application and concurrent runtime are separate firmware roles. Provisioning establishes the initial authority-state record; the concurrent runtime consumes and enforces that state during requester processing.

## Wi-Fi configuration

`main/local_wifi_config.example.h` is the publication-safe template for the local Wi-Fi configuration.

Create:

~~~text
main/local_wifi_config.h
~~~

from the example and set the credentials for the reproduction environment.

The example retains the tested SSID identifier but does not contain the lab Wi-Fi password.

`local_wifi_config.h` is consumed by the endpoint runtime and is not included as a published credential-bearing artifact.

## Reproduction sequence

The firmware portion of the ESP-LOCAL-007 setup follows this order:

1. Build the appropriate authority provisioner.
2. Flash the provisioner application.
3. Confirm its durable `UNSPENT` readback.
4. Preserve or inspect the resulting `nuvl_state` partition as required by the test procedure.
5. Restore `ESP_LOCAL_007_CONCURRENT.c` as the application source.
6. Build the concurrent runtime.
7. Flash the application partition without erasing or replacing `nuvl_state`.
8. Start the endpoint and confirm the ESP-LOCAL-007 listener is active.
9. Use the host-side coordinator to arm concurrent requester connections.

For R003, AUTH2 was provisioned before the concurrent runtime was installed.

## Important distinction: runtime versus provisioned authority

The concurrent runtime is not an AUTH2-specific runtime.

AUTH1 and AUTH2 are represented by persistent authority state established by their respective provisioners. The ESP-LOCAL-007 concurrent runtime was not modified to hardcode AUTH2 for R003.

This separation matters for reproduction: changing the provisioned authority does not require changing the concurrent dispatch implementation.

## Publication boundary

This directory contains the firmware artifacts required to understand and reproduce the ESP-LOCAL-007 concurrent endpoint configuration.

The concurrent-dispatch changes, provisioners, build configuration, partition definition, and cryptographic dependency are published so the tested configuration can be inspected independently.

The broader repository's publication boundary still applies to persistence-boundary implementation material not intended for publication. The presence of reproduction artifacts here should not be interpreted as expanding claims beyond the behavior actually tested by ESP-LOCAL-007.
