# ESP-LOCAL-006 Provenance

This document records the lineage, tested identities, publication relationships, and evidence classifications for ESP-LOCAL-006.

ESP-LOCAL-006 evaluates hostile-relay / compromised-forwarder behavior while retaining provider-controlled authority and endpoint-local recognition and enforcement.

The completed publication includes the tested endpoint implementation, provisioner implementation, preserved tested application binaries, provider artifacts, hostile-relay implementation, independent witness implementation, persistent-state captures, relay evidence, curated terminal evidence, and build-support material required to inspect the tested authority path.

## Test Lineage

ESP-LOCAL-006 extends the endpoint-local bounded-authority model exercised in ESP-LOCAL-004 and ESP-LOCAL-005.

ESP-LOCAL-004 established endpoint-local Ed25519 recognition of provider-issued authority.

ESP-LOCAL-005 added persistent endpoint-local single-use authority consumption before the observed physical command path and characterized persistence behavior across restart, power-loss, malformed-state, and crash conditions.

ESP-LOCAL-006 retained that authority model and introduced a hostile application-layer intermediary between the requester/provider side and the endpoint.

Tested path:

```text
requester / provider
        ↓
Raspberry Pi 3 hostile relay
        ↓
ESP32-S3 endpoint-local recognition
        ↓
persistent single-use authority enforcement
        ↓
servo PWM command path
        ↓
independent ESP32-S3 witness
```

ESP-LOCAL-006 did not transfer provider authority-generation capability to the relay.

The relay could inspect, modify, substitute, forward, delay, and replay requests but did not possess the trusted provider private key.

## Architectural Classification

ESP-LOCAL-006 is classified as:

```text
NUVL core
architecture change: no
```

The test adds a hostile intermediary condition to the existing bounded-authority architecture.

It does not introduce a new authority source or transfer authority-generation capability to the relay or endpoint.

The supported claim is limited to the tested architecture:

> Intermediary control over the request path did not become the ability to originate, enlarge, substitute, regenerate, or reuse executable provider authority.

The test also demonstrated that rejected invalid submissions did not consume or poison legitimate unused authority subsequently accepted under its original provider-established bounds.

## Trusted Provider Key Lineage

ESP-LOCAL-006 reused the Ed25519 provider identity previously used in the ESP-LOCAL series.

Original trusted private-key source:

```text
C:\Users\holiw\esp32-main\ESP_LOCAL_004\provider\keys\esp_local_004_private.pem
```

Original private-key file SHA-256:

```text
DA0A36F274EFC6E3CE1C7643800B952B1AA2895201E5A6D6852D308729466509
```

Corresponding raw Ed25519 public key:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

The trusted private key was used on the provider/requester side to generate the signed Authority #1 and Authority #2 trusted requests.

It was not present on the Raspberry Pi 3 hostile relay.

It was not embedded in the endpoint runtime.

It is not published in the ESP-LOCAL-006 tree.

## Endpoint Identity

Tested endpoint:

```text
identity:          esp32-xiao-servo-02
hardware:          Seeed XIAO ESP32-S3
MAC:               1c:db:d4:45:10:a4
serial interface:  COM15
TCP port:          19061
framework:         ESP-IDF v6.1
```

Observed physical-command path:

```text
endpoint GPIO5
      ↓
witness GPIO4
```

## Endpoint Runtime Lineage

Original project root:

```text
C:\Users\holiw\esp32-main\ESP_LOCAL_006\
```

Original tested runtime source:

```text
main\ESP_LOCAL_006.c
```

Published source:

```text
firmware/main/ESP_LOCAL_006.c
```

Tested source SHA-256:

```text
4BD962535C61C17AD093973DBB720A99CD709D626D3E9EEFF1AD51B6E6E6AAFF
```

Recovered preserved tested application binary:

```text
build\ESP_LOCAL_006.bin
```

Published as:

```text
evidence/ESP_LOCAL_006_RUNTIME.bin
```

Tested binary SHA-256:

```text
21376CDD12D63D2F0E8362C969C7268BE56A701ECB3C78BAC712564D5FBE5E75
```

The recovered binary matched the previously recorded SHA-256 for the runtime used during the scored ESP-LOCAL-006 matrix.

