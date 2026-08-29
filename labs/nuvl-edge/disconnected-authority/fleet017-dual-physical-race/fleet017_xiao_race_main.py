"""
FLEET-017 XIAO race firmware.

Both physical boards run this IDENTICAL file.

What differs between the boards:
    device_id.txt  -> holds the PHYSICAL label only ("servo-01" or "servo-02")

What is IDENTICAL between the boards:
    poc005_race_artifact.json  -> the one shared pre-issued single-use artifact
    the /spend payload built from that artifact (byte-for-byte)

Authority identity comes from the artifact's issue_request, NOT from
device_id.txt. device_id.txt is physical labeling for evidence only and is
never placed inside the signed spend request.

Sequence:
    1. connect wifi
    2. load shared artifact, build canonical /spend payload ONCE
    3. poll coordinator /arm until armed, receive relative wait_ms
    4. open socket to boundary and connect (pre-armed)
    5. sleep the remaining wait, then sendall() the prebuilt request
    6. parse decision
    7. ONLY on accepted -> drive servo
    8. report result to coordinator keyed by physical_id
"""

import gc
import json
import machine
import network
import socket
import time
from machine import PWM, Pin

# ---------------------------------------------------------------- config

WIFI_SSID = "YOUR SSID"
WIFI_PASSWORD = "YOUR PASSWORD"

PI_HOST = "192.168.0.94"
BOUNDARY_PORT = 8092          # persistent boundary with /spend
COORDINATOR_PORT = 19053      # FLEET-017 coordinator

ARTIFACT_FILE = "poc005_race_artifact.json"
PHYSICAL_ID_FILE = "device_id.txt"

SERVO_PIN = 5                 # D4 / GPIO5
SERVO_FREQ_HZ = 50
SERVO_ACCEPT_DUTY_U16 = 6554  # matches canonical esp32_xiao_servo_nuvl_archer.py
SERVO_HOLD_MS = 1000

POLL_INTERVAL_MS = 250
SOCKET_TIMEOUT_S = 15

# ---------------------------------------------------------------- helpers


def log(msg):
    print(msg)


def read_physical_id():
    try:
        with open(PHYSICAL_ID_FILE) as handle:
            return handle.read().strip()
    except Exception:
        return "unknown-physical"


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    try:
        wlan.config(pm=network.WLAN.PM_NONE)
    except Exception:
        pass
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        deadline = time.ticks_add(time.ticks_ms(), 20000)
        while not wlan.isconnected():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                raise RuntimeError("wifi_connect_timeout")
            time.sleep_ms(200)
    return wlan.ifconfig()[0]


def canonical_json(obj):
    """
    Match the reference implementation's serialization:
        json.dumps(obj, sort_keys=True, separators=(",", ":"))

    MicroPython's json.dumps has neither sort_keys nor separators, so this
    builds canonical output manually. Both boards must produce byte-identical
    payloads or the race is not testing one shared request.
    """
    if isinstance(obj, dict):
        parts = []
        for key in sorted(obj.keys()):
            parts.append(canonical_json(key) + ":" + canonical_json(obj[key]))
        return "{" + ",".join(parts) + "}"
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(canonical_json(item) for item in obj) + "]"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if obj is None:
        return "null"
    if isinstance(obj, (int, float)):
        return json.dumps(obj)
    return json.dumps(obj)


def parse_http_body(raw):
    marker = raw.find(b"\r\n\r\n")
    if marker < 0:
        raise ValueError("invalid_http_response")
    return json.loads(raw[marker + 4:].decode("utf-8"))


