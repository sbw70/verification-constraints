import gc
import json
import network
import socket
import time
from machine import Pin, PWM
# XIAO actuator build: no NeoPixel status LED

SSID = "YOUR SSID"
PASSWORD = "YOUR PASSWORD"

PI_IP = "192.168.0.94"
NUVL_PORT = 8089
COORD_PORT = 19052
CONTEXT = "field_led_demo"

LED_PIN = 48
SERVO_PIN = 5
SERVO_FREQ_HZ = 50
SERVO_ACCEPT_DUTY_U16 = 6554
SERVO_HOLD_MS = 1000
POLL_MS = 250
WIFI_PM_MODE = network.WLAN.PM_NONE

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
    # No status NeoPixel is used on the XIAO actuator endpoint.
    return


def actuate_accept():
    servo = PWM(Pin(SERVO_PIN), freq=SERVO_FREQ_HZ)
    try:
        servo.duty_u16(SERVO_ACCEPT_DUTY_U16)
        time.sleep_ms(SERVO_HOLD_MS)
    finally:
        servo.deinit()


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
    ).format(method, path, PI_IP, len(body)).encode() + body

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
            time.ticks_diff(address_complete, address_start)
        ),
        "connect_ms": ms_from_us(
            time.ticks_diff(connect_complete, connect_start)
        ),
        "send_ms": ms_from_us(
            time.ticks_diff(send_complete, send_start)
        ),
        "first_byte_wait_ms": ms_from_us(
            time.ticks_diff(first_byte_complete, first_byte_start)
        ),
        "receive_rest_ms": ms_from_us(
            time.ticks_diff(receive_complete, receive_rest_start)
        ),
        "response_parse_ms": ms_from_us(
            time.ticks_diff(parse_complete, parse_start)
        ),
        "http_total_ms": ms_from_us(
            time.ticks_diff(parse_complete, total_start)
        ),
    }

    if return_timing:
        return parsed, timing

    return parsed


def post_nuvl(device_id, mode, run_id):
    nonce = "{}-{}-{}".format(device_id, run_id, time.ticks_ms())

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


def main():
    gc.collect()

    device_id = read_device_id()
    np = None
    led(np, "idle")

    wlan = connect_wifi(np)
    endpoint_ip = wlan.ifconfig()[0]

    print(
        "MULTI_ENDPOINT_POLL_READY device_id={} ip={} poll_ms={} wifi_pm=PM_NONE stage_timing=enabled".format(
            device_id,
            endpoint_ip,
            POLL_MS,
        )
    )

    last_run_id = None

    while True:
        try:
            trigger = http_json(
                "GET",
                COORD_PORT,
                "/trigger?device_id={}".format(device_id),
                None,
                timeout=3,
            )
        except Exception:
            time.sleep_ms(POLL_MS)
            continue

        if trigger.get("armed") is not True:
            time.sleep_ms(POLL_MS)
            continue

        run_id = str(trigger.get("run_id", ""))

        if not run_id or run_id == last_run_id:
            time.sleep_ms(POLL_MS)
            continue

        last_run_id = run_id
        mode = str(trigger.get("mode", "accept"))
        wait_ms = int(trigger.get("wait_ms", 0))
        if wait_ms > 0:
            time.sleep_ms(wait_ms)

        gc.collect()
        baseline_free = gc.mem_free()

        led(np, "created")
        time.sleep_ms(100)
        led(np, "waiting")

        actuator_attempted = False
        actuator_command_completed = False
        actuator_error = None

        started = time.ticks_ms()

        try:
            nonce, response, stage_timing = post_nuvl(
                device_id,
                mode,
                run_id,
            )
            elapsed_ms = time.ticks_diff(time.ticks_ms(), started)

            decision = response.get("decision")
            reason = response.get("reason")
            if decision == "accepted":
                led(np, "accept")
                actuator_attempted = True
                try:
                    actuate_accept()
                    actuator_command_completed = True
                except Exception as exc:
                    actuator_error = repr(exc)
            elif reason == "stale_replay_malformed":
                led(np, "stale")
            elif decision == "denied":
                led(np, "deny")
            else:
                led(np, "fail")

            result = {
                "run_id": run_id,
                "device_id": device_id,
                "ip": endpoint_ip,
                "decision": decision,
                "reason": reason,
                "elapsed_ms": elapsed_ms,
                "nonce": nonce,
                "actuator_attempted": actuator_attempted,
                "actuator_command_completed": actuator_command_completed,
                "actuator_error": actuator_error,
            }
            result.update(stage_timing)
        except Exception as exc:
            elapsed_ms = time.ticks_diff(time.ticks_ms(), started)
            led(np, "fail")

            result = {
                "run_id": run_id,
                "device_id": device_id,
                "ip": endpoint_ip,
                "decision": "unavailable",
                "reason": repr(exc),
                "provider_verified": False,
                "elapsed_ms": elapsed_ms,
                "nonce": None,
                "actuator_attempted": False,
                "actuator_command_completed": False,
                "actuator_error": None,
            }

        gc.collect()
        result["free_delta"] = gc.mem_free() - baseline_free

        try:
            http_json(
                "POST",
                COORD_PORT,
                "/result",
                result,
                timeout=4,
            )
        except Exception as exc:
            print(
                "RESULT_REPORT_FAILED run_id={} device_id={} error={}".format(
                    run_id,
                    device_id,
                    repr(exc),
                )
            )

        print(
            "MULTI_ENDPOINT_RESULT run_id={} device_id={} decision={} "
            "reason={} elapsed_ms={} free_delta={}".format(
                run_id,
                device_id,
                result.get("decision"),
                result.get("reason"),
                result.get("elapsed_ms"),
                result.get("free_delta"),
            )
        )

        print(
            "ACTUATOR_RESULT run_id={} device_id={} attempted={} completed={} error={}".format(
                run_id,
                device_id,
                result.get("actuator_attempted"),
                result.get("actuator_command_completed"),
                result.get("actuator_error"),
            )
        )

        time.sleep(2)
        led(np, "idle")


main()

