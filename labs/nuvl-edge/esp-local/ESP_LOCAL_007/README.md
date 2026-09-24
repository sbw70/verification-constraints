# ESP-LOCAL-007 — Concurrent Requesters

**Status:** PASS  
**Scored run:** R003  
**Date:** 2026-09-23  
**Classification:** NUVL core

ESP-LOCAL-007 tests whether a provider-issued single-use authority remains bounded when the same valid authority is presented to an endpoint by multiple requesters concurrently.

Two requesters presented the same valid AUTH2 request with:

~~~text
max_uses = 1
~~~

Exactly one physical command executed.

The independent hardware witness observed exactly one servo-like pulse burst, the competing requester was denied before reaching physical execution, and the authority was left durably `SPENT`.

## Claim under test

The test question is:

> If multiple requesters present the same valid one-use authority concurrently, can more than one physical command escape?

ESP-LOCAL-007 retains the provider and endpoint authority model established by the preceding ESP-LOCAL tests.

The provider originates and signs the authority.

The endpoint verifies and enforces it.

The endpoint cannot originate or enlarge provider-issued authority.

The new variable in ESP-LOCAL-007 is **concurrent presentation**.

## Result

R003 passed every scored criterion.

~~~text
requesters:                  2
same authority:              yes
max_uses:                    1

accepted:                    1
denied:                      1
requester errors:            0

endpoint PWM executions:     1
endpoint ACCEPT_EXECUTED:    1
witness servo-like bursts:   1

final authority state:       SPENT
~~~

Coordinator release send-start skew:

~~~text
42.7 µs
~~~

The result demonstrates at-most-once physical execution under the tested concurrent contention condition.

## Test architecture

~~~text
                         provider
                            |
                     signed authority
                            |
                            v
                    AUTH2 request bytes
                            |
                 +----------+----------+
                 |                     |
             requester 1           requester 2
                 |                     |
                 +----------+----------+
                            |
                    synchronized release
                            |
                            v
                  ESP32-S3 endpoint
                 esp32-xiao-servo-02
                            |
              signature / semantics / state
                            |
                    durable consume
                            |
                            v
                     physical PWM
                            |
                            +--------------------+
                                                 |
                                                 v
                                      independent witness
                                       ESP32-S3 RMT RX
                                            GPIO4
~~~

The coordinator transports the already-issued authority and synchronizes requester release.

It does not issue authority or decide which requester succeeds.

The independent witness has no authorization role. It observes the endpoint's physical servo-control signal electrically.

## Repository layout

~~~text
ESP_LOCAL_007/
├── README.md
├── PROVENANCE.md
├── RESULTS.md
├── coordinator/
├── provider/
├── firmware/
├── witness/
└── evidence/
~~~

### `provider/`

Contains the provider-side generator, test Ed25519 key material, and exact AUTH2 artifacts used for R003.

The provider creates the canonical authority, derives its SHA-256 authority ID, and signs the canonical bytes with the provider private key.

See:

~~~text
provider/README.md
~~~

### `firmware/`

Contains the ESP-IDF concurrent endpoint runtime, explicit AUTH1 and AUTH2 provisioners, partition configuration, build configuration, and cryptographic dependency.

The concurrent runtime retains the existing enforcement path and changes request dispatch so multiple client tasks can enter it concurrently.

No contention mutex is added around the enforcement path.

See:

~~~text
firmware/README.md
~~~

### `coordinator/`

Contains the host-side tools used to coordinate requester release and inspect the test configuration.

The directory includes:

~~~text
esp_local_007_coordinator.py
decode_nuvl_state.py
witness_loopback_check.py
witness_probe.py
~~~

The coordinator requires exact READY from all intended requester connections before releasing the request barrier.

Live execution requires explicit confirmation of the authority ID.

See:

~~~text
coordinator/README.md
~~~

### `witness/`

Contains the ESP-IDF RMT RX independent hardware witness.

The witness observes the endpoint's servo-control signal on GPIO4 and records pulse-level evidence independently of the endpoint.

It has:

~~~text
authority role:      NONE
authorization role:  NONE
~~~

See:

~~~text
witness/README.MD
~~~

### `evidence/`

Contains the scored R003 evidence and retained controls.

Principal R003 artifacts include:

~~~text
coordinator_R003.json
endpoint_serial_R003.log
R_R003.jl
witness_serial_R003.log
witness_evidence_R003.bin
nuvl_state_pre_race_UNSPENT.bin
nuvl_state_post_race_SPENT.bin
ESP_LOCAL_007_CONCURRENT.bin.WITHHELD.txt
~~~

The `controls/` subdirectory preserves prior-run and setup evidence relevant to interpretation of R003.

See:

~~~text
evidence/README.md
~~~

## Authority under test