The publication therefore contains the preserved tested application image rather than a later rebuild represented as the tested binary.

## Runtime Authority Path

The published runtime performs the following authority-processing sequence:

```text
receive relay envelope
        ↓
strict envelope decoding
        ↓
Ed25519 verification against trusted provider public key
        ↓
semantic admissibility
        ↓
SHA-256 received canonical authority
        ↓
persistent-state validation
        ↓
exact authority-id match
        ↓
require UNSPENT
        ↓
transition to SPENT
        ↓
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
fresh persistent-state reread
        ↓
require same authority-id + SPENT
        ↓
PWM command
```

The runtime does not contain provider private signing material.

No later runtime failure path restores consumed authority.

Missing, malformed, corrupt, mismatched, or already-spent authority state is not converted into fresh authority.

## Authority-State Record

ESP-LOCAL-006 uses a dedicated NVS partition.

Partition definition:

```text
nuvl_state,data,nvs,,24K,
```

Resolved tested parameters:

```text
label:   nuvl_state
offset:  0x110000
size:    0x6000
length:  24576 bytes
```

The authority record is 44 bytes and contains:

```text
magic
version
state
reserved
authority_id[32]
crc32
```

Recognized authority-state values:

```text
UNSPENT = 1
SPENT   = 2
```

Namespace:

```text
nuvl_auth
```

Key:

```text
state
```

The stored `authority_id` is matched against the SHA-256 identifier of the received canonical authority.

## Persistence Interpretation

The runtime records accepted authority as `SPENT` before PWM command issuance.

After `nvs_commit()`, the tested runtime:

```text
closes the NVS handle
deinitializes the authority partition
reinitializes the authority partition
performs a fresh read
requires the same authority identifier
requires SPENT state
```

The runtime emits:

```text
006_DURABLE_SPENT_REREAD_PASS
```

only after that post-commit sequence succeeds.

This is stronger than a same-handle cached reread.

It does not independently establish persistence across every possible immediate power-loss boundary and does not resolve the exact ESP-IDF/NVS physical persistence point characterized separately in ESP-LOCAL-005.

## Authority #1 Lineage

Authority #1 was generated using the trusted provider Ed25519 private key.

Published metadata:

```text
provider/ESP_LOCAL_006_AUTH1.txt
```

Original SHA-256:

```text
BEF521A5A13F6707271731A8D5E46F8713F976F653B5ABEB8DE71F5FE05C456D
```

Published signed request:

```text
provider/ESP_LOCAL_006_AUTH1_REQUEST.json
```

Original SHA-256:

```text
8DF2EAA48A572494EE32F815AFF05B4E7533221C9AAA04C859836983D7DB27DD
```

Canonical semantics:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "99337255d93cee60019493a813c42f23"
}
```

Authority identifier:

```text
f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6
```

Provider signature:

```text
6bsiP6Tqky4FfRvy0qSEXs+gZxbKT/5tz8AAbPMVnLYdHKN3hl8mQ9WsIGk5bgUmS5+/ja8CfgrygAkiRiHuAA==
```

Authority #1 was used for:

```text
action mutation
context mutation
device_id mutation
max_uses enlargement
untouched trusted positive control
spent-authority replay
```

## Authority #1 Provisioner Lineage

Original source:

```text
main\ESP_LOCAL_006_PROVISIONER.c
```

Published source:

```text
firmware/main/ESP_LOCAL_006_PROVISIONER.c
```

Source SHA-256:

```text
4F461509B5A17F333F43A58F536313CD2647A630AAB5A873CA7C7E116A8F04BB
```

Recovered tested provisioner application binary:

```text
build-provisioner\ESP_LOCAL_006.bin
```

Published as:

```text
evidence/ESP_LOCAL_006_PROVISIONER.bin
```

Tested binary SHA-256:

```text
DE134F4C8B69E5B8627B952098D601D769FCC4DE2F27F9D4CC517F12837675FC
```

The provisioner constructs the exact Authority #1 identifier as `UNSPENT`.

It refuses provisioning when an existing authority-state record is already present.

After writing and committing the record, it closes and reinitializes the authority-state partition and performs a fresh reread requiring a valid `UNSPENT` record before reporting provisioning success.

## Authority #1 Final State

Final raw state capture:

```text
evidence/ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin
```

SHA-256:

```text
6CD54795B1A346E8C4C87A0ECD044BC64025E49BA55D2F170E9B03FF74306C9F
```

The parsed record identified Authority #1 and showed:

```text
state: SPENT
```

The raw partition capture is evidence of the final authority-state image.

Its hash identifies the complete partition image and is not, by itself, interpreted as proof that only the state byte changed.

## Authority #2 Lineage

Authority #2 was generated as a fresh trusted-provider authority for the different-provider-key control.

Published metadata:

```text
provider/ESP_LOCAL_006_AUTH2.txt
```

SHA-256:

```text
7BD190C4E51BF16260996D1A1745099BA4D0E58A47448385E0D29E9234A9A2BB
```

Canonical semantics:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "58f8f57034a9bbe30ffb099c7f9ae62c"
}
```

