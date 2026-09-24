#!/usr/bin/env python3
"""Poll the ESP_LOCAL_007 witness's STATUS a few times, a second apart,
to see whether pulse_seq/queue_drops are advancing (real electrical
activity on GPIO4) versus static (one-off settling that's already over).

Touches nothing on the endpoint. Sends no authority. Safe to run any
number of times.
"""
import json
import socket
import time

WITNESS_HOST = "192.168.0.216"
WITNESS_PORT = 19072

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(2)

for i in range(5):
    s.sendto(b"W007 STATUS", (WITNESS_HOST, WITNESS_PORT))
    try:
        data, _ = s.recvfrom(2048)
        reply = json.loads(data.decode())
        print(f"[{i}] pulse_seq={reply.get('pulse_seq')} "
              f"queue_depth={reply.get('queue_depth')} "
              f"queue_drops={reply.get('queue_drops')} "
              f"connected={reply.get('connected')}")
    except socket.timeout:
        print(f"[{i}] no reply (timeout)")
    time.sleep(1)
