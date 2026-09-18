# ESP-LOCAL-006 Provenance

## Purpose

This document records the origin, lineage, and relationship of the artifacts published for ESP-LOCAL-006.

It distinguishes:

- original tested artifacts,
- provider-generated authority material,
- hostile-relay artifacts,
- independent witness material,
- direct persistent-state captures,
- curated terminal transcripts,
- publication copies,
- tested implementation material intentionally excluded from publication.

Observed behavior is documented in `RESULTS.md`.

Published artifact integrity is documented in `SHA256SUMS.txt`.

## Test Lineage

ESP-LOCAL-006 extends the endpoint-local bounded-authority model exercised in ESP-LOCAL-004 and ESP-LOCAL-005.

ESP-LOCAL-004 established endpoint-local Ed25519 recognition of provider-issued authority.

ESP-LOCAL-005 added persistent endpoint-local single-use consumption before the observed physical command path.

ESP-LOCAL-006 retained that endpoint-local enforcement model and introduced a hostile application-layer intermediary between the requester/provider side and the endpoint.

The tested path was:

```text
requester / provider
        ↓
Raspberry Pi 3 hostile relay
        ↓
ESP32-S3 endpoint-local enforcement
        ↓
servo PWM command path
        ↓
independent ESP32-S3 witness
```

ESP-LOCAL-006 did not transfer provider authority-generation capability to the relay.

The relay could inspect, modify, substitute, forward, and replay requests but did not possess the trusted provider private key.

## Trusted Provider Key Lineage

ESP-LOCAL-006 reused the Ed25519 provider identity previously used in ESP-LOCAL-004 and ESP-LOCAL-005.

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

The trusted provider private key was used on the requester/provider side to generate the signed Auth1 and Auth2 control artifacts.

It was not present on the Raspberry Pi 3 hostile relay.

It is not published in the ESP-LOCAL-006 directory.

## Endpoint Runtime Lineage

The tested endpoint runtime was developed locally under:

```text
C:\Users\holiw\esp32-main\ESP_LOCAL_006\
```

Primary tested runtime source:

```text
main\ESP_LOCAL_006.c
```

Original tested source SHA-256:

```text
4BD962535C61C17AD093973DBB720A99CD709D626D3E9EEFF1AD51B6E6E6AAFF
```

The final runtime binary used for the scored ESP-LOCAL-006 matrix had SHA-256:

```text
21376CDD12D63D2F0E8362C969C7268BE56A701ECB3C78BAC712564D5FBE5E75
```

That runtime was flashed to the endpoint identified as:

```text
identity: esp32-xiao-servo-02
hardware: Seeed XIAO ESP32-S3
MAC: 1c:db:d4:45:10:a4
serial interface: COM15
```

The final tested runtime connected to the ESP-LOCAL-006 network and listened for endpoint requests on TCP port `19061`.

The endpoint runtime source and binary are intentionally not published in this package because they expose implementation detail inside the persistent-authority enforcement boundary.

Their hashes are retained here to identify the tested implementation without distributing that implementation.

## Persistent-State Implementation Publication Boundary

ESP-LOCAL-006 reused the endpoint-local persistent-state model established during ESP-LOCAL-005.

The public ESP-LOCAL-006 package preserves state captures and observed behavior but does not publish the persistence-boundary implementation.

The following tested implementation classes remain outside the ESP-LOCAL-006 publication tree:

- endpoint persistence implementation source,
- authority provisioner source,
- authority provisioner binaries,
- implementation-specific state-write logic.

This is a publication boundary, not an absence of tested implementation.

The resulting raw state captures are published separately as evidence.

## Authority #1 Lineage

Authority #1 was generated locally using the trusted provider Ed25519 private key.

Published metadata:

```text
provider/ESP_LOCAL_006_AUTH1.txt
```

Published request envelope:

```text
provider/ESP_LOCAL_006_AUTH1_REQUEST.json
```

Authority #1 identifier:

```text
f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6
```

Authority #1 canonical semantics:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "99337255d93cee60019493a813c42f23"
}
```

Known original artifact hashes:

```text
ESP_LOCAL_006_AUTH1.txt
BEF521A5A13F6707271731A8D5E46F8713F976F653B5ABEB8DE71F5FE05C456D

ESP_LOCAL_006_AUTH1_REQUEST.json
8DF2EAA48A572494EE32F815AFF05B4E7533221C9AAA04C859836983D7DB27DD
```

Authority #1 was used for:

- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` enlargement,
- untouched positive control,
- spent-authority replay.

## Authority #1 Provisioning Lineage

Authority #1 was provisioned into the dedicated endpoint persistent-state partition before the scored relay matrix.