Authority identifier:

```text
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
```

## Wrong-Provider Key Lineage

A separate Ed25519 keypair was generated specifically for the Authority #2 negative control.

Wrong-provider raw public key:

```text
4c0baa6a6df7637dbb78aec1262c142be80f66d68eac3fd91f7ee41ee003a2de
```

Published public-key file:

```text
provider/ESP_LOCAL_006_WRONG_PROVIDER_PUBLIC.pem
```

Original public-key file SHA-256:

```text
34AD95543CA665E834B8DFD955C5212052F1D2548061EF657966B896942DCF40
```

Local wrong-provider private-key SHA-256:

```text
124669887CB947107821229A821C65F0011CFD6FC76EDB909EB84928CBB0942E
```

The wrong-provider private key is intentionally not published.

The endpoint had no configured trust relationship with the wrong-provider public key.

## Authority #2 Request Relationship

Trusted-provider request:

```text
provider/ESP_LOCAL_006_AUTH2_TRUSTED_REQUEST.json
```

SHA-256:

```text
4BA2BEB9B3C2A405DDCA5530BA693C406975BC4B7C514788582D75E9F333933A
```

Wrong-provider request:

```text
provider/ESP_LOCAL_006_AUTH2_WRONG_PROVIDER_REQUEST.json
```

SHA-256:

```text
A178FDEC65502AECC90DB8065B5EF88A64D70FA5F574D5C9C0D5AAE46B63AAE5
```

Verification established:

```text
authority_bytes_equal: True

authority_sha256:
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

signatures_equal: False
```

The two requests therefore preserve identical canonical Authority #2 bytes while differing in signature identity.

This isolates provider-key trust from authority-content differences.

The wrong-provider version was rejected.

The trusted-provider version over the same canonical authority bytes was subsequently accepted.

The wrong-provider rejection did not consume Authority #2.

## Authority #2 Provisioner Lineage

Original source:

```text
main\ESP_LOCAL_006_AUTH2_PROVISIONER.c
```

Published source:

```text
firmware/main/ESP_LOCAL_006_AUTH2_PROVISIONER.c
```

Source SHA-256:

```text
EFF601F71E71DB9AED8FC6E6849A4CD6DB238CB2F3FAED75F14E4BE52B2E3F2C
```

Recovered tested application binary:

```text
build-auth2-provisioner\ESP_LOCAL_006.bin
```

Published as:

```text
evidence/ESP_LOCAL_006_AUTH2_PROVISIONER.bin
```

Tested binary SHA-256:

```text
D465219F6460DEE4A69381221F93EDE09BD2D82C67025425B2B5E9515864C0D8
```

The provisioner establishes the exact Authority #2 identifier as `UNSPENT`.

It refuses provisioning if an authority-state record already exists.

## Authority #2 Persistent-State Captures

Pre-test capture:

```text
evidence/ESP_LOCAL_006_AUTH2_UNSPENT.bin
```

SHA-256:

```text
7529911EE67A9702F2769BB5AFDCAF40481BF3C8E601F0E508BAA62478F4D80C
```

Parsed record:

```text
authority_id:
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

state:
UNSPENT
```

The NVS page CRC validated.

Final post-test capture:

```text
evidence/ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin
```

SHA-256:

```text
F807BC6493E7D2F2CE33EB72A550E5F9ECA2597C3DD83EE9AB0D60E721EA528C
```

