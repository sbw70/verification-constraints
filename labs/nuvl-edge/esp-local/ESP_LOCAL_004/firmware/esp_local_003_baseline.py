import hashlib
import json
import socket
import time
import network
import ubinascii
from machine import Pin, PWM

SSID = "Xer0trust 2.4"

with open("wifi_password.txt", "r") as f:
    PASSWORD = f.read().strip()

DEVICE_ID = "esp32-xiao-servo-01"
CONTEXT = "esp_local_003"
ACTION = "move_servo"

AUTHORITY_COMMITMENT = (
    "2452e70c9003739fd571a5e38752e54d"
    "526c1f7ee876ad3bed3041e09ca9c0cc"
)

PORT = 8088

SERVO_PIN = 5
SERVO_FREQ = 50
SERVO_DUTY = 6554
SERVO_HOLD_MS = 1000

ALLOWED_KEYS = {
    "device_id",
    "context",
    "action",
    "nonce",
    "max_uses",
}

authority_spent = False


def canonical_authority(obj):
    return (
        '{"action":' + json.dumps(obj["action"]) +
        ',"context":' + json.dumps(obj["context"]) +
        ',"device_id":' + json.dumps(obj["device_id"]) +
        ',"max_uses":' + str(obj["max_uses"]) +
        ',"nonce":' + json.dumps(obj["nonce"]) +
        '}'
    )


def authority_hash(obj):
    canonical = canonical_authority(obj)
    digest = hashlib.sha256(canonical.encode("utf-8")).digest()
    return ubinascii.hexlify(digest).decode("ascii")


def actuate_servo():
    pwm = PWM(Pin(SERVO_PIN))
    pwm.freq(SERVO_FREQ)
    pwm.duty_u16(SERVO_DUTY)

    time.sleep_ms(SERVO_HOLD_MS)

    pwm.deinit()


def decision(obj):
    global authority_spent

    if set(obj.keys()) != ALLOWED_KEYS:
        return False, "unexpected_or_missing_field"

    if obj["device_id"] != DEVICE_ID:
        return False, "wrong_device"

    if obj["context"] != CONTEXT:
        return False, "wrong_context"

    if obj["action"] != ACTION:
        return False, "action_not_authorized"

    if obj["max_uses"] != 1:
        return False, "use_constraint_invalid"

    if not isinstance(obj["nonce"], str):
        return False, "nonce_invalid"

    try:
        digest = authority_hash(obj)
    except Exception:
        return False, "authority_invalid"

    if digest != AUTHORITY_COMMITMENT:
        return False, "authority_commitment_mismatch"

    if authority_spent:
        return False, "authority_spent"

    authority_spent = True
    return True, "authority_admissible"


def send_response(client, status, body):
    payload = json.dumps(body)

    response = (
        "HTTP/1.1 {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
        "{}"
    ).format(
        status,
        len(payload),
        payload,
    )

    client.send(response.encode("utf-8"))


def read_request(client):
    data = b""

    while b"\r\n\r\n" not in data:
        chunk = client.recv(512)

        if not chunk:
            raise ValueError("incomplete_headers")

        data += chunk

        if len(data) > 8192:
            raise ValueError("request_too_large")

    headers, body = data.split(b"\r\n\r\n", 1)

    content_length = 0

    for line in headers.split(b"\r\n")[1:]:
        if b":" not in line:
            continue

        name, value = line.split(b":", 1)

        if name.strip().lower() == b"content-length":
            content_length = int(value.strip())

    while len(body) < content_length:
        chunk = client.recv(512)

        if not chunk:
            raise ValueError("incomplete_body")

        body += chunk

    body = body[:content_length]

    return json.loads(body.decode("utf-8"))


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)

        while not wlan.isconnected():
            time.sleep_ms(250)

    return wlan


wlan = connect_wifi()

print("ESP_LOCAL_003_READY")
print("device_id={}".format(DEVICE_ID))
print("ip={}".format(wlan.ifconfig()[0]))
print("authority_state=UNSPENT")

addr = socket.getaddrinfo("0.0.0.0", PORT)[0][-1]

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(2)

while True:
    client = None

    try:
        client, remote = server.accept()

        obj = read_request(client)

        accepted, reason = decision(obj)

        if accepted:
            actuate_servo()

            send_response(
                client,
                "200 OK",
                {
                    "decision": "accepted",
                    "reason": reason,
                    "device_id": DEVICE_ID,
                },
            )

        else:
            send_response(
                client,
                "403 Forbidden",
                {
                    "decision": "denied",
                    "reason": reason,
                },
            )

    except Exception as exc:
        try:
            if client:
                send_response(
                    client,
                    "500 Internal Server Error",
                    {
                        "decision": "unavailable",
                        "reason": str(exc),
                    },
                )
        except Exception:
            pass

    finally:
        try:
            if client:
                client.close()
        except Exception:
            pass
