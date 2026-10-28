"""Future live case phases. Explicit gates; NEVER kills or restarts a live provider."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *

def require_live_permission(root,authorization_path,phase,session_id=None):
    if phase not in ('rehearsal','scored') or not authorization_path:raise PreconditionError('Later explicit phase authorization required')
    auth=read(authorization_path);m=read(Path(root)/'configs/MP005_RUN_MANIFEST.json')
    required='APPROVED_FOR_LIVE_REHEARSAL' if phase=='rehearsal' else 'APPROVED_FOR_SCORED_AFTER_REHEARSAL_REVIEW'
    if auth.get('authorized') is not True or auth.get('phase')!=phase or m.get('status')!=required:raise PreconditionError('Draft build is not authorized for live execution')
    if not auth.get('session_id') or session_id is not None and auth['session_id']!=session_id:raise PreconditionError('Authorization/session mismatch')
    if phase=='scored' and not auth.get('rehearsal_review_reference'):raise PreconditionError('Scored authorization must reference rehearsal review')
    lock=Path(root)/'configs/MP005_LIVE_LOCK_SHA256SUMS.txt'
    if not lock.is_file():raise PreconditionError('Reviewed live contract/manifest lock absent')
    for line in lock.read_text().splitlines():
        expected,rel=line.split(None,1);p=(Path(root)/rel).resolve()
        if not p.is_relative_to(Path(root).resolve()) or digest(p.read_bytes())!=expected:raise PreconditionError('Live lock mismatch')
    verify_harness(root)
    return m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['initialize-state','prepare','consume','checkpoint','capture','capture-state','prepare-fresh','replay','fresh','score']);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--phase',choices=['rehearsal','scored'],required=True);ap.add_argument('--operator-authorization',type=Path,required=True);ap.add_argument('--session-id',required=True);ap.add_argument('--case',choices=['R01','R02'],required=True);ap.add_argument('--state-dir',type=Path);ap.add_argument('--pid',type=int);ap.add_argument('--label',choices=['pre_restart','post_restart','pre_consume','consumed','before_replay','after_replay','before_fresh','after_fresh']);ap.add_argument('--association-log',type=Path);a=ap.parse_args()
    root=a.root.resolve();m=require_live_permission(root,a.operator_authorization,a.phase,a.session_id)
    provider='provider_a' if a.case=='R01' else 'provider_b';phase_dir='preflight' if a.phase=='rehearsal' else 'scored';case=root/'evidence'/phase_dir/a.session_id/a.case
    verify_sources(root,provider)
    deployment=m['deployments'][provider]
    if a.state_dir and str(a.state_dir.resolve())!=deployment['state_dir']:raise PreconditionError('State path does not match reviewed deployment')
    state_dir=Path(deployment['state_dir']);state=state_dir/(provider+'_spent_state.json');execution=state_dir/(provider+'_execution.jsonl')
    runtime=root/provider/(provider+'.py');launcher=root/'harness/launch_provider.py'
    expected_hash=next(e['sha256'] for e in read(root/'configs/MP005_SOURCE_MANIFEST.json')['frozen_implementation'] if e['path']==provider+'/'+provider+'.py')
    if a.action=='initialize-state':
        require_linux();state_dir.mkdir(parents=True,exist_ok=False);raw_write(state,canonical({'version':1,'spent':{}}));print('Initialized NEW state directory only.');return 0
    if a.action=='prepare':
        case.mkdir(parents=True,exist_ok=False);prepare_authority(root,provider,case/'original',a.case,a.session_id)
        write(case/'case_identity.json',{'provider':provider,'case':a.case,'session_id':a.session_id,'runtime_path':deployment['runtime_path'],'state_path':deployment['spent_state_path'],'execution_path':deployment['execution_log_path'],'runtime_sha256':expected_hash,'phase':a.phase});return 0
    if not case.is_dir():raise HarnessError('Prepare this case first')
    ident=read(case/'original/identity.json');aid=ident['authorization_id']
    if a.action=='capture':
        if not a.pid or a.label not in ('pre_restart','post_restart'):raise HarnessError('Capture requires actual PID and pre_restart/post_restart label')
        require_linux();process=process_identity(a.pid,runtime,state,launcher,provider);write(case/(a.label+'_process.json'),process);state_snapshot(state,execution,aid,case/(a.label+'_state'));return 0
    if a.action=='capture-state':
        if a.label not in ('pre_consume','consumed','before_replay','after_replay','before_fresh','after_fresh'):raise HarnessError('Choose an explicit state snapshot label')
        if not a.pid:raise HarnessError('Actual provider PID required to bind snapshot to intended process')
        require_linux();process=process_identity(a.pid,runtime,state,launcher,provider)
        current=read(case/('fresh' if 'fresh' in a.label else 'original')/'identity.json')
        snapshot=state_snapshot(state,execution,current['authorization_id'],case/a.label)
        write(case/a.label/'process.json',process);print(json.dumps(snapshot));return 0
    if a.action=='checkpoint':
        consumed=read(case/'consumed/snapshot.json');events=read(case/'consume/boundary_records.json')
        if not consumed['authorization_present'] or consumed['matching_execution_count']<1 or [v['event']['stage'] for v in events]!=['START','COMPLETE']:raise PreconditionError('Consume not proven: do not terminate')
        old=read(case/'pre_restart_process.json')
        if old['runtime_sha256']!=expected_hash:raise PreconditionError('Runtime differs')
        instruction={'status':'OPERATOR_CHECKPOINT','case':a.case,'idle_requirement':'Prior correlated COMPLETE and local consume/execution captured; operator must independently confirm no request in flight','operator_linux_kill_command':'kill -KILL '+str(old['pid']),'automatic_kill_executed':False,'operator_restart':'Repeat the exact previously captured launch command with the same runtime and state directory','next':'capture post_restart, then replay; relay/recorder/non-target must remain running'}
        write(case/'operator_checkpoint.json',instruction);print(json.dumps(instruction,indent=2));return 0
    if a.action=='prepare-fresh':
        replay=read(case/'replay/boundary_records.json');before=read(case/'before_replay/snapshot.json');after=read(case/'after_replay/snapshot.json')
        if not all(replay_assertions(before,after,[r['event'] for r in replay]).values()):raise PreconditionError('Replay assertions incomplete/failed')
        prepare_authority(root,provider,case/'fresh',a.case+'_FRESH',a.session_id);return 0
    if a.action in ('consume','replay','fresh'):
        if not a.association_log:raise HarnessError('Provide locally accessible continuous association log')
        if a.action=='replay':
            if not (case/'operator_checkpoint.json').is_file():raise PreconditionError('Operator checkpoint not recorded')
            old=read(case/'pre_restart_process.json');new=read(case/'post_restart_process.json')
            assertions=restart_assertions(old,new,expected_hash)
            if not all(assertions.values()):raise PreconditionError('Restart not objectively proven')
        if a.action=='fresh':
            replay=read(case/'replay/boundary_records.json');before=read(case/'before_replay/snapshot.json');after=read(case/'after_replay/snapshot.json')
            if not all(replay_assertions(before,after,[r['event'] for r in replay]).values()):raise PreconditionError('Replay assertions incomplete/failed')
        folder=case/('fresh' if a.action=='fresh' else 'original');current=read(folder/'identity.json')
        before_name={'consume':'pre_consume','replay':'before_replay','fresh':'before_fresh'}[a.action]
        after_name={'consume':'consumed','replay':'after_replay','fresh':'after_fresh'}[a.action]
        before=read(case/before_name/'snapshot.json')
        if before['authorization_id']!=current['authorization_id'] or before['state_path']!=deployment['spent_state_path']:raise PreconditionError('Transferred pre-send snapshot is for a different authority/state path')
        out=case/(a.action if a.action!='fresh' else 'fresh_send');out.mkdir();cursor=log_cursor(a.association_log);write(out/'association_cursor.json',cursor)
        send_preserved(folder,m['relay_url'],out)
        records=wait_events(root,a.association_log,cursor,current,['DENY'] if a.action=='replay' else ['START','COMPLETE'],m.get('timeout_seconds',15))
        write(out/'boundary_records.json',records);print('Signed completion captured. Operator must now capture '+after_name+' on the target provider and copy the snapshot back; HTTP 204 alone was not used.');return 0
    if a.action=='score':
        get=lambda name:validate_snapshot(case/name)
        def events(name):
            identity=read(case/('fresh' if name=='fresh_send' else 'original')/'identity.json')
            records=read(case/name/'boundary_records.json')
            if name=='replay':
                if not a.association_log:raise PreconditionError('Final score requires the continuous recorder log for a late-event recheck')
                records=correlate(root,a.association_log,read(case/name/'association_cursor.json'),identity)
            return validate_boundary_records(root,records,identity)
        try:
            result=score_restart_case(read(case/'pre_restart_process.json'),read(case/'post_restart_process.json'),get('pre_consume'),get('consumed'),get('before_replay'),get('after_replay'),events('replay'),get('before_fresh'),get('after_fresh'),events('fresh_send'),expected_hash,events('consume'),aid,read(case/'fresh/identity.json')['authorization_id'])
        except PreconditionError as ex:result={'status':'PRECONDITION_NOT_MET','error':str(ex)}
        except (OSError,ValueError,HarnessError) as ex:result={'status':'HARNESS_ERROR','error':str(ex)}
        write(case/'case_results.json',result);inventory(case);print(json.dumps(result));return 0 if result['status']=='PASS' else 2

if __name__=='__main__':
    try:sys.exit(main())
    except (PreconditionError,HarnessError,OSError,ValueError) as ex:
        status='PRECONDITION_NOT_MET' if isinstance(ex,PreconditionError) else 'HARNESS_ERROR'
        print(json.dumps({'status':status,'error':str(ex)}));sys.exit(2)