R003 used AUTH2:

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

Both R003 requesters presented the same signed request bytes.

The test did not issue one authority per requester.

## Endpoint under test

~~~text
device_id:   esp32-xiao-servo-02
platform:    ESP32-S3
address:     192.168.0.186
TCP port:    19061
servo GPIO:  5
~~~

The concurrent runtime is derived from the ESP-LOCAL-006 enforcement implementation.

The significant ESP-LOCAL-007 change is dispatch:

- accepted clients execute in separate FreeRTOS tasks;
- each client reports READY;
- the listener returns immediately to `accept()`;
- requester tasks wait independently for their request bytes; and
- multiple tasks can enter the existing enforcement path concurrently.

No mutex was added around the authority-consumption path because serialization at that point would remove the condition being tested.

## Enforcement order

The endpoint enforcement path retains the existing sequence:

~~~text
Ed25519 signature verification
        |
        v
semantic admissibility
        |
        v
SHA-256 authority identifier
        |
        v
persistent-state load
        |
        v
authority-ID match
        |
        v
require UNSPENT
        |
        v
durable consume -> SPENT
        |
        v
durable SPENT reread
        |
        v
physical PWM execution
~~~

Missing, malformed, wrongly signed, semantically inadmissible, mismatched, invalid, or already-consumed authority state is denied before physical execution.

## Initial state

Before R003, AUTH2 was explicitly provisioned into the endpoint's dedicated `nuvl_state` partition as:

~~~text
UNSPENT
~~~

The raw pre-race partition was preserved as:

~~~text
evidence/nuvl_state_pre_race_UNSPENT.bin
~~~

SHA-256:

~~~text
38327e63133030933c23b8d5d816fa85729a4aeb48f3e14fc3e71ee9fb35340f
~~~

The concurrent application was installed without replacing the provisioned state.

## Concurrent contention

The coordinator established both requester connections and waited for exact endpoint READY messages.

The endpoint recorded:

~~~text
007_CLIENT_READY fd=55
007_CLIENT_READY fd=56
~~~

Both requests then reached the concurrent request path:

~~~text
007_CLIENT_REQUEST_RECEIVED fd=56
007_CLIENT_REQUEST_RECEIVED fd=55
~~~

The winning path reached:

~~~text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_AUTHORITY_UNSPENT_PASS
006_DURABLE_SPENT_REREAD_PASS
006_PWM_COMMAND_BEGIN
006_PWM_COMMAND_END
006_ACCEPT_EXECUTED
~~~

The competing path reached:

~~~text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
Unable to read authority state: ESP_ERR_NVS_INVALID_HANDLE
006_DENY_STATE_INVALID
~~~

The losing requester encountered the state read while the winning durable-consumption path had the NVS partition deinitialized.

The failure direction was denial.

The losing path never crossed the PWM execution boundary.

## Independent physical witness

The scored R003 run used the ESP-IDF RMT witness:

~~~text
device_id:      esp32-witness-007
address:        192.168.0.216
UDP port:       19072
observed GPIO:  4
capture engine: RMT RX
resolution:     1 MHz
~~~

GPIO4 observed the endpoint's Servo #2 GPIO5 output.

The completed R003 physical burst contained:

~~~text
pulses:                50
width_min_us:          1999
width_max_us:          2000
period_min_us:         20000
period_max_us:         20001
period_out_of_range:   0
servo_like:            true
duration_us:           982013
~~~

The witness therefore independently corroborated exactly one physical servo command.

Capture overflow, truncation, and error counters remained zero.

## Witness run-summary note

R003 preserves a timing artifact in the witness evidence.

The run-level `run_end` summary in `R_R003.jl` reports zero servo-like bursts, while the full witness serial evidence contains the completed R003 `burst_end` event with:

~~~text
pulses = 50
servo_like = true
burst_run = R003
~~~

The coordinator issued STOP approximately 29 ms before the witness's 100 ms quiet-gap classifier had closed the burst.

The run summary was therefore emitted before the burst counters were updated.

The physical burst itself was captured completely.

For R003, the raw `burst_end` event is the authoritative physical-burst classification.

A future coordinator procedure should wait approximately 200 ms after requester completion before STOP so the run-level summary self-corroborates the completed burst.

That change was not part of R003.

## Final state

After R003, the endpoint state was verified as:

~~~text
SPENT
~~~

The raw post-race partition is retained as:

~~~text
evidence/nuvl_state_post_race_SPENT.bin
~~~

SHA-256:

~~~text
b87b8deba8d08c602af86ff3bac7636a02f0bc8dec5a4401d162b955384d4471
~~~

The scored transition was therefore:

~~~text
AUTH2 UNSPENT
      |
      | same authority presented concurrently twice
      |
      +---- one request denied
      |
      +---- one durable consume
                    |
                    v
             one physical command
                    |
                    v
               AUTH2 SPENT