Parsed record:

```text
authority_id:
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

state:
SPENT
```

The NVS page CRC validated.

The pre-test and final images have different complete-partition hashes.

The specific `UNSPENT` to `SPENT` interpretation comes from parsing the authority record and validating the record structure and CRC rather than from the hash difference alone.

## Persistent-State Capture Lineage

Published raw state images:

```text
evidence/ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin
evidence/ESP_LOCAL_006_AUTH2_UNSPENT.bin
evidence/ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin
```

Each image is a direct raw read of the dedicated endpoint `nuvl_state` partition.

These files are binary partition captures.

They are not reconstructed text evidence.

## Hostile Relay Lineage

The hostile relay was developed and executed on a Raspberry Pi 3.

Original path:

```text
/home/seth/ESP_LOCAL_006/relay/esp_local_006_hostile_relay.py
```

Published copy:

```text
relay/esp_local_006_hostile_relay.py
```

Tested source SHA-256:

```text
61684936844297A11895218EB78630196BA2EC74BE1E5399F6F629AF012E66F4
```

The relay implementation supports:

```text
pass
mutate-action
mutate-context
mutate-device
mutate-max-uses
replay
```

The relay retained the original provider signature after mutation.

It did not possess the trusted provider private key.

It did not have trusted-provider signing capability.

## Relay Host Baseline

Published baseline:

```text
evidence/ESP_LOCAL_006_PI3_BASELINE.txt
```

Original path:

```text
/home/seth/ESP_LOCAL_006/evidence/ESP_LOCAL_006_PI3_BASELINE.txt
```

SHA-256:

```text
14A18FC971B79CB479751E88AD39BDE3391C0D40BDAB49D7D40BECD40B9E49D5
```

Test topology included:

```text
Pi hostname: nuvl-relay

eth0:
192.168.0.141/24
test-path interface

wlan0:
192.168.1.154/24
management interface

IP forwarding:
disabled
```

## Relay Evidence Lineage

Authority #1 relay evidence:

```text
evidence/ESP_LOCAL_006_RELAY_AUTH1.jsonl
```

Frozen record count:

```text
8
```

Frozen SHA-256:

```text
CCAC98462DA0708A463ECC1328A5C01CD0B77F0566E1260F9E70237B0F43B659
```

The file contains scored transactions plus non-authority connectivity/probe records.

Empty probes are not classified as scored authority attempts.

Authority #2 relay evidence:

```text
evidence/ESP_LOCAL_006_RELAY_AUTH2.jsonl
```

Record count:

```text
3
```

Frozen SHA-256:

```text
27A63A71289A49E9B44DF57ACCE8A065D4F1CBA2A5B697E4314B4CBF2982A0DA
```

For pass-through transactions, relay evidence preserved byte equality between ingress and egress.

Known Authority #2 envelope hashes:

```text
wrong-provider envelope:
03bc27c96c99225f84a64fd74621293826f0a0561f67fbea2484b9041ba0137b

trusted-provider envelope:
13ce223290a908b855eccf05047a636cdee6de6207639dae2a3e8076a2d898a4
```

## Transport Anomaly Lineage

The first `max_uses` mutation attempts experienced multisecond Pi-to-endpoint transport delay and timed out before reaching the endpoint.

Those attempts were not classified as authorization denials.

The relay source was inspected and no corresponding mutation defect was identified.

The case was rerun with a longer relay/requester timeout.

The rerun reached the endpoint and was rejected by the endpoint validation path.

Only the completed endpoint-reaching attempt was scored.

This preserves the distinction between:

```text
transport failure
```

and:

```text
authorization denial
```

## Independent Witness Lineage

The independent witness was a separate ESP32-S3 DevKit running MicroPython.

Witness MAC:

```text
44:1b:f6:ff:36:a8
```

Serial interface:

```text
COM8
```

Physical mapping:

```text
endpoint GPIO5
      ↓
witness GPIO4
```

Published implementation:

```text
witness/ESP_LOCAL_006_WITNESS_GPIO4.py
```

Publication-stage SHA-256:

```text
CEF567D1778F648904C6C3410381B96FFA0938E7D86E483D286FDABE0EE3CAA3
```

