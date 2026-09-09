import json
import network
import socket
import time
from machine import Pin, PWM

SSID = "Xer0trust 2.4"
PASSWORD = open("wifi_password.txt").read().strip()

DEVICE_ID = "esp32-xiao-servo-01"
CONTEXT = "esp_local_demo"
SERVO_PIN = 5
SERVO_FREQ_HZ = 50
SERVO_DUTY_U16 = 6554
SERVO_HOLD_MS = 1000

ALLOWED_ACTIONS = {
    "move_servo": {
        "device_id": DEVICE_ID,
        "context": CONTEXT,
    }
}

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        for _ in range(30):
            if wlan.isconnected():
                break
            time.sleep_ms(500)

    if not wlan.isconnected():
        raise OSError("wifi_not_connected")

    return wlan

def actuate():
    servo = PWM(Pin(SERVO_PIN), freq=SERVO_FREQ_HZ)
    try:
        servo.duty_u16(SERVO_DUTY_U16)
        time.sleep_ms(SERVO_HOLD_MS)
    finally:
        servo.deinit()

def recognize_authority(req):
    allowed_keys = {"device_id", "context", "action"}

    for key in req:
        if key not in allowed_keys:
            return False, "unexpected_field"

    action = req.get("action")
    rule = ALLOWED_ACTIONS.get(action)

    if rule is None:
        return False, "action_not_authorized"

    if req.get("device_id") != rule["device_id"]:
        return False, "wrong_device"

    if req.get("context") != rule["context"]:
        return False, "wrong_context"

    return True, "authority_admissible"

def recv_http_request(conn):
    data = b""

    while b"\r\n\r\n" not in data:
        chunk = conn.recv(512)
        if not chunk:
            raise ValueError("incomplete_http_headers")
        data += chunk

    marker = data.find(b"\r\n\r\n")
    headers = data[:marker].decode()
    body = data[marker + 4:]

    content_length = 0

    for line in headers.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break

    while len(body) < content_length:
        chunk = conn.recv(512)
        if not chunk:
            raise ValueError("incomplete_http_body")
        body += chunk

    return json.loads(body[:content_length].decode())

def send_json(conn, status, obj):
    body = json.dumps(obj).encode()

    headers = (
        "HTTP/1.1 {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(status, len(body)).encode()

    conn.send(headers + body)

def serve():
    wlan = connect_wifi()
    ip = wlan.ifconfig()[0]

    addr = socket.getaddrinfo("0.0.0.0", 8088)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print(
        "ESP_LOCAL_001_READY device_id={} ip={} port=8088 context={}".format(
            DEVICE_ID,
            ip,
            CONTEXT,
        )
    )

    while True:
        conn, remote = s.accept()

        try:
            req = recv_http_request(conn)

            admissible, reason = recognize_authority(req)

            if not admissible:
                print(
                    "ESP_LOCAL_001_RESULT decision=denied reason={} request={}".format(
                        reason,
                        req,
                    )
                )

                send_json(
                    conn,
                    "403 Forbidden",
                    {
                        "decision": "denied",
                        "reason": reason,
                    },
                )
                continue

            actuate()

            print(
                "ESP_LOCAL_001_RESULT decision=accepted reason={} request={}".format(
                    reason,
                    req,
                )
            )

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
            print("ESP_LOCAL_001_ERROR", repr(exc))

            try:
                send_json(
                    conn,
                    "500 Internal Server Error",
                    {
                        "decision": "unavailable",
                        "reason": repr(exc),
                    },
                )
            except Exception:
                pass

        finally:
            conn.close()

serve()


