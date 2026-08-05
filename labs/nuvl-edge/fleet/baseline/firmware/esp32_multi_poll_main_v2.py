import gc
import json
import network
import socket
import time
from machine import Pin
from neopixel import NeoPixel

SSID = "YOUR SSIDf"
PASSWORD = "YOUR PASSWORD"

PI_IP = "YOUR PI IP"
NUVL_PORT = 8089
COORD_PORT = 19052
CONTEXT = "field_led_demo"

LED_PIN = 48
POLL_MS = 250

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


def http_json(method, port, path, payload=None, timeout=5):
    body = b"" if payload is None else json.dumps(payload).encode()

    request = (
        "{} {} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(method, path, PI_IP, len(body)).encode() + body

    addr = socket.getaddrinfo(PI_IP, port)[0][-1]
    sock = socket.socket()
    sock.settimeout(timeout)

    try:
        sock.connect(addr)
        send_all(sock, request)

        chunks = []
        while True:
            chunk = sock.recv(512)
            if not chunk:
                break
            chunks.append(chunk)

        raw = b"".join(chunks)
    finally:
        sock.close()

    marker = raw.find(b"\r\n\r\n")
    if marker < 0:
        raise ValueError("invalid_http_response")

    return json.loads(raw[marker + 4:].decode())


def post_nuvl(device_id, mode, run_id):
    nonce = "{}-{}-{}".format(device_id, run_id, time.ticks_ms())

    response = http_json(
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
    )
    return nonce, response


def main():
    gc.collect()

    device_id = read_device_id()
    np = NeoPixel(Pin(LED_PIN, Pin.OUT), 1)
    led(np, "idle")

    wlan = connect_wifi(np)
    endpoint_ip = wlan.ifconfig()[0]

    print(
        "MULTI_ENDPOINT_POLL_READY device_id={} ip={} poll_ms={}".format(
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

        started = time.ticks_ms()

        try:
            nonce, response = post_nuvl(device_id, mode, run_id)
            elapsed_ms = time.ticks_diff(time.ticks_ms(), started)

            decision = response.get("decision")
            reason = response.get("reason")
            provider_verified = response.get("provider_verified")

            if decision == "accepted":
                led(np, "accept")
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
                "provider_verified": provider_verified,
                "elapsed_ms": elapsed_ms,
                "nonce": nonce,
            }
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

        time.sleep(2)
        led(np, "idle")


main()