The witness uses MicroPython pulse-width measurement and reports:

```text
PWM_HIGH_US <width>
```

The witness does not:

```text
generate provider authority
verify provider signatures
consume authority
modify authority state
participate in authorization
```

It observes the electrical PWM command path only.

## Endpoint Transcript Lineage

The COM15 endpoint session was observed interactively during the original scored run.

The serial session was not redirected into a raw capture file.

Selected preserved terminal output was later assembled into:

```text
evidence/ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt
```

Publication-stage SHA-256:

```text
17D7C4F5C1C8AFF3BD5BEAC42116D92ED7B7C431D4BC78FAC10BB12B909524CA
```

This artifact is explicitly classified as a curated derivative.

It is not represented as an original raw serial capture.

Its SHA-256 identifies the curated publication artifact itself.

## Witness Transcript Lineage

The COM8 witness session was also observed interactively rather than redirected into an original raw capture file.

Preserved output was later assembled into:

```text
evidence/ESP_LOCAL_006_WITNESS_COM8_CURATED.txt
```

Publication-stage SHA-256:

```text
5B768366307449D2C6694A15A50C271B2CCC217FA7C0AEE0BA9F451EE209C378
```

This artifact is a curated derivative.

It preserves:

```text
two isolated 1 µs Auth1 transients
Auth1 servo-valid PWM sequence
Auth2 servo-valid PWM sequence
absence of a second replay-associated servo-valid burst
```

The isolated `1 µs` observations are retained rather than omitted.

They are not classified as servo-valid PWM pulses.

## Witnessed Authority #1 Command

The accepted Authority #1 execution produced:

```text
49 servo-valid observed pulses
pulse widths: 1998–2001 µs
```

Two isolated `1 µs` transients were also preserved before the valid burst.

The replay control did not produce a second servo-valid burst.

## Witnessed Authority #2 Command

The wrong-provider Authority #2 request produced no servo-valid PWM command.

The subsequent trusted-provider request over the same canonical Authority #2 bytes produced:

```text
49 servo-valid observed pulses
pulse widths: 1999–2001 µs
```

The subsequent replay produced no second servo-valid burst.

## Build Configuration Lineage

Published project-level build file:

```text
firmware/CMakeLists.txt
```

Original SHA-256:

```text
74756F785534E7C037C1873F6902BE2F5D041F823EF190B1DD6C628924D58565
```

Published partition definition:

```text
firmware/partitions.csv
```

Original SHA-256:

```text
2C19BE352D37A87EFF1910984DA4094CC3F76658E0E2F80B630D4C35E4398337
```

Published ESP-IDF configuration:

```text
firmware/sdkconfig
```

Original SHA-256:

```text
9C6A5C99E2F1FE700886778ED4569614A62D36C7BCDE0B5C8090C88B40B09FAB
```

The original project-local Wi-Fi configuration file is not published because it contained local network credentials.

## Main CMake Selector Lineage

The local project reused:

```text
main/CMakeLists.txt
```

as a source selector during the different application builds.

The final retained local form selected the Authority #2 provisioner:

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

Original SHA-256:

```text
9665E6F9CDEBFCC0C640B0E1B6ADBBCAD67E5662F94EE6D3FE92B31D785B98FC
```

That exact final retained file is published as:

```text
firmware/main/CMakeLists.AUTH2_TESTED.txt
```

It is identified as the final retained Authority #2 build selector and is not represented as the universal build selector for the runtime or Authority #1 provisioner.

## Wi-Fi Configuration Publication Derivative

Original local file:

```text
main/local_wifi_config.h
```

Original SHA-256:

```text
AC311CA125F7DC1AC30346D7ABF5DB3361737261AFEA4E14863DEE6F87182629
```

The original contained the test network SSID and Wi-Fi password.

It is not published.

A sanitized derivative is published as:

```text
firmware/main/local_wifi_config.example.h
```

with placeholder values:

```c
#pragma once

#define ESP_LOCAL_006_WIFI_SSID     "<TEST_WIFI_SSID>"
#define ESP_LOCAL_006_WIFI_PASSWORD "<TEST_WIFI_PASSWORD>"
```

The sanitized derivative has its own publication identity.

