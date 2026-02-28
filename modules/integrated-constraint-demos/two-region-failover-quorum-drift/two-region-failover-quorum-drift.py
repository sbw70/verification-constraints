#!/usr/bin/env python3

Copyright 2026 Seth Brian Wells



This file incorporates components derived from the NUVL core,

which is licensed under the Apache License, Version 2.0.

A copy of the Apache License may be obtained at:

http://www.apache.org/licenses/LICENSE-2.0



Except for the Apache-2.0 licensed NUVL core components,

all additional orchestration, failover, quorum, adversarial,

and integration logic contained in this file is proprietary.



Commercial deployment, redistribution, or integration of

the proprietary portions requires a separate written license agreement.

from http.server import ThreadingHTTPServer as HTTPServer, BaseHTTPRequestHandler
import hashlib, hmac, json, random, threading, time, urllib.request

============================================================

CONFIG

============================================================

TOTAL_REQUESTS = 750
FAILOVER_AT = 375
QUORUM_THRESHOLD = 2
RANDOM_SEED = 1337

EXPECTED_CONTEXT = "CTX_ALPHA"
DOMAINS = ["payments", "identity", "storage"]

NUVL_A_PORT = 8000
HUB_A_PORT = 8100

NUVL_B_PORT = 8001
HUB_B_PORT = 8101

AUDITOR_PORT = 8200

PROVIDER_PORTS = {
"PROVIDER_A": 9001,
"PROVIDER_B": 9002,
"PROVIDER_C": 9003,
}

============================================================

RANDOMIZED BYZANTINE (runtime)

============================================================

ACTIVE_BYZ_PROVIDER = None
ACTIVE_BYZ_AT = None

============================================================

PROVIDERS

============================================================

PROVIDER_KEYS = {
"PROVIDER_A": b"A_KEY",
"PROVIDER_B": b"B_KEY",
"PROVIDER_C": b"C_KEY",
}

PROVIDER_THRESHOLDS = {
"payments": 0.55,
"identity": 0.60,
"storage": 0.50,
}

PROVIDER_INIT_COUNTS = {k: 0 for k in PROVIDER_PORTS}
PROVIDER_LOCK = threading.Lock()
CURRENT_REQUEST_INDEX = 0

def provider_score(pid, rr, ctx, domain):
seed = PROVIDER_KEYS[pid]
material = f"{pid}|{domain}|{rr}|{ctx}".encode()
digest = hmac.new(seed, material, hashlib.sha256).digest()
n = int.from_bytes(digest[:8], "big")
base = (n % 10_000_000) / 10_000_000.0
if ctx == EXPECTED_CONTEXT:
base += 0.15
return min(base, 1.0)

def sign(pid, rr):
return hmac.new(PROVIDER_KEYS[pid], rr.encode(), hashlib.sha256).hexdigest()

class ProviderHandler(BaseHTTPRequestHandler):
provider_id = "X"
def log_message(self, *args): return

def do_POST(self):  
    global CURRENT_REQUEST_INDEX  

    msg = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))  
    rr = msg["request_repr"]  
    ctx = msg["verification_context"]  
    domain = msg["domain"]  

    s = provider_score(self.provider_id, rr, ctx, domain)  
    initiated = s >= PROVIDER_THRESHOLDS[domain]  

    if self.provider_id == ACTIVE_BYZ_PROVIDER and CURRENT_REQUEST_INDEX >= ACTIVE_BYZ_AT:  
        initiated = not initiated  

    if initiated:  
        with PROVIDER_LOCK:  
            PROVIDER_INIT_COUNTS[self.provider_id] += 1  

    fire(f"http://127.0.0.1:{AUDITOR_PORT}/audit", {  
        "provider": self.provider_id,  
        "request_repr": rr,  
        "initiated": initiated,  
        "signature": sign(self.provider_id, rr),  
    })  

    self.send_response(204)  
    self.end_headers()

def make_provider(pid, port):
handler = type(pid, (ProviderHandler,), {"provider_id": pid})
return HTTPServer(("0.0.0.0", port), handler)

============================================================

HUBS

============================================================

def fire(url, payload):
def ():
try:
req = urllib.request.Request(
url,
data=json.dumps(payload).encode(),
headers={"Connection":"close","Content-Type":"application/json"},
)
urllib.request.urlopen(req, timeout=2)
except:
pass
threading.Thread(target= , daemon=True).start()

class HubHandler(BaseHTTPRequestHandler):
def log_message(self, *args): return
def do_POST(self):
msg = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
for port in PROVIDER_PORTS.values():
fire(f"http://127.0.0.1:{port}", msg)
self.send_response(204)
self.end_headers()

============================================================

NUVL FRONTS

============================================================

class NUVLHandler(BaseHTTPRequestHandler):
hub_port = 0
def log_message(self, *args): return
def do_POST(self):
raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
rr = hashlib.sha256(raw).hexdigest()
ctx = self.headers.get("X-Verification-Context", "")
domain = self.headers.get("X-Domain", "payments")

