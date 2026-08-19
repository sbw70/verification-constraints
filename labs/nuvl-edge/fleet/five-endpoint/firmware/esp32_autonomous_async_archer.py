import gc
import json
import network
import socket
import time
from machine import Pin
from neopixel import NeoPixel

SSID = "YOUR SSID"
PASSWORD = "YOUR PASSWORD"

PI_IP = "192.168.0.94"
NUVL_PORT = 8089
COORD_PORT = 19052
CONTEXT = "field_led_demo"

LED_PIN = 48
WIFI_PM_MODE = network.WLAN.PM_NONE

# FLEET-006 autonomous asynchronous schedules.
# Each endpoint has a different base interval.
SCHEDULES_MS = {
    "esp32-field-01": 2000,
    "esp32-s3-02": 3000,
    "esp32-s3-03": 5000,
}

# Add 0..JITTER_MAX_MS to each base interval.
JITTER_MAX_MS = 750

COLORS = {
    "off": (0, 0, 0),
    "idle": (0, 0, 25),
    "created": (25, 18, 0),
    "waiting": (18, 0, 25),
    "accept": (0, 25, 0),
    "deny": (25, 0, 0),
    "fail": (20, 20, 20),
    "stale": (25, 8, 0),
}


def read_device_id():
    with open("device_id.txt", "r") as f:
        value = f.read().strip()

    if not value:
        raise RuntimeError("device_id_missing")

    return value


def led(np, state):
    np[0] = COLORS[state]
    np.write()


def connect_wifi(np):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=WIFI_PM_MODE)

    if wlan.isconnected():
        return wlan

    wlan.connect(SSID, PASSWORD)

    for _ in range(30):
        if wlan.isconnected():
            return wlan
        time.sleep_ms(500)

    led(np, "fail")
    raise OSError("wifi_not_connected")


def send_all(sock, data):
    offset = 0

    while offset < len(data):
        sent = sock.send(data[offset:])

        if sent is None:
            sent = 0

        if sent <= 0:
            raise OSError("socket_send_failed")

        offset += sent


def ms_from_us(value):
    return round(value / 1000, 3)


def http_json(
    method,
    port,
    path,
    payload=None,
    timeout=5,
    return_timing=False,
):
    total_start = time.ticks_us()

    body = b"" if payload is None else json.dumps(payload).encode()

    request = (
        "{} {} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(
        method,
        path,
        PI_IP,
        len(body),
    ).encode() + body

    address_start = time.ticks_us()
    addr = socket.getaddrinfo(PI_IP, port)[0][-1]
    address_complete = time.ticks_us()

    sock = socket.socket()
    sock.settimeout(timeout)

    try:
        connect_start = time.ticks_us()
        sock.connect(addr)
        connect_complete = time.ticks_us()

        send_start = time.ticks_us()
        send_all(sock, request)
        send_complete = time.ticks_us()

        first_byte_start = time.ticks_us()
        first_chunk = sock.recv(512)
        first_byte_complete = time.ticks_us()

        chunks = []

        if first_chunk:
            chunks.append(first_chunk)

        receive_rest_start = time.ticks_us()

        while first_chunk:
            chunk = sock.recv(512)

            if not chunk:
                break

            chunks.append(chunk)

        receive_complete = time.ticks_us()
        raw = b"".join(chunks)

    finally:
        sock.close()

    parse_start = time.ticks_us()

    marker = raw.find(b"\r\n\r\n")

    if marker < 0:
        raise ValueError("invalid_http_response")

    parsed = json.loads(raw[marker + 4:].decode())
    parse_complete = time.ticks_us()

    timing = {
        "address_ms": ms_from_us(
            time.ticks_diff(
                address_complete,
                address_start,
            )
        ),
        "connect_ms": ms_from_us(
            time.ticks_diff(
                connect_complete,
                connect_start,
            )
        ),
        "send_ms": ms_from_us(
            time.ticks_diff(
                send_complete,
                send_start,
            )
        ),
        "first_byte_wait_ms": ms_from_us(
            time.ticks_diff(
                first_byte_complete,
                first_byte_start,
            )
        ),
        "receive_rest_ms": ms_from_us(
            time.ticks_diff(
                receive_complete,
                receive_rest_start,
            )
        ),
        "response_parse_ms": ms_from_us(
            time.ticks_diff(
                parse_complete,
                parse_start,
            )
        ),
        "http_total_ms": ms_from_us(
            time.ticks_diff(
                parse_complete,
                total_start,
            )
        ),
    }

    if return_timing:
        return parsed, timing

    return parsed


def next_jitter_ms():
    # Local bounded jitter without requiring a coordinator.
    return time.ticks_us() % (JITTER_MAX_MS + 1)


def make_transaction_id(device_id, counter):
    return "{}-{}-{}".format(
        device_id,
        time.ticks_ms(),
        counter,
    )


