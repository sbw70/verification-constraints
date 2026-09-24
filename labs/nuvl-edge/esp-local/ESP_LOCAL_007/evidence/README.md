# ESP-LOCAL-007 Evidence

This directory contains the published evidence for ESP-LOCAL-007, the concurrent-requester contention test for endpoint-local bounded authority.

The authoritative scored run is **R003, executed 2026-09-23**.

R003 tested whether two concurrent requesters presenting the same valid, provider-issued single-use authority could cause more than one physical command to escape the endpoint.

## Result

**PASS**

Two requesters presented the same valid authority, AUTH2, with `max_uses = 1`.

Observed result:

- exactly one requester was accepted;
- exactly one requester was denied;
- exactly one endpoint PWM command began and ended;
- exactly one endpoint `ACCEPT_EXECUTED` occurred;
- the losing requester did not cross the PWM execution boundary;
- the independent RMT hardware witness recorded exactly one servo-like physical pulse burst;
- witness capture overflow, truncation, and error counters remained zero;
- the authority was left durably `SPENT`.

The requester release send-start skew recorded by the coordinator was:

~~~text
42.7 µs
~~~

The result establishes at-most-once physical execution under concurrent presentation of the tested single-use provider authority on the tested ESP32-S3 / ESP-IDF / NVS configuration.

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

## R003 evidence set

### `coordinator_R003.json`

Machine-readable coordinator evidence for the scored run.

It records:

- test ID and run ID;
- authority ID;
- endpoint and witness addresses;
- witness state before and after the run;
- witness START and STOP responses;
- both requester connection and READY observations;
- requester release timestamps;
- requester responses;
- accepted and denied counts;
- denial reason; and
- release send-start skew.

The recorded requester result is:

~~~text
accepted_count:       1
denied_count:         1
error_count:          0
denied reason:        state_invalid
release_send_skew_ns: 42700
~~~

The accepted requester returned:

~~~json
{"status":"accepted","reason":"executed"}
~~~

The losing requester returned:

~~~json
{"status":"denied","reason":"state_invalid"}
~~~

### `endpoint_serial_R003.log`

Serial evidence from the endpoint.

The scored R003 section records two concurrent clients becoming ready and both requests reaching the endpoint.

The winning path records:

~~~text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_AUTHORITY_UNSPENT_PASS
006_DURABLE_SPENT_REREAD_PASS
006_PWM_COMMAND_BEGIN
006_PWM_COMMAND_END
006_ACCEPT_EXECUTED
007_CLIENT_COMPLETE fd=56 result=accepted
~~~

The losing path records:

~~~text
Unable to read authority state: ESP_ERR_NVS_INVALID_HANDLE
006_DENY_STATE_INVALID
007_CLIENT_COMPLETE fd=55 result=state_invalid
~~~

The losing requester encountered the state read while the winning execution path had the NVS partition deinitialized during durable consumption. The failure direction was denial.

No second PWM command appears in the scored execution.

The log also retains earlier activity from the same serial capture, including the R002 control/misfire. The scored R003 portion is the later contention sequence ending in one accepted execution and one `state_invalid` denial.

### `R_R003.jl`

Witness run file created by the independent ESP-IDF RMT witness.

It contains the witness's run-scoped JSON-lines record and is retained exactly as produced by the witness.

The witness returned the following SHA-256 digest when the run file was closed:

~~~text
cad594e3fc18a0baa90f6a11bc789124c21241340329f83be23f50341ba10705
~~~

### `witness_serial_R003.log`

Full witness serial capture surrounding R003.

This artifact contains the pulse- and burst-level physical observation needed to interpret the scored run.

The authoritative `burst_end` observation for R003 records:

~~~text
burst_run:            R003
pulses:               50
width_min_us:         1999
width_max_us:         2000
period_min_us:        20000
period_max_us:        20001
period_out_of_range:  0
servo_like:           true
duration:             approximately 982 ms
~~~

The witness therefore independently observed one physical servo-like command burst corresponding to the single accepted endpoint execution.

### `witness_evidence_R003.bin`

Raw 4 MiB image of the witness evidence partition collected for the R003 evidence set.

This preserves the witness-side persistent evidence independently of the exported serial log and extracted run file.

### `nuvl_state_pre_race_UNSPENT.bin`

Raw endpoint `nuvl_state` partition image captured before the scored contention run.

The state was verified before release as one valid `UNSPENT` record for AUTH2.

SHA-256:

~~~text
38327e63133030933c23b8d5d816fa85729a4aeb48f3e14fc3e71ee9fb35340f
~~~

### `nuvl_state_post_race_SPENT.bin`

Raw endpoint `nuvl_state` partition image captured after R003.

The post-race state was independently decoded as a valid `SPENT` record for the same AUTH2 authority ID with matching record integrity information.

SHA-256:

~~~text
b87b8deba8d08c602af86ff3bac7636a02f0bc8dec5a4401d162b955384d4471
~~~

Together, the pre- and post-race partition images preserve the persistent-state transition:

~~~text
AUTH2 UNSPENT
      |
      | concurrent presentation
      v
AUTH2 SPENT
~~~

## Physical witness measurement note

R003 contains an important timing artifact that is retained rather than normalized away.

The witness's run-level `run_end` summary in `R_R003.jl` reports:

~~~text
servo_valid_pulses:  0
bursts:              0
servo_like_bursts:   0
~~~

That summary does **not** mean that the witness failed to observe the physical command.

The full witness serial record contains the completed `burst_end` event for R003:

~~~text
50 valid pulses
1999–2000 µs pulse width
20000–20001 µs period
period_out_of_range = 0
servo_like = true
burst_run = R003
~~~

The coordinator issued STOP approximately 29 ms before the witness's 100 ms quiet-gap interval had closed the active burst. As a result, the run-summary counters were sampled before the burst classifier had finalized the burst.

The raw `burst_end` event is therefore the authoritative physical-burst classification for R003.

The witness captured the complete physical burst. The discrepancy is a coordinator STOP-timing artifact, not a missed physical event or capture failure.

The planned procedural correction is to delay STOP by approximately 200 ms after requester completion so that future run summaries self-corroborate the already captured burst.

That correction was **not** applied retroactively to R003.

## Capture health

The R003 coordinator evidence records the witness before the run with:

~~~text
capture_ready:        true
capture_queue_depth:  0
capture_overflows:    0
capture_truncations:  0
capture_errors:       0
~~~

The witness remained free of recorded capture overflow, truncation, or error faults during the scored observation.

This is significant because ESP-LOCAL-007 R001 had already demonstrated why detecting some signal activity was insufficient: the physical witness had to capture the execution with enough fidelity to support the scored claim.

## Tested runtime binary

`ESP_LOCAL_007_CONCURRENT.bin.WITHHELD.txt` records the identity of the exact endpoint application binary used for R003.

The binary itself is not published because the ESP-IDF build compiled the real Wi-Fi password from `local_wifi_config.h` into the application image.

Tested binary SHA-256:

~~~text
6266f600f1d463b0d73878374fad178cae62497dbf38854e4df92a69a44b4abf
~~~

The source and `sdkconfig` are the reproduction artifacts.

A reproduction build using different Wi-Fi credentials or different compile-time metadata is not expected to reproduce the binary hash above. The hash identifies the exact tested build.

## Controls and prior runs

The `controls/` directory preserves evidence that is relevant to the development and interpretation of the final R003 result but is not itself the scored R003 evidence set.

### R001

R001 established the endpoint-side contention behavior:

- exactly one requester accepted;
- exactly one requester denied;
- exactly one endpoint PWM execution;
- final authority state `SPENT`.

Its original MicroPython witness did not capture the physical servo burst with sufficient fidelity to satisfy the independent witness criterion.

R001 is therefore classified as:

~~~text
INCONCLUSIVE_WITNESS_CAPTURE
~~~

It is not classified as an endpoint contention failure.

`controls/R001_spent_state.bin` preserves the post-R001 spent authority state.

### R002

R002 was a test misfire retained as a negative control.

The coordinator presented the already-spent AUTH1 request while the endpoint had been provisioned for AUTH2.

Both requests were denied with an authority-state mismatch and no physical command executed.

R002 therefore demonstrates that presentation of the valid but non-provisioned authority did not consume or execute AUTH2.

The coordinator record is retained as:

~~~text
controls/R002_misfire_coordinator.json
~~~

R002 is not counted as the scored contention run.

### Witness pre-erase image

`controls/witness_preerase_image.bin` preserves the witness evidence partition before it was cleared for the final R003 evidence collection.

The witness evidence storage had accumulated prior validation material. It was archived before clearing the evidence partition so R003 could begin with clean witness storage while preserving the previous data.

## Evidence interpretation

No single artifact is sufficient to establish the complete R003 result.

The scored conclusion is supported by correlation across independent evidence domains:

| Evidence domain | Artifact | Observation |
|---|---|---|
| Requester coordination | `coordinator_R003.json` | 1 accepted, 1 denied, 42.7 µs release skew |
| Endpoint enforcement | `endpoint_serial_R003.log` | one durable consumption path, one denial, one PWM execution |
| Physical observation | `witness_serial_R003.log` | one 50-pulse servo-like burst |
| Witness run record | `R_R003.jl` | run identity, timing anchors, capture-health evidence |
| Witness persistent evidence | `witness_evidence_R003.bin` | raw witness evidence partition |
| Pre-race authority state | `nuvl_state_pre_race_UNSPENT.bin` | AUTH2 `UNSPENT` before contention |
| Post-race authority state | `nuvl_state_post_race_SPENT.bin` | AUTH2 `SPENT` after contention |
| Runtime identity | `ESP_LOCAL_007_CONCURRENT.bin.WITHHELD.txt` | SHA-256 identity of exact tested endpoint build |

The coordinator's TCP result alone is not treated as proof of at-most-once physical execution.

The endpoint log establishes the execution path.

The independent witness establishes the observed physical output.

The raw state images establish the persistent authority state surrounding the contention event.

## Claim boundary

ESP-LOCAL-007 R003 establishes, for the tested configuration:

> A single-use provider-issued authority subjected to concurrent presentation resulted in at most one physical execution, with the authority durably consumed and the physical event independently corroborated.

The result does **not** establish:

- resistance to provider private-key theft;
- security after compromise of endpoint firmware;
- denial-of-service resistance or availability;
- protection against tampering with or rollback of persistent state;
- time-based authority validity or expiry;
- a persistence guarantee independent of the tested storage stack; or
- correctness for arbitrary hardware, firmware, storage, or concurrency implementations.

R003 is evidence for the specific bounded-authority property and configuration tested. It is not a general claim that concurrent embedded execution is race-free.

## Result history

~~~text
R001  endpoint enforcement passed; physical witness inconclusive
R002  misfire retained as negative control; no execution
R003  scored PASS; endpoint enforcement and independent physical witness agree
~~~

R003 supersedes R001 as the scored ESP-LOCAL-007 contention result while preserving R001 and R002 as part of the experimental record.