The generated Authority #1 provisioner source had SHA-256:

```text
4F461509B5A17F333F43A58F536313CD2647A630AAB5A873CA7C7E116A8F04BB
```

The associated provisioner binary had SHA-256:

```text
DE134F4C8B69E5B8627B952098D601D769FCC4DE2F27F9D4CC517F12837675FC
```

Those provisioner artifacts are not included in the public ESP-LOCAL-006 package.

An intermediate raw state capture was created during provisioning diagnostics after the first successful provisioning run and before the provisioning sequence was fully understood.

That troubleshooting artifact was retained locally as:

```text
ESP_LOCAL_006_PREPROVISION_UNEXPECTED_STATE.bin
```

It is intentionally excluded from the curated publication package because it is not part of the scored ESP-LOCAL-006 matrix.

The final post-Auth1 state capture is published as:

```text
evidence/ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin
```

Publication-stage SHA-256:

```text
6cd54795b1a346e8c4c87a0ecd044bc64025e49ba55d2f170e9b03ff74306c9f
```

## Authority #2 Lineage

Authority #2 was generated locally as a fresh provider-issued authority for the different-provider-key control.

Published metadata:

```text
provider/ESP_LOCAL_006_AUTH2.txt
```

Authority #2 identifier:

```text
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
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

Known original metadata SHA-256:

```text
7BD190C4E51BF16260996D1A1745099BA4D0E58A47448385E0D29E9234A9A2BB
```

## Wrong-Provider Key Lineage

A separate Ed25519 keypair was generated locally specifically for the Authority #2 negative control.

The keypair was independent of the trusted provider key.

Wrong-provider raw public key:

```text
4c0baa6a6df7637dbb78aec1262c142be80f66d68eac3fd91f7ee41ee003a2de
```

Published public key:

```text
provider/ESP_LOCAL_006_WRONG_PROVIDER_PUBLIC.pem
```

Known original public-key file SHA-256:

```text
34AD95543CA665E834B8DFD955C5212052F1D2548061EF657966B896942DCF40
```

The corresponding wrong-provider private key was generated only for the negative-control signing operation.

Its local file SHA-256 was:

```text
124669887CB947107821229A821C65F0011CFD6FC76EDB909EB84928CBB0942E
```

The wrong-provider private key is intentionally not published.

The endpoint had no configured trust relationship with the wrong-provider public key.

## Authority #2 Request Relationship

Two request envelopes were generated over the same canonical Authority #2 bytes.

Trusted-provider request:

```text
provider/ESP_LOCAL_006_AUTH2_TRUSTED_REQUEST.json
```

Known original SHA-256:

```text
4BA2BEB9B3C2A405DDCA5530BA693C406975BC4B7C514788582D75E9F333933A
```

Wrong-provider request:

```text
provider/ESP_LOCAL_006_AUTH2_WRONG_PROVIDER_REQUEST.json
```

Known original SHA-256:

```text
A178FDEC65502AECC90DB8065B5EF88A64D70FA5F574D5C9C0D5AAE46B63AAE5
```

Artifact verification confirmed:

```text
authority_bytes_equal: True

authority_sha256:
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

signatures_equal: False
```

The two request envelopes therefore differ in signature while preserving identical canonical Authority #2 content.

This relationship is central to the different-provider-key control.

## Authority #2 Provisioning Lineage

Authority #2 used a dedicated generated provisioner.

Original provisioner source:

```text
main\ESP_LOCAL_006_AUTH2_PROVISIONER.c
```

Source SHA-256:

```text
EFF601F71E71DB9AED8FC6E6849A4CD6DB238CB2F3FAED75F14E4BE52B2E3F2C
```

Compiled provisioner binary SHA-256:

```text
D465219F6460DEE4A69381221F93EDE09BD2D82C67025425B2B5E9515864C0D8
```

Those artifacts are not included in the public ESP-LOCAL-006 package.

After provisioning, the persistent-state partition was read directly before the wrong-provider / trusted-provider sequence.

Published pre-test capture:

```text
evidence/ESP_LOCAL_006_AUTH2_UNSPENT.bin
```

SHA-256:

```text
7529911EE67A9702F2769BB5AFDCAF40481BF3C8E601F0E508BAA62478F4D80C
```

The parsed state showed Authority #2 as `UNSPENT`.

After trusted execution and replay testing, the partition was read directly again.

Published post-test capture:

```text
evidence/ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin
```

SHA-256:

```text
F807BC6493E7D2F2CE33EB72A550E5F9ECA2597C3DD83EE9AB0D60E721EA528C
```

The parsed state showed the same Authority #2 identifier as `SPENT`.

## Persistent-State Capture Lineage

The published persistent-state images are direct raw reads of the dedicated endpoint NVS partition.

Partition parameters:

```text
label:  nuvl_state
offset: 0x110000
length: 0x6000
size:   24576 bytes
```

Published captures:

```text
evidence/ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin
evidence/ESP_LOCAL_006_AUTH2_UNSPENT.bin
evidence/ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin
```

These files are raw binary partition images.

They are not text transcripts.

The Auth2 pre-test and post-test images have different SHA-256 values.

The hash difference establishes that the binary images differ.

The specific `UNSPENT` to `SPENT` interpretation comes from parsing the state records, preserving the authority identifier, and validating the NVS page CRC rather than from the partition hashes alone.

## Hostile Relay Lineage

The hostile relay was developed and executed on a Raspberry Pi 3.

Original relay path on the Pi:

```text
/home/seth/ESP_LOCAL_006/relay/esp_local_006_hostile_relay.py
```

Published copy:

```text
relay/esp_local_006_hostile_relay.py
```

Original tested SHA-256:

```text
61684936844297A11895218EB78630196BA2EC74BE1E5399F6F629AF012E66F4
```

The publication copy was transferred from the Pi and verified against the original tested hash before publication staging.

The relay implemented:

- pass-through,
- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` mutation,
- replay capability,
- per-transaction JSONL logging.

