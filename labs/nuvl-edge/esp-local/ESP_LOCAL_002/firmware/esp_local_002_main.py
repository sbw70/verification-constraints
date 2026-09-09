import json
import socket
import time
import network
import hashlib
import ubinascii
from machine import Pin, PWM

SSID = "Xer0trust 2.4"
PASSWORD_FILE = "wifi_password.txt"

DEVICE_ID = "esp32-xiao-servo-01"
CONTEXT = "esp_local_002"
ACTION = "move_servo"

# Provider-generated SHA-256 commitment.
# The capability itself is NOT stored on the endpoint.
CAPABILITY_COMMITMENT = (
    "700775b2bd9fd36b8f0c5f6e5072297a"
    "6e6df30bbfb24b49fbf9e88960ad18ae"
)

HTTP_PORT = 8088

SERVO_PIN = 5
SERVO_HZ = 50
SERVO_DUTY = 6554
SERVO_HOLD_MS = 1000

ALLOWED_KEYS = {
    "device_id",
    "context",
    "action",
    "capability",
}

capability_spent = False

servo = PWM(Pin(SERVO_PIN))
servo.freq(SERVO_HZ)
servo.duty_u16(0)


def load_wifi_password():
    with open(PASSWORD_FILE, "r") as f:
        return f.read().strip()


def connect_wifi():
    password = load_wifi_password()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(SSID, password)

        deadline = time.ticks_add(time.ticks_ms(), 20000)

        while not wlan.isconnected():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                raise RuntimeError("wifi_connect_timeout")

            time.sleep_ms(100)

    return wlan


def sha256_hex(value):
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return ubinascii.hexlify(digest).decode()


def recognize_authority(req):
    global capability_spent

    for key in req:
        if key not in ALLOWED_KEYS:
            return False, "unexpected_field"

    if req.get("device_id") != DEVICE_ID:
        return False, "wrong_device"

    if req.get("context") != CONTEXT:
        return False, "wrong_context"

    if req.get("action") != ACTION:
        return False, "action_not_authorized"

    capability = req.get("capability")

    if not isinstance(capability, str):
        return False, "capability_missing"

    if sha256_hex(capability) != CAPABILITY_COMMITMENT:
        return False, "capability_invalid"

    if capability_spent:
        return False, "capability_spent"

    # Consume before physical execution.
    capability_spent = True

    return True, "authority_admissible"


def actuate_servo():
    servo.duty_u16(SERVO_DUTY)
    time.sleep_ms(SERVO_HOLD_MS)
    servo.duty_u16(0)


def send_json(conn, status, payload):
    body = json.dumps(payload)

    response = (
        "HTTP/1.1 {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
        "{}"
    ).format(
        status,
        len(body),
        body,
    )

    conn.send(response.encode("utf-8"))


def read_http_request(conn):
    data = b""

    while b"\r\n\r\n" not in data:
        chunk = conn.recv(512)

        if not chunk:
            raise ValueError("incomplete_headers")

        data += chunk

        if len(data) > 8192:
            raise ValueError("headers_too_large")

    header_bytes, body = data.split(b"\r\n\r\n", 1)
    header_text = header_bytes.decode("utf-8")

    content_length = 0

    for line in header_text.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break

    if content_length <= 0:
        raise ValueError("missing_content_length")

    if content_length > 4096:
        raise ValueError("body_too_large")

    while len(body) < content_length:
        chunk = conn.recv(
            min(512, content_length - len(body))
        )

        if not chunk:
            raise ValueError("incomplete_body")

        body += chunk

    return json.loads(
        body[:content_length].decode("utf-8")
    )


def handle_connection(conn):
    try:
        req = read_http_request(conn)

        accepted, reason = recognize_authority(req)

        if not accepted:
            send_json(
                conn,
                "403 Forbidden",
                {
                    "decision": "denied",
                    "reason": reason,
                },
            )
            return

        actuate_servo()

        send_json(
            conn,
            "200 OK",
            {
                "decision": "accepted",
                "reason": reason,
                "device_id": DEVICE_ID,
            },
        )

    except Exception as exc:
        send_json(
            conn,
            "500 Internal Server Error",
            {
                "decision": "unavailable",
                "reason": repr(exc),
            },
        )


wlan = connect_wifi()

print("ESP_LOCAL_002_READY")
print("device_id={}".format(DEVICE_ID))
print("ip={}".format(wlan.ifconfig()[0]))
print("capability_state=UNSPENT")

addr = socket.getaddrinfo(
    "0.0.0.0",
    HTTP_PORT,
)[0][-1]

server = socket.socket()
server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1,
)
server.bind(addr)
server.listen(2)

while True:
    conn = None

    try:
        conn, remote = server.accept()
        handle_connection(conn)

    except Exception as exc:
        print(
            "ESP_LOCAL_002_SERVER_ERROR {}".format(
                repr(exc)
            )
        )

    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