The original credential-bearing file hash is not assigned to the modified publication copy.

## Monocypher Component Lineage

Published component path:

```text
firmware/components/monocypher/
```

Published component build file:

```text
firmware/components/monocypher/CMakeLists.txt
```

Original SHA-256:

```text
4E020DC17F045BE8578EB707260D94059C2D5D4C9175DC8481D7AB254305A7B6
```

Published sources:

```text
firmware/components/monocypher/monocypher.c
firmware/components/monocypher/monocypher.h
firmware/components/monocypher/monocypher-ed25519.c
firmware/components/monocypher/monocypher-ed25519.h
```

Original source SHA-256 values:

```text
monocypher.c
F1F838CDD483BDEBE0DF0FF5C5ED60535E496F769C6A2F933AC4C0B114207123

monocypher.h
FCAF6ED771358BB4F40FBA016F6518AE86EC02B1B877D2CC35AD92D3A26FD7B3

monocypher-ed25519.c
CE0D2F8E32CA8F66398BA5B3456CC74327C3EFF14E7B950CE7D57BE9025CC453

monocypher-ed25519.h
3A3035181F991A158D0E1C7567258F0BAE8BA0F1F23C5512B4A1DB1B3C9730CE
```

These identities are consistent with the Monocypher component used in the preceding ESP-LOCAL work.

## Published Tested Application Binaries

The completed publication contains the three preserved application binaries used during the ESP-LOCAL-006 sequence:

```text
evidence/ESP_LOCAL_006_RUNTIME.bin
evidence/ESP_LOCAL_006_PROVISIONER.bin
evidence/ESP_LOCAL_006_AUTH2_PROVISIONER.bin
```

Recorded tested SHA-256 values:

```text
ESP_LOCAL_006_RUNTIME.bin
21376CDD12D63D2F0E8362C969C7268BE56A701ECB3C78BAC712564D5FBE5E75

ESP_LOCAL_006_PROVISIONER.bin
DE134F4C8B69E5B8627B952098D601D769FCC4DE2F27F9D4CC517F12837675FC

ESP_LOCAL_006_AUTH2_PROVISIONER.bin
D465219F6460DEE4A69381221F93EDE09BD2D82C67025425B2B5E9515864C0D8
```

A later rebuilt binary is a reproduction artifact unless its SHA-256 exactly matches the corresponding preserved tested binary.

## Publication Tree

The implementation publication is organized as:

```text
firmware/
├── README.md
├── CMakeLists.txt
├── partitions.csv
├── sdkconfig
├── main/
│   ├── CMakeLists.AUTH2_TESTED.txt
│   ├── ESP_LOCAL_006.c
│   ├── ESP_LOCAL_006_PROVISIONER.c
│   ├── ESP_LOCAL_006_AUTH2_PROVISIONER.c
│   └── local_wifi_config.example.h
└── components/
    └── monocypher/
        ├── CMakeLists.txt
        ├── monocypher.c
        ├── monocypher.h
        ├── monocypher-ed25519.c
        └── monocypher-ed25519.h
```

Preserved tested binaries are placed under:

```text
evidence/
```

rather than duplicated under `firmware/`.

## Artifact Classification

| Artifact class | Classification | Purpose |
|---|---|---|
| `firmware/main/*.c` | Original tested source / byte-preserved publication copy | Endpoint and provisioner implementation |
| `firmware/CMakeLists.txt` | Original project build material | ESP-IDF project definition |
| `firmware/partitions.csv` | Original tested build material | Partition layout |
| `firmware/sdkconfig` | Original tested ESP-IDF configuration | Tested build configuration |
| `firmware/main/CMakeLists.AUTH2_TESTED.txt` | Original final retained main build selector | Authority #2 provisioner build state |
| `firmware/main/local_wifi_config.example.h` | Sanitized publication derivative | Reproduction template without local credentials |
| `firmware/components/monocypher/*` | Original dependency source / publication copy | Ed25519 cryptographic dependency |
| `evidence/*PROVISIONER.bin` | Preserved tested binary | Provisioning application image |
| `evidence/ESP_LOCAL_006_RUNTIME.bin` | Preserved tested binary | Scored endpoint runtime |
| `relay/*.py` | Original tested source / publication copy | Hostile intermediary implementation |
| `witness/*.py` | Tested witness implementation / publication copy | Independent PWM observation |
| `provider/*.txt` | Provider-generated test artifact | Frozen authority metadata |
| `provider/*.json` | Provider-generated test artifact | Signed request envelopes |
| `provider/*.pem` | Test public-key material | Wrong-provider verification material |
| `evidence/*.jsonl` | Original test-time evidence | Relay transaction sequence |
| `evidence/*SPENT*.bin` / `*UNSPENT*.bin` | Original binary evidence | Raw persistent-state partition capture |
| `evidence/*_CURATED.txt` | Curated derivative | Preserved terminal observations |
| `evidence/ESP_LOCAL_006_PI3_BASELINE.txt` | Original environment record | Relay-host baseline |

