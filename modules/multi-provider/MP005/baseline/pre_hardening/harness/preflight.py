"""Future host-local inspection. No SSH, network requests or service control."""
import argparse,json,platform,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--role',choices=['provider_a','provider_b','intermediary','association'],required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--pid',type=int);ap.add_argument('--state-dir',type=Path);a=ap.parse_args()
    root=a.root.resolve();manifest=read(root/'configs/MP005_SOURCE_MANIFEST.json');entries=[e for e in manifest['frozen_implementation'] if e['role']==a.role];checks=[]
    for e in entries:
        p=(root/e['path']).resolve();actual=digest(p.read_bytes()) if p.is_file() else None
        checks.append({'path':str(p),'expected':e['sha256'],'actual':actual,'matches':actual==e['sha256']})
    result={'classification':'HOST_LOCAL_PREFLIGHT_CHECK_ONLY','hostname':socket.gethostname(),'os':platform.platform(),'python':sys.version,'role':a.role,'files':checks,'status':'PASS' if checks and all(c['matches'] for c in checks) else 'PRECONDITION_NOT_MET'}
    if a.role.startswith('provider'):
        require_linux()
        if not a.pid or not a.state_dir:raise PreconditionError('Provider preflight requires actual PID and state directory')
        state=(a.state_dir/(a.role+'_spent_state.json')).resolve()
        result['process']=process_identity(a.pid,root/a.role/(a.role+'.py'),state,root/'harness/launch_provider.py',a.role)
        result['resolved_state_path']=str(state);result['filesystem']=filesystem_info(a.state_dir)
    write(a.output,result);print(json.dumps(result));return 0 if result['status']=='PASS' else 2
if __name__=='__main__':
    try:sys.exit(main())
    except (PreconditionError,OSError) as ex:print('PRECONDITION_NOT_MET: '+str(ex),file=sys.stderr);sys.exit(2)
