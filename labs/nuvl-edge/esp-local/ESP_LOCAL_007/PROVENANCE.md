# ESP-LOCAL-007 Provenance

This document records the provenance of the principal artifacts used to reproduce, execute, and evaluate ESP-LOCAL-007.

ESP-LOCAL-007 tests concurrent presentation of a provider-issued single-use authority at an ESP32-S3 endpoint. The final scored run is **R003, executed 2026-09-23**.

## Test lineage

ESP-LOCAL-007 extends the enforcement path established in ESP-LOCAL-006.

The provider authority semantics remain:

~~~text
provider-issued
Ed25519 signed
endpoint verified
endpoint locally consumed
max_uses = 1
~~~

ESP-LOCAL-007 changes the request-dispatch condition so multiple accepted TCP clients can enter the existing enforcement path concurrently.

The test variable is concurrent presentation, not a new authority model.

## Tested endpoint

~~~text
device_id: esp32-xiao-servo-02
endpoint:  192.168.0.186:19061
platform:  ESP32-S3
servo:     Servo #2
servo GPIO: 5
~~~

The endpoint runtime is derived from ESP-LOCAL-006.

Exact ESP-LOCAL-006 source SHA-256:

~~~text
4bd962535c61c17ad093973dbb720a99cd709d626d3e9eeff1ad51b6e6e6aaff
~~~

ESP-LOCAL-006 runtime binary SHA-256:

~~~text
21376cdd12d63d2f0e8362c969c7268be56a701ecb3c78bac712564d5fbe5e75
~~~

ESP-LOCAL-007 concurrent runtime source SHA-256:

~~~text
179029cb805fa93ca593f1433454311b4640a8aca0421228c88a8cffda9cf356
~~~

Concurrent source diff SHA-256:

~~~text
4e387fc018e17b7d50384c2b6bfd4bda4be5764742f26b799355b38d8398281a
~~~

Exact R003 concurrent runtime binary SHA-256:

~~~text
6266f600f1d463b0d73878374fad178cae62497dbf38854e4df92a69a44b4abf
~~~

The tested binary itself is withheld because the ESP-IDF application image contains the lab Wi-Fi password compiled from `local_wifi_config.h`.

Its hash is retained to identify the exact binary used for the scored run.

The published source, build configuration, and sanitized Wi-Fi configuration template provide the reproduction material.

## Provider lineage

The provider uses the existing ESP-LOCAL test Ed25519 keypair.

Trusted raw provider public key:

~~~text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
~~~

Trusted private-key file SHA-256:

~~~text
da0a36f274efc6e3ce1c7643800b952b1aa2895201e5a6d6852d308729466509
~~~

The test keypair is retained in the published provider directory for reproduction.

The provider private key is used to originate signed authority. The endpoint enforcement path uses the corresponding public verification material and does not require possession of the provider private key.

## AUTH1 lineage

AUTH1 was the original single-use authority used during the earlier ESP-LOCAL-007 contention work.

~~~text
device_id: esp32-xiao-servo-02
context:   esp_local_006
action:    move_servo
max_uses:  1
nonce:     55dff5bbd9cab62835036cdd1b5a04e7
~~~

AUTH1 authority ID:

~~~text
5204cc275cbb67009025c7d4d84f2594b8f678b09092d091ca44576f0415a904
~~~

AUTH1 request SHA-256:

~~~text
11bfcf671dc64a65dc31d361b863e98ed8f37604f3b90b06fb67e39ef70a5c44
~~~

AUTH1 was consumed during R001.

The resulting R001 SPENT state was archived before AUTH2 was provisioned. It is retained under:

~~~text
evidence/controls/R001_spent_state.bin
~~~

R001 is retained as `INCONCLUSIVE_WITNESS_CAPTURE`: endpoint enforcement produced the expected at-most-once result, but the original physical witness did not capture the servo burst with sufficient fidelity to satisfy the independent witness criterion.

## AUTH2 lineage

A fresh authority was generated for the final scored run rather than attempting to reuse the already-consumed AUTH1.

AUTH2:

~~~text
device_id: esp32-xiao-servo-02
context:   esp_local_006
action:    move_servo
max_uses:  1
nonce:     b3e5571eee07d3e37ca757b54a549a3e
~~~

Canonical authority:

~~~json
{"action":"move_servo","context":"esp_local_006","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"b3e5571eee07d3e37ca757b54a549a3e"}
~~~

Authority ID:

~~~text
066fd59f04ba90f1476ea388a84e125a349a54435552205c0aaa6d5adfa14545
~~~

Signature:

~~~text
oD/gud28uD5tCy2yRURfVEsejixcJ4FClJ2222fhaJNGKuDf4/6e2/sjpxTbNyay7PbujCweZD9b62uvO/0MAA==
~~~

AUTH2 request SHA-256:

~~~text
55f4380f4f50b2c68e6b4dfd1cb6e9b405fb938a498ae680ff36a5d248fc236a
~~~

AUTH2 generation-record SHA-256:

~~~text
867740e115664e4031b1a9be2f97c06e074d8c0133aa9213719912b06501b651
~~~

The exact provider artifacts are retained as:

~~~text
provider/ESP_LOCAL_007_AUTH2_REQUEST.json
provider/ESP_LOCAL_007_AUTH2.txt
~~~

Both R003 requesters presented the same AUTH2 request. No second authority was generated for the competing requester.

## AUTH2 provisioning

AUTH2 was installed into the endpoint's dedicated `nuvl_state` partition using the explicit AUTH2 provisioner.

The provisioner writes one `UNSPENT` state record and refuses to overwrite an existing authority-state record.

Provisioner source SHA-256:

~~~text
939c8eaa6fa5266e8741dd92d7dea85129449c396ba3ebcaad044fa9a7ae42e3
~~~

Before AUTH2 provisioning, the R001 SPENT AUTH1 state was archived and the dedicated authority-state partition was deliberately erased.

After provisioning, AUTH2 was reread and verified as durably `UNSPENT` before the concurrent runtime was installed.

The concurrent runtime itself is authority-agnostic with respect to AUTH1 and AUTH2. AUTH2 is selected through the provisioned persistent state, not through an AUTH2-specific runtime build.

## Pre-race persistent state

The raw `nuvl_state` partition was captured before the scored R003 release.

Artifact:

~~~text
evidence/nuvl_state_pre_race_UNSPENT.bin
~~~

SHA-256:

~~~text
38327e63133030933c23b8d5d816fa85729a4aeb48f3e14fc3e71ee9fb35340f
~~~

The partition contained the valid AUTH2 authority ID in the `UNSPENT` state.

## Post-race persistent state

The raw `nuvl_state` partition was captured after R003.

Artifact:

~~~text
evidence/nuvl_state_post_race_SPENT.bin
~~~

SHA-256:

~~~text
b87b8deba8d08c602af86ff3bac7636a02f0bc8dec5a4401d162b955384d4471
~~~

Firmware reread and independent raw-partition decoding confirmed AUTH2 in the `SPENT` state with a valid record CRC.

## Coordinator provenance

The host coordinator used for ESP-LOCAL-007 is:

~~~text
coordinator/esp_local_007_coordinator.py
~~~

It:

- opens the requester connections;
- requires exact READY from each connection;
- holds requesters at a shared barrier;
- releases identical request bytes;
- records requester timing and responses;
- controls the independent witness run; and
- emits machine-readable JSON evidence.

The R003 coordinator evidence is retained as:

~~~text
evidence/coordinator_R003.json
~~~

R003 recorded:

~~~text
requesters:            2
accepted:              1
denied:                1
errors:                0
release_send_skew_ns:  42700
~~~

The denied requester returned:

~~~text
state_invalid
~~~

The accepted requester returned:

~~~text
executed
~~~

## Endpoint serial provenance

The endpoint serial record for the scored run is retained as:

~~~text
evidence/endpoint_serial_R003.log
~~~

The R003 sequence records two clients reaching the concurrent request path.

One path reached:

~~~text
006_AUTHORITY_UNSPENT_PASS
006_DURABLE_SPENT_REREAD_PASS
006_PWM_COMMAND_BEGIN
006_PWM_COMMAND_END
006_ACCEPT_EXECUTED
~~~

The competing path encountered:

~~~text
ESP_ERR_NVS_INVALID_HANDLE
006_DENY_STATE_INVALID
~~~

and did not cross the PWM execution boundary.

The serial artifact also contains earlier activity from the same capture session. The scored R003 sequence is the later section containing the one accepted execution and one `state_invalid` denial.

## Witness lineage

The original ESP-LOCAL-007 physical witness used a MicroPython interrupt/Python-queue capture path.

R001 showed that this witness could detect activity but did not capture the physical servo burst completely enough to satisfy the scored independent-witness criterion.

The witness was replaced with an ESP-IDF RMT RX implementation.

The RMT witness:

~~~text
device_id:      esp32-witness-007
platform:       ESP32-S3
observed GPIO:  GPIO4
control:        UDP 19072
capture engine: RMT RX
resolution:     1 MHz
~~~

The witness observes the endpoint Servo #2 GPIO5 signal electrically.

It has no provider key, no authority state, and no authorization role.

## RMT witness validation

Before R003, the RMT witness was validated with a synthetic servo-like signal.

The validation produced:

~~~text
50 servo-valid pulses
1 burst
1 servo-like burst
0 transients
0 capture overflows
0 capture truncations
0 capture errors
~~~

Observed synthetic pulse characteristics were approximately:

~~~text
width:  ~2000 µs
period: ~20000 µs
duration: ~982000 µs
~~~

The temporary GPIO6-to-GPIO4 self-test loopback used during validation was removed before R003.

The witness configuration was checked before the scored run so GPIO4 observed the endpoint rather than the witness's own self-test output.

## Witness evidence provenance

The scored witness run file is:

~~~text
evidence/R_R003.jl
~~~

Witness-computed SHA-256:

~~~text
cad594e3fc18a0baa90f6a11bc789124c21241340329f83be23f50341ba10705
~~~

The complete witness serial capture is:

~~~text
evidence/witness_serial_R003.log
~~~

The raw witness evidence-partition image is:

~~~text
evidence/witness_evidence_R003.bin
~~~

The physical R003 `burst_end` observation records:

~~~text
burst_run:           R003
pulses:              50
width_min_us:        1999
width_max_us:        2000
period_min_us:       20000
period_max_us:       20001
period_out_of_range: 0
servo_like:          true
duration_us:         982013
~~~

Capture overflow, truncation, and error counters remained zero.

## R003 witness-summary timing artifact

The R003 run-level witness summary and raw burst evidence do not initially appear to agree.

`R_R003.jl` records:

~~~text
servo_like_bursts = 0
~~~

The complete witness serial evidence subsequently records the R003 burst as:

~~~text
servo_like = true
pulses = 50
burst_run = R003
~~~

The coordinator issued STOP approximately 29 ms before the witness's 100 ms quiet-gap classifier had closed the active burst.

The run summary was therefore emitted before the burst counters were updated.

The complete burst was captured. The raw `burst_end` event is the authoritative physical-burst record for R003.

This discrepancy is retained as part of the evidence rather than rewritten.

A future coordinator procedure should wait approximately 200 ms after requester completion before issuing STOP. That change was not part of R003.

## Witness storage history

Before the scored R003 collection, existing witness evidence storage was archived and then cleared so the scored run began with clean evidence storage.

The pre-erase witness evidence image is retained as:

~~~text
evidence/controls/witness_preerase_image.bin
~~~

The archive preserves the earlier witness material rather than discarding it during preparation for R003.

## R002 control provenance

R002 was not a scored contention result.

The coordinator still referenced the already-consumed AUTH1 request while the endpoint had been provisioned for AUTH2.

Both requesters therefore presented a valid but non-provisioned authority.

Observed result:

~~~text
accepted: 0
denied:   2
physical execution: 0
~~~

Both were denied for authority-state mismatch.

R002 did not consume AUTH2.

Its coordinator evidence is retained as:

~~~text
evidence/controls/R002_misfire_coordinator.json
~~~

R002 is retained as a setup misfire and useful negative control.

## R003 evidence chain

The principal R003 evidence chain is:

~~~text
provider/ESP_LOCAL_007_AUTH2_REQUEST.json
        |
        | same signed request presented by both requesters
        v
evidence/coordinator_R003.json
        |
        | concurrent release / 1 accepted / 1 denied
        v
evidence/endpoint_serial_R003.log
        |
        | one durable consume / one PWM execution
        v
evidence/witness_serial_R003.log
        |
        | one independently observed servo-like burst
        v
evidence/nuvl_state_post_race_SPENT.bin
        |
        | final AUTH2 state
        v
      SPENT
~~~

The pre-race state is independently preserved in:

~~~text
evidence/nuvl_state_pre_race_UNSPENT.bin
~~~

The witness's persistent evidence is independently preserved in:

~~~text
evidence/R_R003.jl
evidence/witness_evidence_R003.bin
~~~

## Provenance boundary

The published artifacts preserve the relationship between:

- the provider-generated authority;
- the authority ID provisioned into endpoint state;
- the exact tested endpoint runtime identity;
- the coordinator's concurrent release;
- endpoint enforcement observations;
- independent physical witness observations; and
- pre- and post-race persistent state.

The exact tested runtime binary is identified by SHA-256 but withheld because it embeds the real lab Wi-Fi password.

The experiment does not claim provenance beyond the artifacts and configuration recorded here. Rebuilding from the published source with different credentials or build metadata produces a new binary and therefore a different binary hash.