## Intentionally Unpublished Material

The completed ESP-LOCAL-006 publication no longer withholds the endpoint runtime, authority provisioner source, or preserved tested application binaries.

The principal intentionally unpublished test material is:

```text
trusted provider private key
wrong-provider private key
original credential-bearing local_wifi_config.h
```

The omission of those files does not prevent inspection of the tested trust relationships because the corresponding public keys, signed test requests, source code, persistent-state captures, and tested application binaries are published.

## Excluded Troubleshooting Artifact

A provisioning diagnostic artifact was retained locally:

```text
ESP_LOCAL_006_PREPROVISION_UNEXPECTED_STATE.bin
```

It resulted from an intermediate setup/provisioning diagnostic condition.

It was not part of the scored ESP-LOCAL-006 matrix.

It is therefore intentionally excluded from the curated publication package.

## Publication Relationship

The ESP-LOCAL-006 publication distinguishes between:

```text
original tested artifacts
byte-preserved publication copies
preserved tested binaries
sanitized derivatives
curated derivatives
excluded diagnostic material
```

A hash established for an original artifact is not assigned to a modified or reconstructed derivative.

The sanitized Wi-Fi header has its own publication identity.

The curated terminal transcripts have their own publication identities.

The preserved tested application binaries retain the recorded SHA-256 identities of the binaries used in the test sequence.

## Manifest Relationship

`SHA256SUMS.txt` records SHA-256 values for the files actually present in the final published ESP-LOCAL-006 tree.

The manifest is generated only after the publication tree and documentation are finalized.

Any earlier manifest created before the final firmware-source and binary publication is superseded by the final regenerated manifest.

## Evidence Relationship

The publication preserves distinct evidence layers:

```text
provider authority artifact
        ↓
hostile relay transaction evidence
        ↓
endpoint decision observation
        ↓
persistent authority state
        ↓
independent PWM observation
```

The provider artifacts establish the canonical authority and signature material presented.

The relay JSONL files establish intermediary handling.

The endpoint curated transcript preserves observed endpoint decisions.

The raw partition images preserve persistent authority-state conditions.

The witness transcript preserves independent electrical PWM observations.

The source and preserved tested binaries expose the implementation corresponding to those observed behaviors.

No single evidence layer is treated as sufficient by itself to establish the complete result.

## Interpretation Boundaries

A relay timeout or dropped request is not classified as an endpoint authorization denial unless the request reached the endpoint and exercised the validation path.

A difference between complete persistent-state partition hashes is not, by itself, proof of a specific field transition.

A curated terminal transcript is not represented as a raw redirected serial capture.

An electrical PWM witness is not represented as proof of guaranteed mechanical movement.

Post-commit partition deinitialization, reinitialization, and fresh reread establish a stronger runtime verification boundary than a same-handle read but do not independently resolve every immediate-power-loss persistence point.

ESP-LOCAL-006 does not establish resistance to:

```text
trusted provider private-key theft
complete endpoint compromise
denial of service
hostile routing
rollback of persistent storage
physical storage tampering
absence of trusted time
```

Those limitations do not alter the tested result that a hostile intermediary lacking trusted provider signing material did not obtain greater executable authority in the scored configuration.

Observed outcomes are recorded in:

```text
RESULTS.md
```

Firmware implementation and reproduction notes are recorded in:

```text
firmware/README.md
```

Published-file integrity is recorded in:

```text
SHA256SUMS.txt
```
