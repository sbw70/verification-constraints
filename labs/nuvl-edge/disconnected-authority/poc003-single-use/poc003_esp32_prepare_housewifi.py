import gc
import json
import os
import socket
import time

PI_IP = "192.168.1.167"
PORT = 8089
OUTPUT_FILE = "poc003_artifacts.json"

DEVICE_ID = "esp32-field-01"
CONTEXT = "field_led_demo"
ACTION = "accept"

ARTIFACT_NAMES = [
    ("primary", "valid"),
    ("wrong_context", "valid"),
    ("wrong_action", "valid"),
    ("wrong_nonce", "valid"),
    ("wrong_device", "valid"),
    ("tampered", "valid"),
    ("unsigned", "valid"),
    ("stale", "stale"),
]


def http_json(method, path, payload=None, timeout=8):
    body = b"" if payload is None else json.dumps(payload).encode()

    request = (
        "{} {} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(method, path, PI_IP, len(body)).encode() + body

    s = socket.socket()
    s.settimeout(timeout)

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
        return json.loads(response_body.decode())
    finally:
        try:
            s.close()
        except Exception:
            pass


print("POC003_PREPARE_START")
gc.collect()
baseline_free = gc.mem_free()

artifacts = {}
passed = 0
failed = 0

for index, item in enumerate(ARTIFACT_NAMES, 1):
    name, mode = item
    issue_request = {
        "device_id": DEVICE_ID,
        "context": CONTEXT,
        "requested_action": ACTION,
        "nonce": "poc003-{}-{}-{}".format(name, index, time.ticks_ms()),
        "test_mode": mode,
    }

    try:
        response = http_json("POST", "/issue", issue_request)
        ok = (
            response.get("decision") == "issued"
            and response.get("provider_verified") is True
            and isinstance(response.get("package"), dict)
        )

        if ok:
            artifacts[name] = {
                "issue_request": issue_request,
                "package": response["package"],
            }
            passed += 1
        else:
            failed += 1

        print(
            "ISSUE {} name={} mode={} decision={} reason={} verified={} result={}".format(
                index,
                name,
                mode,
                response.get("decision"),
                response.get("reason"),
                response.get("provider_verified"),
                "PASS" if ok else "FAIL",
            )
        )
    except Exception as exc:
        failed += 1
        print(
            "ISSUE {} name={} error={} result=FAIL".format(
                index, name, repr(exc)
            )
        )

    gc.collect()
    time.sleep_ms(150)

if failed:
    print("POC003_PREPARE_ABORT")
    print("issued=", passed)
    print("failed=", failed)
    raise RuntimeError("Artifact preparation failed")

with open(OUTPUT_FILE, "w") as f:
    json.dump(artifacts, f)

gc.collect()
final_free = gc.mem_free()
file_size = os.stat(OUTPUT_FILE)[6]

print("POC003_PREPARE_SUMMARY")
print("artifacts_issued=", passed)
print("failed=", failed)
print("artifact_file=", OUTPUT_FILE)
print("artifact_file_bytes=", file_size)
print("baseline_free=", baseline_free)
print("final_free=", final_free)
print("free_delta=", final_free - baseline_free)
print("private_key_on_endpoint=", False)
print("STOP_PROVIDER_BEFORE_SPEND=True")
print("POC003_PREPARE_END")