def http_get_json(host, port, path):
    request = (
        "GET {} HTTP/1.1\r\n"
        "Host: {}:{}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(path, host, port).encode("ascii")

    sock = socket.socket()
    sock.settimeout(SOCKET_TIMEOUT_S)
    try:
        sock.connect(socket.getaddrinfo(host, port)[0][-1])
        sock.sendall(request)
        chunks = []
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            chunks.append(chunk)
        return parse_http_body(b"".join(chunks))
    finally:
        sock.close()


def http_post_json(host, port, path, obj):
    body = canonical_json(obj).encode("utf-8")
    request = (
        "POST {} HTTP/1.1\r\n"
        "Host: {}:{}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(path, host, port, len(body)).encode("ascii") + body

    sock = socket.socket()
    sock.settimeout(SOCKET_TIMEOUT_S)
    try:
        sock.connect(socket.getaddrinfo(host, port)[0][-1])
        sock.sendall(request)
        chunks = []
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            chunks.append(chunk)
        return parse_http_body(b"".join(chunks))
    finally:
        sock.close()


# ---------------------------------------------------------------- actuator


def drive_servo():
    """
    Physical actuation. Called ONLY from the accepted branch.
    Behavior matches canonical esp32_xiao_servo_nuvl_archer.py actuate_accept().
    Returns (attempted, completed, error_string_or_None).
    """
    servo = None
    try:
        servo = PWM(Pin(SERVO_PIN), freq=SERVO_FREQ_HZ)
        servo.duty_u16(SERVO_ACCEPT_DUTY_U16)
        time.sleep_ms(SERVO_HOLD_MS)
        return (True, True, None)
    except Exception as exc:
        return (True, False, str(exc))
    finally:
        if servo is not None:
            try:
                servo.deinit()
            except Exception:
                pass


# ---------------------------------------------------------------- main


def main():
    physical_id = read_physical_id()
    log("FLEET017_BOOT physical_id={}".format(physical_id))

    ip_addr = connect_wifi()
    log("FLEET017_WIFI ip={}".format(ip_addr))

    with open(ARTIFACT_FILE) as handle:
        record = json.load(handle)

    issue_request = record["issue_request"]
    package = record["package"]

    # Authority identity comes from the artifact, not from this board.
    spend_request = {
        "device_id": issue_request["device_id"],
        "context": issue_request["context"],
        "requested_action": issue_request["requested_action"],
        "nonce": issue_request["nonce"],
    }

    payload_obj = {
        "package": package,
        "spend_request": spend_request,
    }
    payload = canonical_json(payload_obj).encode("utf-8")

    spend_http = (
        "POST /spend HTTP/1.1\r\n"
        "Host: {}:{}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(PI_HOST, BOUNDARY_PORT, len(payload)).encode("ascii") + payload

    log("FLEET017_ARMED_PAYLOAD physical_id={} authority_device_id={} nonce={} bytes={}".format(
        physical_id,
        spend_request["device_id"],
        spend_request["nonce"],
        len(payload),
    ))

    gc.collect()

    # ---- poll for release ----

    run_id = None
    wait_ms = 0
    while True:
        try:
            arm = http_get_json(
                PI_HOST, COORDINATOR_PORT,
                "/arm?physical_id={}".format(physical_id),
            )
        except Exception as exc:
            log("FLEET017_ARM_POLL_ERROR {}".format(exc))
            time.sleep_ms(POLL_INTERVAL_MS)
            continue

        if arm.get("armed"):
            run_id = arm.get("run_id")
            wait_ms = int(arm.get("wait_ms", 0))
            log("FLEET017_RELEASE_RECEIVED physical_id={} run_id={} wait_ms={}".format(
                physical_id, run_id, wait_ms))
            break

        time.sleep_ms(POLL_INTERVAL_MS)

    # ---- pre-connect so only sendall() remains after release ----

    sock = socket.socket()
    sock.settimeout(SOCKET_TIMEOUT_S)
    addr = socket.getaddrinfo(PI_HOST, BOUNDARY_PORT)[0][-1]
    sock.connect(addr)
    log("FLEET017_PRECONNECTED physical_id={}".format(physical_id))

    # ---- burn the remaining wait, then fire ----

    release_at = time.ticks_add(time.ticks_ms(), wait_ms)
    while time.ticks_diff(release_at, time.ticks_ms()) > 0:
        pass  # busy wait for tightest release

    send_start_us = time.ticks_us()

    decision = "unavailable"
    reason = None
    artifact_id = None
    provider_verified = None
    provider_contacted = None
    elapsed_ms = None

    try:
        sock.sendall(spend_http)
        chunks = []
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            chunks.append(chunk)
        elapsed_ms = time.ticks_diff(time.ticks_us(), send_start_us) // 1000
        response = parse_http_body(b"".join(chunks))
        decision = response.get("decision", "unavailable")
        reason = response.get("reason")
        artifact_id = response.get("artifact_id")
        provider_verified = response.get("provider_verified")
        provider_contacted = response.get("provider_contacted_for_spend")
    except Exception as exc:
        elapsed_ms = time.ticks_diff(time.ticks_us(), send_start_us) // 1000
        decision = "unavailable"
        reason = str(exc)
    finally:
        try:
            sock.close()
        except Exception:
            pass

    log("FLEET017_SPEND_RESULT physical_id={} decision={} reason={} artifact_id={} elapsed_ms={}".format(
        physical_id, decision, reason, artifact_id, elapsed_ms))

    # ---- actuator gate: ONLY accepted reaches the servo ----

    actuator_attempted = False
    actuator_completed = False
    actuator_error = None

    if decision == "accepted":
        actuator_attempted, actuator_completed, actuator_error = drive_servo()
        log("FLEET017_ACTUATOR physical_id={} attempted={} completed={} error={}".format(
            physical_id, actuator_attempted, actuator_completed, actuator_error))
    else:
        log("FLEET017_NO_ACTUATOR physical_id={} decision={}".format(
            physical_id, decision))

    # ---- report ----

    result = {
        "physical_id": physical_id,
        "run_id": run_id,
        "authority_device_id": spend_request["device_id"],
        "nonce": spend_request["nonce"],
        "decision": decision,
        "reason": reason,
        "artifact_id": artifact_id,
        "provider_verified": provider_verified,
        "provider_contacted_for_spend": provider_contacted,
        "elapsed_ms": elapsed_ms,
        "send_start_us": send_start_us,
        "endpoint_ip": ip_addr,
        "actuator_attempted": actuator_attempted,
        "actuator_command_completed": actuator_completed,
        "actuator_error": actuator_error,
        "free_mem": gc.mem_free(),
    }

    for attempt in range(5):
        try:
            http_post_json(PI_HOST, COORDINATOR_PORT, "/result", result)
            log("FLEET017_REPORTED physical_id={}".format(physical_id))
            break
        except Exception as exc:
            log("FLEET017_REPORT_ERROR {} attempt={}".format(exc, attempt))
            time.sleep_ms(500)

    log("FLEET017_DONE physical_id={}".format(physical_id))


try:
    main()
except Exception as exc:
    print("FLEET017_FATAL {}".format(exc))