fire(f"http://127.0.0.1:{self.hub_port}", {  
        "request_repr": rr,  
        "verification_context": ctx,  
        "domain": domain  
    })  

    self.send_response(204)  
    self.end_headers()

============================================================

AUDITOR

============================================================

AUDIT_LOG = {}
AUDIT_LOCK = threading.Lock()
QUORUM_SUCCESS = 0
QUORUM_FAIL = 0

class AuditorHandler(BaseHTTPRequestHandler):
def log_message(self, *args): return
def do_POST(self):
global QUORUM_SUCCESS, QUORUM_FAIL

msg = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))  
    rr = msg["request_repr"]  
    pid = msg["provider"]  
    initiated = msg["initiated"]  
    sig = msg["signature"]  

    if sig != sign(pid, rr):  
        self.send_response(204); self.end_headers(); return  

    with AUDIT_LOCK:  
        AUDIT_LOG.setdefault(rr, []).append(initiated)  
        if len(AUDIT_LOG[rr]) == 3:  
            if sum(AUDIT_LOG[rr]) >= QUORUM_THRESHOLD:  
                QUORUM_SUCCESS += 1  
            else:  
                QUORUM_FAIL += 1  

    self.send_response(204)  
    self.end_headers()

============================================================

REQUESTER

============================================================

def requester_send(port, payload, ctx, domain):
req = urllib.request.Request(
f"http://127.0.0.1:{port}",
data=payload,
headers={
"Connection":"close",
"Content-Type":"application/octet-stream",
"X-Verification-Context": ctx,
"X-Domain": domain
}
)
urllib.request.urlopen(req, timeout=2)

def run():
global CURRENT_REQUEST_INDEX
random.seed(RANDOM_SEED)

start = time.perf_counter()  

for i in range(TOTAL_REQUESTS):  
    CURRENT_REQUEST_INDEX = i  
    region_port = NUVL_A_PORT if i < FAILOVER_AT else NUVL_B_PORT  
    ctx = EXPECTED_CONTEXT if random.random() > 0.1 else "SPOOF"  
    domain = random.choice(DOMAINS)  
    payload = f'{{"i":{i}}}'.encode()  
    requester_send(region_port, payload, ctx, domain)  

elapsed = (time.perf_counter() - start) * 1000  
time.sleep(2)  
return elapsed

============================================================

MAIN

============================================================

def start(server): server.serve_forever()

def main():
global ACTIVE_BYZ_PROVIDER, ACTIVE_BYZ_AT

random.seed(RANDOM_SEED)  
ACTIVE_BYZ_PROVIDER = random.choice(list(PROVIDER_PORTS.keys()))  
ACTIVE_BYZ_AT = random.randint(int(TOTAL_REQUESTS*0.55), int(TOTAL_REQUESTS*0.9))  

for pid, port in PROVIDER_PORTS.items():  
    threading.Thread(target=start, args=(make_provider(pid, port),), daemon=True).start()  

threading.Thread(target=start, args=(HTTPServer(("0.0.0.0", HUB_A_PORT), HubHandler),), daemon=True).start()  
threading.Thread(target=start, args=(HTTPServer(("0.0.0.0", HUB_B_PORT), HubHandler),), daemon=True).start()  

handlerA = type("NUVL_A", (NUVLHandler,), {"hub_port": HUB_A_PORT})  
handlerB = type("NUVL_B", (NUVLHandler,), {"hub_port": HUB_B_PORT})  
threading.Thread(target=start, args=(HTTPServer(("0.0.0.0", NUVL_A_PORT), handlerA),), daemon=True).start()  
threading.Thread(target=start, args=(HTTPServer(("0.0.0.0", NUVL_B_PORT), handlerB),), daemon=True).start()  

threading.Thread(target=start, args=(HTTPServer(("0.0.0.0", AUDITOR_PORT), AuditorHandler),), daemon=True).start()  

time.sleep(1)  

elapsed = run()  

print("\n===== REGION FAILOVER + RANDOMIZED BYZANTINE QUORUM =====")  
print(f"Total requests: {TOTAL_REQUESTS}")  
print(f"Failover at: {FAILOVER_AT}")  
print(f"Byzantine provider: {ACTIVE_BYZ_PROVIDER}")  
print(f"Byzantine flip at: {ACTIVE_BYZ_AT}")  
print(f"Total time: {elapsed:.2f} ms")  
print(f"Avg per request: {elapsed/TOTAL_REQUESTS:.4f} ms\n")  

print("Provider Initiations:")  
for k,v in PROVIDER_INIT_COUNTS.items():  
    print(f"{k}: {v}")  

print("\nAuditor Results:")  
print(f"Quorum successes: {QUORUM_SUCCESS}")  
print(f"Quorum failures: {QUORUM_FAIL}")  
print("==============================================\n")  

while True:  
    time.sleep(1)

if name == "main":
main()