~~~

## Prior runs

### R001

R001 produced the expected endpoint-side contention result:

~~~text
accepted:       1
denied:         1
PWM executions: 1
final state:    SPENT
~~~

The original MicroPython witness did not capture the physical burst with sufficient fidelity to satisfy the independent-witness criterion.

R001 is retained as:

~~~text
INCONCLUSIVE_WITNESS_CAPTURE
~~~

It is not classified as an endpoint contention failure.

### R002

R002 was a setup misfire.

The endpoint had been provisioned for AUTH2 while the coordinator still presented the previously consumed AUTH1 request.

Both requests were denied for authority-state mismatch.

~~~text
accepted:           0
denied:             2
physical execution: 0
~~~

AUTH2 was not consumed.

R002 is retained as a negative control rather than a scored contention run.

### R003

R003 corrected the request selection and satisfied the complete scored criteria:

~~~text
same valid AUTH2 presented concurrently
        |
        +---- 1 denied before execution
        |
        +---- 1 accepted
                  |
                  v
            1 physical command
                  |
                  v
           independently witnessed
                  |
                  v
              AUTH2 SPENT
~~~

R003 supersedes R001 as the scored ESP-LOCAL-007 result.

## Evidence model

The PASS determination does not rely on a single software component reporting its own success.

The evidence chain crosses separate observation domains:

| Domain | Evidence |
|---|---|
| Provider | exact signed AUTH2 request and generation record |
| Coordinator | concurrent release and requester responses |
| Endpoint | verification, durable consumption, denial, and execution log |
| Physical witness | independently captured servo waveform |
| Persistent state | raw pre-race `UNSPENT` and post-race `SPENT` partitions |

This separation is intentional.

A requester-level `accepted` response alone is insufficient to establish physical at-most-once execution.

Likewise, an endpoint log claiming one PWM command is not treated as independent physical corroboration.

R003 combines both.

## Exact tested runtime

The exact R003 endpoint binary is identified by SHA-256:

~~~text
6266f600f1d463b0d73878374fad178cae62497dbf38854e4df92a69a44b4abf
~~~

The binary itself is withheld because the ESP-IDF build contains the real lab Wi-Fi password compiled into the application image.

The source, build configuration, partition layout, and sanitized Wi-Fi configuration template are published.

A reproduction build using different Wi-Fi credentials or build metadata is not expected to reproduce the exact binary hash.

## Reproduction outline

The complete procedure is represented by the artifacts in this directory.

At a high level:

1. Build the provider environment and verify the test Ed25519 keypair.
2. Generate or select a fresh single-use authority.
3. Provision its authority ID into the endpoint as `UNSPENT`.
4. Verify the provisioned state by durable reread.
5. Build the ESP-LOCAL-007 concurrent endpoint runtime.
6. Install the runtime without replacing `nuvl_state`.
7. Build and start the RMT witness.
8. Connect endpoint Servo #2 GPIO5 to witness GPIO4.
9. Verify that the temporary witness self-test loopback is removed.
10. Confirm witness capture health.
11. Preserve the pre-race endpoint state.
12. Start endpoint and witness serial logging.
13. Run the coordinator in rehearsal mode before spending the authority.
14. Execute one explicitly armed live contention run.
15. Preserve coordinator, endpoint, witness, and persistent-state evidence.
16. Decode the final endpoint state independently.
17. Correlate requester, endpoint, physical-witness, and state evidence before assigning a result.

The folder-specific READMEs document the corresponding components and artifacts.

## Claim boundary

ESP-LOCAL-007 R003 establishes, for the tested configuration:

> Concurrent presentation of one valid provider-issued single-use authority resulted in at most one physical execution, with the authority durably consumed and the physical execution independently corroborated.

It does not establish:

- resistance to provider private-key theft;
- security after compromise of endpoint firmware;
- denial-of-service resistance;
- availability under contention;
- protection against deliberate persistent-state tampering;
- protection against persistent-state rollback;
- time-based authority validity or expiry;
- persistence guarantees independent of the tested storage stack;
- behavior for arbitrary numbers of simultaneous requesters; or
- correctness across arbitrary hardware, firmware, storage, or scheduler implementations.

The observed losing path failed closed with `state_invalid`. ESP-LOCAL-007 treats that as correct bounded-authority behavior for this test, not as an availability guarantee.

## Supporting documents

`RESULTS.md` records the scored observations and result.

`PROVENANCE.md` records artifact lineage, authority lineage, runtime identity, witness lineage, and evidence relationships.

Folder-specific READMEs document the provider, endpoint firmware, coordinator tools, witness, and evidence set.

The repository evidence is authoritative for the configuration and result reported here.
