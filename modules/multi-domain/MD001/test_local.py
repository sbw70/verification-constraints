"""Local integration validation of physical adapters using loopback-only configs."""
import base64
from datetime import datetime, timezone
import hashlib
import http.client
import json
from pathlib import Path
import queue
import socket
import subprocess
import sys
import threading
import uuid

B = Path(__file__).resolve().parent


def main():
    out = B / "validation" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ_") + uuid.uuid4().hex[:8])
    out.mkdir(parents=True)
    processes, logs, checks = [], [], []
    def check(name, value):
        checks.append(dict(name=name, passed=bool(value)))
        if not value: raise AssertionError(name)
    def run(*args):
        result=subprocess.run([sys.executable,"-B",str(B/'md001.py'),*map(str,args)],capture_output=True,timeout=25)
        tag=uuid.uuid4().hex
        (out/(tag+'-command-stdout.txt')).write_bytes(result.stdout)
        (out/(tag+'-command-stderr.txt')).write_bytes(result.stderr)
        result.check_returncode()
        return result
    def port():
        with socket.socket() as s:
            s.bind(('127.0.0.1',0)); return s.getsockname()[1]
    def launch(name, role, listen, target=None, mode='pass', peer='127.0.0.1'):
        cfg=dict(role=role,listen=dict(host='127.0.0.1',port=listen),target=None if target is None else dict(host='127.0.0.1',port=target),mode=mode,allowed_peer=peer)
        cp=out/(name+'.json');cp.write_text(json.dumps(cfg))
        err=(out/(name+'-stderr.txt')).open('xb');logs.append(err)
        args=[sys.executable,'-B',str(B/'md001.py'),'serve','--config',str(cp),'--out',str(out/name)]
        if role=='verifier':args+=['--trust',str(out/'keys/trust.json')]
        proc=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=err);processes.append(proc)
        q=queue.Queue();threading.Thread(target=lambda:q.put(proc.stdout.readline()),daemon=True).start()
        line=q.get(timeout=20);(out/(name+'-stdout.txt')).write_bytes(line)
        if not line:raise RuntimeError(name+' startup failed')
        return proc,json.loads(line)
    def stop(p):
        if p.poll() is None:p.terminate();p.wait(timeout=10)
    def read(p):return json.loads(p.read_bytes())
    try:
        run('keygen','--out',out/'keys')
        vp,ip,rp=port(),port(),port()
        v,old=launch('verifier1','verifier',vp)
        ingress,_=launch('ingress','ingress',ip,vp)
        relay,_=launch('relay','relay',rp,ip,peer=None)
        run('produce-send','--key',out/'keys/TEST_ONLY_private.pem','--host','127.0.0.1','--port',rp,'--out',out/'B01')
        raw=(out/'B01/artifact.json').read_bytes()
        check('B01_producer_operates_signs_and_sends',read(out/'B01/result.json')['response']['accepted'] and (out/'B01/operation.json').exists())
        check('B01_ingress_and_verifier_identical_bytes',all(p.read_bytes()==raw for folder in ['ingress','verifier1'] for p in (out/folder).glob('*-ingress.bin')))
        records=[json.loads(x) for x in (out/'relay/relay.jsonl').read_text().splitlines()]
        check('frozen_relay_records_same_body_hash',any(x['transport_result']=='response_forwarded' and x['ingress_body_sha256']==x['egress_body_sha256']==hashlib.sha256(raw).hexdigest() for x in records))
        stop(ingress)
        tamper,_=launch('tamper','ingress',ip,vp,'tamper')
        run('resubmit','--artifact',out/'B01/artifact.json','--host','127.0.0.1','--port',rp,'--out',out/'N01')
        n=read(out/'N01/result.json')['response']
        check('N01_rejected_invalid_signature',n['reason']=='invalid_signature' and n['signature_checks']==1)
        mutated=next((out/'tamper').glob('*-egress.bin')).read_bytes()
        check('N01_original_signature_retained',read(out/'B01/artifact.json')['signature']==json.loads(mutated)['signature'] and mutated!=raw)
        stop(tamper);stop(v)
        v2,new=launch('verifier2','verifier',vp)
        ingress2,_=launch('ingress2','ingress',ip,vp)
        # Original producer is the completed produce-send subprocess; it is absent.
        # Resubmitter needs only exact artifact bytes, no private key or producer API.
        run('resubmit','--artifact',out/'B01/artifact.json','--host','127.0.0.1','--port',rp,'--out',out/'B02')
        r=read(out/'B02/result.json')['response']
        check('B02_fresh_process_fresh_crypto_no_producer',old['pid']!=new['pid'] and old['process_instance']!=new['process_instance'] and r['accepted'] and r['signature_checks']==1)
        run('resubmit','--artifact',out/'B01/artifact.json','--host','127.0.0.1','--port',rp,'--out',out/'repeat')
        check('same_artifact_accepted_again',read(out/'repeat/result.json')['response']['accepted'])
        c=http.client.HTTPConnection('127.0.0.1',rp,timeout=10)
        c.request('POST','/verify',raw,{'X-MH-Destination':'PROVIDER_A','Content-Type':'application/json'})
        reply=c.getresponse();check('unused_A_route_denied_locally',reply.status==403);reply.read();c.close()
        c=http.client.HTTPConnection('127.0.0.1',ip,timeout=10)
        c.request('POST','/wrong',raw,{'X-MH-Destination':'PROVIDER_B','Content-Type':'application/json'})
        reply=c.getresponse();check('wrong_path_rejected',reply.status==400);reply.read();c.close()
        deny_port=port();denier,_=launch('wrong_peer','ingress',deny_port,vp,peer='127.0.0.2')
        c=http.client.HTTPConnection('127.0.0.1',deny_port,timeout=10);c.request('POST','/verify',raw)
        reply=c.getresponse();check('ingress_enforces_pi_peer',reply.status==403);reply.read();c.close()
        original=read(B/'ORIGINAL_PROJECT_LOCK.json')
        actual={p.relative_to(B.parent/'MULTI_DOMAIN_001').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (B.parent/'MULTI_DOMAIN_001').rglob('*') if p.is_file()}
        check('entire_original_project_unchanged',actual==original)
        lock=read(B/'RUNTIME_LOCK.json')
        check('runtime_matches_frozen_copies',all(hashlib.sha256((B/'runtime'/n).read_bytes()).hexdigest()==h for n,h in lock.items()))
    except Exception:
        import traceback
        (out/'ERROR.txt').write_text(traceback.format_exc())
        checks.append(dict(name='harness_completed',passed=False))
    finally:
        for p in reversed(processes):stop(p)
        for f in logs:f.close()
    result=dict(mode='LOCAL_LOOPBACK_ADAPTER_VALIDATION_ONLY',utc=datetime.now(timezone.utc).isoformat(),checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),physical_evidence=False)
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(out).as_posix()+'\n' for p in sorted(out.rglob('*')) if p.is_file()))
    print(json.dumps(dict(directory=str(out),**result),indent=2))
    return int(result['failed']!=0)


if __name__=='__main__':raise SystemExit(main())
