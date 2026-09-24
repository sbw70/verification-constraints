# ESP-LOCAL-007 Coordinator Tools

This directory contains the host-side coordination and verification utilities used by ESP-LOCAL-007.

The tools in this directory do not implement provider authority or endpoint enforcement. They coordinate concurrent requester release, inspect persistent-state evidence, and verify the independent witness configuration.

## Files

### `esp_local_007_coordinator.py`

Host-side coordinator for the concurrent-requester contention test.

The coordinator:

1. Opens multiple TCP requester connections to the endpoint.
2. Waits for the exact ESP-LOCAL-007 `READY` response from every requester connection.
3. Holds all armed requester threads at a shared barrier.
4. Releases identical request bytes to all requesters as closely together as the host scheduler permits.
5. Captures each endpoint response and associated timestamps independently.
6. Starts, marks, and stops the independent witness run over its UDP control interface.
7. Calculates requester send-start skew.
8. Writes the coordinator observations to a machine-readable JSON evidence file.

The default mode is a rehearsal. It sends a deliberately malformed request that is rejected before authority consumption.

A live authority is sent only when `--live` is supplied. Before a live run, the coordinator computes the authority ID from the exact canonical authority bytes in the request file and requires that ID to be typed back before release.

Example rehearsal:

~~~powershell
python esp_local_007_coordinator.py --run-id RH003
~~~

Example live run:

~~~powershell
python esp_local_007_coordinator.py --run-id R003 --live
~~~

The default live request file is:

~~~text
../provider/ESP_LOCAL_007_AUTH2_REQUEST.json
~~~

The coordinator requires this exact endpoint READY object:

~~~json
{"ready":true,"test":"ESP_LOCAL_007"}
~~~

If any requester does not receive that exact object, the shared barrier is aborted and no coordinated request release occurs.

Coordinator evidence is written as:

~~~text
ESP_LOCAL_007_COORDINATOR_<RUN_ID>_<unix-time>.json
~~~

The coordinator's accepted/denied counts are network-level observations. They do not by themselves establish physical execution or final persistent state.

---

### `decode_nuvl_state.py`

Offline decoder for a raw `nuvl_state` partition dump.

The utility scans the entire partition image for the NUVL state-record magic value rather than assuming that NVS placed the record at a fixed offset.

For each candidate record it decodes and reports:

- magic;
- record version;
- authority state;
- reserved byte;
- 32-byte authority ID;
- stored CRC-32; and
- independently computed CRC-32.

Recognized authority states are:

~~~text
1 = UNSPENT
2 = SPENT
~~~

The record format decoded by this utility is:

~~~text
uint32_t magic
uint16_t version
uint8_t  state
uint8_t  reserved
uint8_t  authority_id[32]
uint32_t crc32
~~~

CRC verification uses standard reflected CRC-32 over the first 40 bytes of the record, matching the firmware state-record validation.

Usage:

~~~powershell
python decode_nuvl_state.py <partition-dump.bin>
~~~

This utility provides an independent host-side interpretation of raw persistent-state evidence. It does not modify the partition image.

---

### `witness_loopback_check.py`

Pre-race witness wiring check.

This utility verifies that the temporary GPIO6-to-GPIO4 loopback used during witness validation has been removed before a scored run.

It:

1. Requests witness `STATUS`.
2. Starts a witness run named `LOOPCHK`.
3. Requests the witness `SELFTEST`.
4. Allows the self-test pulse train to complete.
5. Stops the witness run.
6. Directs evaluation to the witness's own `run_end` record.

Interpretation:

~~~text
servo_like_bursts = 0
    GPIO6 self-test loopback is removed.
    GPIO4 is not observing the witness's own test output.

servo_like_bursts >= 1
    GPIO6 remains connected to GPIO4.
    The scored witness configuration has not been restored.
~~~

The utility sends no request to the endpoint and presents no authority. It is a witness-configuration check only.

Usage:

~~~powershell
python witness_loopback_check.py
~~~

The witness serial evidence remains authoritative for the observed `run_end` result; the script prints the UDP command replies so the control sequence can also be verified.

---

### `witness_probe.py`

Non-invasive witness activity probe.

This utility polls the witness `STATUS` endpoint five times at approximately one-second intervals and reports:

- `pulse_seq`;
- `queue_depth`;
- `queue_drops`; and
- witness connection state.

Usage:

~~~powershell
python witness_probe.py
~~~

The probe is used to distinguish continuing electrical activity on the witness input from a static or one-time transition.

It does not contact the endpoint, send an authority, start a scored run, or alter endpoint persistent state.

Because it only requests witness status, it can be run repeatedly during witness diagnostics.

## Network configuration

The published tools use the tested ESP-LOCAL-007 lab addresses:

~~~text
Endpoint
192.168.0.186:19061 TCP

Witness
192.168.0.216:19072 UDP
~~~

These addresses identify the tested lab configuration and may be changed when reproducing the test on a different network.

## Role separation

The four utilities have distinct roles:

| File | Role | Sends authority | Modifies endpoint state |
|---|---|---:|---:|
| `esp_local_007_coordinator.py` | Concurrent request release and evidence capture | Live mode only | Only through normal endpoint processing |
| `decode_nuvl_state.py` | Offline persistent-state decoding | No | No |
| `witness_loopback_check.py` | Witness wiring/self-test verification | No | No |
| `witness_probe.py` | Witness status/activity polling | No | No |

None of these host-side utilities can originate or enlarge provider-issued authority. Authority acceptance and durable consumption remain endpoint enforcement functions; the witness remains independent of the authority path.
