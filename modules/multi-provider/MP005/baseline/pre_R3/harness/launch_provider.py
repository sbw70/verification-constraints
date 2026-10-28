"""Load candidate provider source; configure paths/network only. Linux only."""
import argparse, importlib.util, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import require_linux, install_loopback_guard, loopback, verify_sources, verify_harness, PreconditionError

def main():
    require_linux()
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['simulation','live'],required=True);ap.add_argument('--root',required=True);ap.add_argument('--provider',choices=['provider_a','provider_b'],required=True);ap.add_argument('--state-dir',required=True);ap.add_argument('--host',required=True);ap.add_argument('--port',type=int,required=True);ap.add_argument('--association-url',required=True);ap.add_argument('--operator-authorization');ap.add_argument('--phase',choices=['rehearsal','scored']);a=ap.parse_args()
    root=Path(a.root).resolve();state=Path(a.state_dir).resolve()
    if a.mode=='simulation':
        install_loopback_guard();loopback(a.association_url)
        if a.host!='127.0.0.1' or not state.is_relative_to(root/'evidence/simulated_smoke'):raise PreconditionError('Simulation state/network isolation invalid')
    else:
        from live_case import require_live_permission
        require_live_permission(root,a.operator_authorization,a.phase)
    verify_sources(root,a.provider);verify_harness(root)
    source=root/a.provider/(a.provider+'.py')
    spec=importlib.util.spec_from_file_location('mp005_frozen_'+a.provider,source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.HOST=a.host;m.PORT=a.port;m.ASSOCIATION_URL=a.association_url
    m.CONSUME_LEDGER_PATH=state/(a.provider+'_consume_ledger.jsonl')
    m.SPENT_STATE_PATH=state/(a.provider+'_spent_state.json');m.EXECUTION_LOG_PATH=state/(a.provider+'_execution.jsonl')
    # No persistence method, fsync call, decision, key, state content or signature logic is replaced.
    m.main()
if __name__=='__main__':
    try:main()
    except PreconditionError as ex: print('PRECONDITION_NOT_MET: '+str(ex),file=sys.stderr);sys.exit(2)
