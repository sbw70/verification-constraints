import json
import socket
import time

PI_IP = "192.168.8.234"
PORT = 8089

payload = {
    "device_id": "esp32-field-01",
    "context": "field_led_demo",
    "requested_action": "accept",
    "nonce": "poc002a-{}".format(time.ticks_ms()),
    "test_mode": "valid",
}

body = json.dumps(payload).encode()
request = (
    "POST /nuvl HTTP/1.1\r\n"
    "Host: {}\r\n"
    "Content-Type: application/json\r\n"
    "Content-Length: {}\r\n"
    "Connection: close\r\n"
    "\r\n"
).format(PI_IP, len(body)).encode() + body

s = socket.socket()
s.settimeout(7)

try:
    s.connect((PI_IP, PORT))
    s.send(request)

    chunks = []
    while True:
        try:
            chunk = s.recv(512)
            if not chunk:
                break
            chunks.append(chunk)
        except OSError:
            if chunks:
                break
            raise

    raw = b"".join(chunks)
    response_body = raw.split(b"\r\n\r\n", 1)[1]
    response = json.loads(response_body.decode())

    print("POC002A_RESPONSE")
    print("decision=", response.get("decision"))
    print("reason=", response.get("reason"))
    print("provider_verified=", response.get("provider_verified"))
    print("boundary=", response.get("boundary"))
finally:
    try:
        s.close()
    except Exception:
        pass
