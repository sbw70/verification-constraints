#!/usr/bin/env python3
"""Pre-race witness wiring check for ESP-LOCAL-007. Spends NO authority.

Wraps the witness's own SELFTEST inside a START/STOP run so the witness
records, in its run_end event, how many servo-like bursts it saw while it
drove its GPIO6 self-test line.

Interpretation:
  servo_like_bursts == 0  -> GPIO6 self-test loopback is REMOVED. Scored
                             config (GPIO4 watching servo-02 GPIO5 only).
                             Good to proceed.
  servo_like_bursts >= 1  -> GPIO6 is still looped to GPIO4. That jumper is
                             also clamping GPIO4 during a real run and would
                             blind the witness. STOP and pull the loopback.

The number itself prints on the witness's own serial monitor in the
run_end line. This script prints the UDP replies (start/selftest/stop) so
you can confirm each step landed.
"""
import json
import socket
import sys
import time
from datetime import datetime, timezone

WITNESS_HOST = "192.168.0.216"
WITNESS_PORT = 19072
MAGIC = "W007"
RUN_ID = "LOOPCHK"


def utc():
    return datetime.now(timezone.utc).isoformat()


def call(sock, command, retries=3):
    payload = f"{MAGIC} {command}".encode()
    last = None
    for _ in range(retries):
        try:
            sock.sendto(payload, (WITNESS_HOST, WITNESS_PORT))
            data, _addr = sock.recvfrom(2048)
            return json.loads(data.decode())
        except socket.timeout as e:
            last = e
    return {"type": "no_reply", "error": str(last), "command": command}


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)

    print("STATUS  :", call(s, "STATUS"))

    start = call(s, f"START {RUN_ID} {utc()}")
    print("START   :", start)
    if start.get("ok") is not True:
        print(f"\nWitness would not start run ({start.get('detail')}). "
              f"Nothing driven, no check performed. Retry in a few seconds.")
        sys.exit(1)

    print("SELFTEST:", call(s, "SELFTEST"))

    # selftest drives 50 pulses at ~20ms period (~1s); give it margin.
    time.sleep(3)

    stop = call(s, f"STOP {utc()}")
    print("STOP    :", stop)
    print("\nNow read the run_end line on the WITNESS serial monitor.")
    print("servo_like_bursts = 0  -> loopback gone, wiring good, proceed.")
    print("servo_like_bursts >= 1 -> loopback still on GPIO4, STOP and pull it.")


if __name__ == "__main__":
    main()