def post_nuvl(device_id, mode, transaction_id):
    nonce = "{}-{}-{}".format(
        device_id,
        transaction_id,
        time.ticks_us(),
    )

    response, timing = http_json(
        "POST",
        NUVL_PORT,
        "/nuvl",
        {
            "device_id": device_id,
            "context": CONTEXT,
            "requested_action": mode,
            "nonce": nonce,
        },
        timeout=6,
        return_timing=True,
    )

    return nonce, response, timing


def report_result(result):
    try:
        http_json(
            "POST",
            COORD_PORT,
            "/result",
            result,
            timeout=4,
        )

        return True

    except Exception as exc:
        print(
            "RESULT_REPORT_FAILED transaction_id={} "
            "device_id={} error={}".format(
                result.get("run_id"),
                result.get("device_id"),
                repr(exc),
            )
        )

        return False


def main():
    gc.collect()

    device_id = read_device_id()

    if device_id not in SCHEDULES_MS:
        raise RuntimeError(
            "unknown_autonomous_device_id:{}".format(
                device_id
            )
        )

    base_interval_ms = SCHEDULES_MS[device_id]

    np = NeoPixel(Pin(LED_PIN, Pin.OUT), 1)
    led(np, "idle")

    wlan = connect_wifi(np)
    endpoint_ip = wlan.ifconfig()[0]

    print(
        "FLEET006_AUTONOMOUS_READY "
        "device_id={} ip={} base_interval_ms={} "
        "jitter_max_ms={} wifi_pm=PM_NONE "
        "stage_timing=enabled".format(
            device_id,
            endpoint_ip,
            base_interval_ms,
            JITTER_MAX_MS,
        )
    )

    counter = 0

    # Initial device-specific delay prevents a simultaneous boot
    # from forcing all endpoints into the same first request window.
    initial_delay_ms = (
        base_interval_ms + next_jitter_ms()
    )

    print(
        "FLEET006_INITIAL_DELAY "
        "device_id={} delay_ms={}".format(
            device_id,
            initial_delay_ms,
        )
    )

    time.sleep_ms(initial_delay_ms)

    while True:
        counter += 1

        transaction_id = make_transaction_id(
            device_id,
            counter,
        )

        mode = "accept"

        gc.collect()
        baseline_free = gc.mem_free()

        led(np, "created")
        time.sleep_ms(100)
        led(np, "waiting")

        started = time.ticks_ms()

        try:
            nonce, response, stage_timing = post_nuvl(
                device_id,
                mode,
                transaction_id,
            )

            elapsed_ms = time.ticks_diff(
                time.ticks_ms(),
                started,
            )

            decision = response.get("decision")
            reason = response.get("reason")

            if decision == "accepted":
                led(np, "accept")

            elif reason == "stale_replay_malformed":
                led(np, "stale")

            elif decision == "denied":
                led(np, "deny")

            else:
                led(np, "fail")

            result = {
                # Coordinator currently indexes observations by run_id.
                # For FLEET-006 this value is generated locally by
                # the endpoint and is a transaction identifier, not
                # a coordinator-issued release/run identifier.
                "run_id": transaction_id,
                "device_id": device_id,
                "ip": endpoint_ip,
                "decision": decision,
                "reason": reason,
                "elapsed_ms": elapsed_ms,
                "nonce": nonce,
                "autonomous": True,
                "sequence": counter,
                "base_interval_ms": base_interval_ms,
            }

            result.update(stage_timing)

        except Exception as exc:
            elapsed_ms = time.ticks_diff(
                time.ticks_ms(),
                started,
            )

            led(np, "fail")

            result = {
                "run_id": transaction_id,
                "device_id": device_id,
                "ip": endpoint_ip,
                "decision": "unavailable",
                "reason": repr(exc),
                "provider_verified": False,
                "elapsed_ms": elapsed_ms,
                "nonce": None,
                "autonomous": True,
                "sequence": counter,
                "base_interval_ms": base_interval_ms,
            }

        gc.collect()
        result["free_delta"] = (
            gc.mem_free() - baseline_free
        )

        report_ok = report_result(result)

        print(
            "FLEET006_AUTONOMOUS_RESULT "
            "transaction_id={} device_id={} sequence={} "
            "decision={} reason={} elapsed_ms={} "
            "free_delta={} report_ok={}".format(
                transaction_id,
                device_id,
                counter,
                result.get("decision"),
                result.get("reason"),
                result.get("elapsed_ms"),
                result.get("free_delta"),
                report_ok,
            )
        )

        led(np, "idle")

        delay_ms = (
            base_interval_ms + next_jitter_ms()
        )

        print(
            "FLEET006_NEXT_DELAY "
            "device_id={} sequence={} delay_ms={}".format(
                device_id,
                counter,
                delay_ms,
            )
        )

        time.sleep_ms(delay_ms)


main()