The relay retained the original provider signature after mutation and did not possess the trusted provider private key.

## Relay Host Baseline Lineage

The Raspberry Pi 3 baseline was preserved as:

```text
evidence/ESP_LOCAL_006_PI3_BASELINE.txt
```

Original path:

```text
/home/seth/ESP_LOCAL_006/evidence/ESP_LOCAL_006_PI3_BASELINE.txt
```

Original SHA-256:

```text
14A18FC971B79CB479751E88AD39BDE3391C0D40BDAB49D7D40BECD40B9E49D5
```

The publication copy was transferred from the Pi and verified against that hash before staging.

## Relay Evidence Lineage

The Authority #1 relay sequence was frozen on the Pi as:

```text
/home/seth/ESP_LOCAL_006/evidence/ESP_LOCAL_006_RELAY_AUTH1.jsonl
```

Published as:

```text
evidence/ESP_LOCAL_006_RELAY_AUTH1.jsonl
```

Record count:

```text
8
```

Original frozen SHA-256:

```text
CCAC98462DA0708A463ECC1328A5C01CD0B77F0566E1260F9E70237B0F43B659
```

The Authority #2 relay sequence was frozen separately as:

```text
/home/seth/ESP_LOCAL_006/evidence/ESP_LOCAL_006_RELAY_AUTH2.jsonl
```

Published as:

```text
evidence/ESP_LOCAL_006_RELAY_AUTH2.jsonl
```

Record count:

```text
3
```

Original frozen SHA-256:

```text
27A63A71289A49E9B44DF57ACCE8A065D4F1CBA2A5B697E4314B4CBF2982A0DA
```

Both publication copies were transferred from the Pi and verified against the frozen test-time hashes before staging.

## Independent Witness Lineage

The independent witness was a separate ESP32-S3 DevKit running MicroPython.

The tested physical mapping was:

```text
Servo #2 / endpoint GPIO5
        ↓
Witness GPIO4
```

The witness was connected through COM8.

Published witness implementation:

```text
witness/ESP_LOCAL_006_WITNESS_GPIO4.py
```

Publication-stage SHA-256:

```text
CEF567D1778F648904C6C3410381B96FFA0938E7D86E483D286FDABE0EE3CAA3
```

The witness implementation measures positive pulse width using MicroPython `time_pulse_us()` and reports observations as:

```text
PWM_HIGH_US <width>
```

The witness is external to the endpoint authorization decision.

It does not generate, validate, consume, or modify provider authority.

It observes the electrical PWM command line only.

## Endpoint Transcript Lineage

The live COM15 endpoint session was observed interactively during ESP-LOCAL-006.

The serial-monitor output was not redirected to a raw log file during the original run.

Selected terminal lines preserved from the live session were later assembled into:

```text
evidence/ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt
```

Publication-stage SHA-256:

```text
17D7C4F5C1C8AFF3BD5BEAC42116D92ED7B7C431D4BC78FAC10BB12B909524CA
```

This file is a curated derivative.

It is not represented as an original raw serial log.

Its hash identifies the curated publication artifact itself and does not represent the unavailable original terminal stream.

## Witness Transcript Lineage

The live COM8 witness output was observed interactively during ESP-LOCAL-006.

The witness output was not redirected to a raw log file during the original run.

Preserved terminal output was later assembled into:

