import gc
import json
import network
import socket
import time
from machine import Pin
from neopixel import NeoPixel

SSID = "GL-MT300N-V2-94f"
PASSWORD = "goodlife"
PI_IP = "192.168.8.234"
PORT = 8089
CONTEXT = "field_led_demo"

LED_PIN = 48

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
    with open("main.py", "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("DEVICE_ID"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("DEVICE_ID not found in main.py")


def led(np, state):
    np[0] = COLORS[state]
    np.write()


def connect_wifi(np):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        return wlan

    wlan.connect(SSID, PASSWORD)

    for _ in range(20):
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


def post_request(device_id):
    nonce = "{}-{}".format(device_id, time.ticks_ms())

    body_obj = {
        "device_id": device_id,
        "context": CONTEXT,
        "requested_action": "accept",
        "nonce": nonce,
    }
    body = json.dumps(body_obj)

    request = (
        "POST /nuvl HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
        "{}"
    ).format(PI_IP, len(body), body).encode()

    addr = socket.getaddrinfo(PI_IP, PORT)[0][-1]
    sock = socket.socket()
    sock.settimeout(5)

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

    response = json.loads(raw[marker + 4:].decode())
    return nonce, response


def main():
    gc.collect()
    baseline_free = gc.mem_free()

    device_id = read_device_id()
    np = NeoPixel(Pin(LED_PIN, Pin.OUT), 1)

    led(np, "idle")
    wlan = connect_wifi(np)

    print(
        "READY device_id={} ip={} free_ram={}".format(
            device_id,
            wlan.ifconfig()[0],
            baseline_free,
        )
    )

    time.sleep_ms(750)

    led(np, "created")
    time.sleep_ms(150)
    led(np, "waiting")

    started = time.ticks_ms()

    try:
        nonce, response = post_request(device_id)
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

        print(
            "RESULT device_id={} decision={} reason={} "
            "provider_verified={} elapsed_ms={} nonce={}".format(
                device_id,
                decision,
                reason,
                provider_verified,
                elapsed_ms,
                nonce,
            )
        )
    except Exception as exc:
        elapsed_ms = time.ticks_diff(time.ticks_ms(), started)
        led(np, "fail")
        print(
            "RESULT device_id={} decision=unavailable reason={} "
            "provider_verified=False elapsed_ms={}".format(
                device_id,
                repr(exc),
                elapsed_ms,
            )
        )

    time.sleep(2)
    led(np, "idle")
    gc.collect()
    final_free = gc.mem_free()
    print(
        "DONE device_id={} final_free={} free_delta={}".format(
            device_id,
            final_free,
            final_free - baseline_free,
        )
    )


main()
