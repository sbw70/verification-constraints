"""Configuration-only launcher for unchanged MP003 role sources."""
import argparse,base64,importlib.util,json,signal,sys,threading
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('role',choices=['provider_a','provider_b','relay','association']); ap.add_argument('--root',required=True); a=ap.parse_args()
    root=Path(a.root).resolve(); cfg=json.loads((root/'configs/AE001_RUN_MANIFEST.json').read_text(encoding='utf-8-sig')); role=a.role
    paths={'provider_a':'provider_a/provider_a.py','provider_b':'provider_b/provider_b.py','relay':'intermediary/nuvl_multi_relay.py','association':'association/association_recorder.py'}
    source=root/'source/MP003'/paths[role]
    spec=importlib.util.spec_from_file_location('ae001_'+role,source); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.HOST='0.0.0.0'
    if role.startswith('provider_'):
        state=root/'runtime'/role
        m.PORT=cfg['ports']['provider']; m.ASSOCIATION_URL=cfg['association_url']
        m.SPENT_STATE_PATH=state/(role+'_spent_state.json'); m.EXECUTION_LOG_PATH=state/(role+'_execution.jsonl')
    elif role=='relay':
        m.PORT=cfg['ports']['relay']
        m.PROVIDERS=tuple({'url':'http://'+cfg['hosts'][r]+':'+str(cfg['ports']['provider'])+'/ingest','authorization_header':'X-Provider-'+r[-1].upper()+'-Authorization'} for r in ('provider_a','provider_b'))
        lock=threading.Lock(); trace=root/'runtime/relay_delivery.jsonl'
        # Observe outbound construction; do not change arguments or decide outcomes.
        def audit(event,args):
            if event=='urllib.Request':
                url,data,headers,method=args
                record={'url':url,'method':method,'body_b64':base64.b64encode(data or b'').decode()}
                with lock:
                    with trace.open('ab') as f: f.write(json.dumps(record,sort_keys=True,separators=(',',':')).encode()+b'\n')
        sys.addaudithook(audit)
    else:
        m.PORT=cfg['ports']['association']
        sys.argv=[str(source),'--session-id',root.name,'--registry',str(root/'source/MP003/association/provider_registry.json'),'--manifest',str(root/'configs/AE001_RUN_MANIFEST.json'),'--contract',str(root/'configs/AE001_CONTRACT.md'),'--log',str(root/'runtime/association.jsonl')]
    def interrupt(signum,frame): raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,interrupt)
    try: m.main()
    except KeyboardInterrupt: print('AE001_ROLE_STOPPED '+role,flush=True)
if __name__=='__main__': main()