```text
evidence/ESP_LOCAL_006_WITNESS_COM8_CURATED.txt
```

Publication-stage SHA-256:

```text
5B768366307449D2C6694A15A50C271B2CCC217FA7C0AEE0BA9F451EE209C378
```

This file is a curated derivative.

It retains:

- the two observed `1 µs` Auth1 transients,
- the Auth1 servo-valid pulse sequence,
- the Auth2 servo-valid pulse sequence,
- the absence-of-second-burst observations associated with replay controls.

It is not represented as an original raw redirected serial log.

Its hash identifies the curated publication artifact.

## Artifact Classification

The published ESP-LOCAL-006 package contains several distinct artifact classes.

| Artifact class | Provenance classification | Purpose |
|---|---|---|
| `relay/*.py` | Original tested source / publication copy | Hostile intermediary implementation |
| `witness/*.py` | Tested witness implementation / publication copy | Independent PWM observation |
| `provider/*.txt` | Provider-generated test artifact | Frozen authority metadata |
| `provider/*.json` | Provider-generated test artifact | Signed request envelopes |
| `provider/*.pem` | Test public-key material | Wrong-provider verification material |
| `evidence/*.jsonl` | Original test-time evidence | Relay transaction sequence |
| `evidence/*_STATE*.bin` / authority `.bin` captures | Original binary evidence | Raw persistent-state partition state |
| `evidence/*_CURATED.txt` | Curated derivative | Preserved terminal observations |
| `evidence/ESP_LOCAL_006_PI3_BASELINE.txt` | Original environment record | Relay-host baseline |

Curated derivatives are explicitly identified and do not inherit hashes from the source terminal sessions.

## Tested but Unpublished Artifacts

Several implementation artifacts were required for the test but are intentionally not included in the public package.

These include:

```text
main/ESP_LOCAL_006.c
main/ESP_LOCAL_006_PROVISIONER.c
main/ESP_LOCAL_006_AUTH2_PROVISIONER.c
build*/ESP_LOCAL_006.bin
provider/ESP_LOCAL_006_WRONG_PROVIDER_PRIVATE.pem
```

The wrong-provider private key is omitted because the signed negative-control request and corresponding public key preserve the tested relationship without requiring publication of private signing material.

Persistence-boundary implementation source and binaries are omitted under the established NUVL publication boundary.

Their omission does not change the provenance of the published test evidence.

## Excluded Troubleshooting Artifact

The following local artifact was retained during setup diagnostics but intentionally excluded from the curated publication package:

```text
ESP_LOCAL_006_PREPROVISION_UNEXPECTED_STATE.bin
```

It resulted from an intermediate provisioning diagnostic condition and was not part of the scored ESP-LOCAL-006 test matrix.

It is therefore retained locally rather than represented as scored evidence.

## Publication Relationship

The ESP-LOCAL-006 publication package distinguishes between byte-preserved tested artifacts and publication-created derivatives.

For byte-preserved tested artifacts, the publication copy is expected to match the frozen local/test-time SHA-256 where such a hash was established.

For curated terminal transcripts, the published file is a derivative artifact with its own publication-stage SHA-256.

A hash from an original artifact is not assigned to a modified, renamed-with-content-change, reconstructed, or curated derivative.

`SHA256SUMS.txt` records the hashes of the files actually published in the ESP-LOCAL-006 tree.

## Evidence Relationship

The publication preserves distinct evidence layers:

```text
provider authority artifact
        ↓
hostile relay transaction evidence
        ↓
endpoint decision observation
        ↓
persistent-state capture
        ↓
independent PWM observation
```

These artifacts are preserved separately so that no single observation source is treated as the sole evidence for the complete result.

The provider artifacts establish the authority and signature material presented.

The relay JSONL files establish intermediary handling.

The endpoint curated transcript preserves the observed endpoint decision sequence.

The raw partition images preserve persistent-state conditions.

The independent witness transcript preserves observed PWM behavior.

## Reproduction and Interpretation

Reproduction should preserve the distinction between:

- trusted provider authority generation,
- hostile relay behavior,
- endpoint-local recognition and enforcement,
- persistent single-use state,
- independent physical-command observation.

A relay timeout or transport failure should not be classified as an endpoint authorization denial unless the request reaches the endpoint and exercises the validation path.

A persistent-state partition hash difference should not, by itself, be interpreted as proof of a specific field transition.

A curated terminal transcript should not be represented as a raw capture.

A physical PWM witness should not be represented as proof of guaranteed mechanical servo movement.

Observed outcomes are documented in:

```text
RESULTS.md
```

Published artifact integrity is documented in:

```text
SHA256SUMS.txt
```
