"""Future live relay/association launcher. No automatic restarts."""
import argparse,importlib.util,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import verify_sources
from live_case import require_live_permission

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--role',choices=['intermediary','association'],required=True);ap.add_argument('--phase',choices=['rehearsal','scored'],required=True);ap.add_argument('--operator-authorization',required=True);ap.add_argument('--session-id',required=True);ap.add_argument('--log',type=Path);a=ap.parse_args()
    root=a.root.resolve();m=require_live_permission(root,a.operator_authorization,a.phase,a.session_id);verify_sources(root,a.role)
    source=root/a.role/('nuvl_multi_relay.py' if a.role=='intermediary' else 'association_recorder.py')
    spec=importlib.util.spec_from_file_location('mp005_'+a.role,source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    if a.role=='intermediary':
        module.HOST=m['relay_listen_host'];module.PORT=m['relay_port'];module.PROVIDERS=tuple({'url':m['deployments'][r]['ingest_url'],'authorization_header':'X-Provider-'+r[-1].upper()+'-Authorization'} for r in ('provider_a','provider_b'))
    else:
        if a.log is None:raise ValueError('Recorder log path required')
        module.HOST=m['association_listen_host'];module.PORT=m['association_port'];sys.argv=[str(source),'--session-id',a.session_id,'--registry',str(root/'association/provider_registry.json'),'--manifest',str(root/'configs/MP005_RUN_MANIFEST.json'),'--contract',str(root/'configs/MP005_CONTRACT.md'),'--log',str(a.log)]
    module.main()
if __name__=='__main__':main()
