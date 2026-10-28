"""MP005 evidence helpers. No provider imports or automatic live control."""
import base64, hashlib, ipaddress, json, os, platform, secrets, socket, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

STATES = {'PASS', 'FAIL', 'HARNESS_ERROR', 'PRECONDITION_NOT_MET', 'NOT_RUN'}
class HarnessError(RuntimeError): pass
class PreconditionError(RuntimeError): pass
def digest(b): return hashlib.sha256(b).hexdigest()
def canonical(v): return json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f: f.write(canonical(v)+b'\n')
def raw_write(p,b):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f: f.write(b)
def utc(): return datetime.now(timezone.utc).isoformat()
def require_linux():
    if sys.platform != 'linux': raise PreconditionError('Linux required; no provider started; persistence is not emulated')
def loopback(url):
    from urllib.parse import urlsplit
    u=urlsplit(url)
    if u.scheme!='http' or not u.hostname or not ipaddress.ip_address(u.hostname).is_loopback or u.username or u.password:
        raise PreconditionError('Simulation permits numeric loopback HTTP addresses only')
    return u
def install_loopback_guard():
    def audit(event,args):
        if event=='socket.connect':
            address=args[1]
            if isinstance(address,tuple):
                try: allowed=ipaddress.ip_address(address[0]).is_loopback
                except ValueError: allowed=False
                if not allowed: raise PreconditionError('Non-loopback simulation connection blocked')
    sys.addaudithook(audit)
def verify_sources(root,role=None):
    root=Path(root).resolve(); manifest=read(root/'configs/MP005_SOURCE_MANIFEST.json'); checked={}
    for e in manifest['frozen_implementation']:
        if role is not None and e['role']!=role:continue
        p=(root/e['path']).resolve()
        if not p.is_relative_to(root): raise PreconditionError('Source path escaped root')
        actual=digest(p.read_bytes())
        if actual!=e['sha256']: raise PreconditionError('Frozen implementation mismatch: '+e['path'])
        checked[e['path']]=actual
    return checked
def validate_snapshot(folder):
    folder=Path(folder);s=read(folder/'snapshot.json');state=(folder/'spent_state.json').read_bytes();execution=(folder/'execution.jsonl').read_bytes()
    parsed=json.loads(state);rows=[json.loads(l) for l in execution.splitlines()];aid=s['authorization_id']
    values={'spent_sha256':digest(state),'spent_length':len(state),'spent_count':len(parsed['spent']),'authorization_present':aid in parsed['spent'],'execution_sha256':digest(execution),'execution_length':len(execution),'execution_line_count':len(rows),'matching_execution_count':sum(r.get('authorization_id')==aid for r in rows)}
    if any(s[k]!=v for k,v in values.items()):raise HarnessError('Snapshot metadata/raw-byte mismatch: '+str(folder))
    return s
def validate_boundary_records(root,records,identity):
    from cryptography.hazmat.primitives import serialization
    for row in records:
        package=json.loads(base64.b64decode(row['raw_body_b64'],validate=True));e=package['event']
        if package.get('alg')!='Ed25519' or row['event']!=e or any(e.get(k)!=identity[k] for k in ('provider_id','authorization_id','operation_id','binding')):raise HarnessError('Saved boundary identity mismatch')
        role='provider_'+e['provider_id'][-1].lower();key=serialization.load_pem_public_key((Path(root)/'association/trust'/(role+'_public.pem')).read_bytes())
        rawkey=key.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        if e.get('key_id')!='sha256:'+digest(rawkey) or e.get('authorization_nonce')!=identity['authorization_nonce']:raise HarnessError('Saved boundary key/nonce mismatch')
        signature=package['signature'];key.verify(base64.urlsafe_b64decode(signature+'='*((-len(signature))%4)),b'NUVL-MP-BOUNDARY-v1|'+canonical(e))
    return [r['event'] for r in records]
def verify_harness(root):
    root=Path(root).resolve(); manifest=read(root/'configs/MP005_HARNESS_MANIFEST.json')
    for e in manifest['mp005_harness_test_code']:
        p=(root/e['path']).resolve()
        if not p.is_relative_to(root) or digest(p.read_bytes())!=e['sha256']:raise PreconditionError('MP005 harness identity mismatch: '+e['path'])
def inventory(root,filename='SHA256SUMS.txt'):
    root=Path(root); target=root/filename
    lines=[]
    for p in sorted(root.rglob('*')):
        if p.is_file() and p!=target: lines.append(digest(p.read_bytes())+'  '+p.relative_to(root).as_posix())
    raw_write(target,('\n'.join(lines)+'\n').encode('ascii'))
def state_snapshot(state_path,execution_path,authorization_id,out):
    state_path=Path(state_path).resolve(); execution_path=Path(execution_path).resolve(); out=Path(out); out.mkdir(parents=True,exist_ok=False)
    if not state_path.is_file(): raise PreconditionError('Spent state missing')
    state=state_path.read_bytes()
    try: parsed=json.loads(state)
    except (ValueError,UnicodeError) as ex: raise PreconditionError('Spent state invalid') from ex
    if not isinstance(parsed,dict) or parsed.get('version')!=1 or not isinstance(parsed.get('spent'),dict): raise PreconditionError('Spent state structure invalid')
    present=execution_path.is_file(); execution=execution_path.read_bytes() if present else b''
    try: rows=[json.loads(line) for line in execution.splitlines()]
    except (ValueError,UnicodeError) as ex: raise HarnessError('Execution log cannot be parsed') from ex
    raw_write(out/'spent_state.json',state); raw_write(out/'execution.jsonl',execution)
    result={'captured_utc':utc(),'state_path':str(state_path),'execution_path':str(execution_path),'spent_sha256':digest(state),'spent_length':len(state),'spent_count':len(parsed['spent']),'authorization_present':authorization_id in parsed['spent'],'authorization_id':authorization_id,'execution_log_exists':present,'execution_sha256':digest(execution),'execution_length':len(execution),'execution_line_count':len(rows),'matching_execution_count':sum(r.get('authorization_id')==authorization_id for r in rows),'local_execution_seq_values':[r.get('local_execution_seq') for r in rows]}
    from ledger_evidence import capture
    result.update(capture(state_path,authorization_id,out))
    write(out/'snapshot.json',result); return result
def filesystem_info(directory):
    info={'directory':str(Path(directory).resolve()),'mountinfo':[]}
    p=Path('/proc/self/mountinfo')
    if p.exists():
        resolved=str(Path(directory).resolve())
        matches=[]
        for line in p.read_text().splitlines():
            fields=line.split(); mount=fields[4].replace('\\040',' ')
            if resolved==mount or resolved.startswith(mount.rstrip('/')+'/'): matches.append((len(mount),line))
        if matches: info['mountinfo']=[max(matches)[1]]
    return info
def process_identity(pid,runtime_path,state_path,launcher_path=None,expected_provider=None):
    require_linux(); pid=int(pid); proc=Path('/proc')/str(pid)
    try:
        stat=(proc/'stat').read_text(); tail=stat.rsplit(')',1)[1].split(); ticks=int(tail[19]); state=tail[0]
        if state=='Z': raise PreconditionError('Provider process is a zombie')
        command=(proc/'cmdline').read_bytes().split(b'\0'); argv=[v.decode('utf-8') for v in command if v]
        cwd=os.readlink(proc/'cwd'); exe=os.readlink(proc/'exe')
        boot=(Path('/proc/sys/kernel/random/boot_id')).read_text().strip()
        btime=next(int(l.split()[1]) for l in Path('/proc/stat').read_text().splitlines() if l.startswith('btime '))
        epoch=btime+ticks/os.sysconf('SC_CLK_TCK')
    except (OSError,ValueError,StopIteration) as ex: raise PreconditionError('Cannot establish process identity') from ex
    runtime_path=Path(runtime_path).resolve(); direct=str(runtime_path) in argv
    wrapper=launcher_path and str(Path(launcher_path).resolve()) in argv
    if wrapper and expected_provider:
        wrapper=('--provider' in argv and argv[argv.index('--provider')+1]==expected_provider)
        wrapper=wrapper and '--state-dir' in argv and str(Path(argv[argv.index('--state-dir')+1]).resolve()/Path(state_path).name)==str(Path(state_path).resolve())
    if not (direct or wrapper): raise PreconditionError('Process command line does not identify intended runtime/launcher')
    version=subprocess.run([exe,'--version'],capture_output=True,text=True,timeout=5)
    return {'captured_utc':utc(),'hostname':socket.gethostname(),'os':platform.platform(),'snapshot_tool_python':sys.version,'python_executable_version':(version.stdout+version.stderr).strip(),'pid':pid,'process_state':state,'boot_id':boot,'start_ticks':ticks,'start_time_epoch':epoch,'start_time_utc':datetime.fromtimestamp(epoch,timezone.utc).isoformat(),'command_line':argv,'cwd':cwd,'executable':exe,'runtime_path':str(runtime_path),'runtime_sha256':digest(runtime_path.read_bytes()),'state_path':str(Path(state_path).resolve()),'filesystem':filesystem_info(Path(state_path).parent)}
def restart_assertions(before,after,expected_runtime_hash):
    return {'same_host':before['hostname']==after['hostname'],'same_boot':before['boot_id']==after['boot_id'],'new_process_instance':(before['pid'],before['start_ticks'])!=(after['pid'],after['start_ticks']),'later_start_time':after['start_ticks']>before['start_ticks'],'same_runtime_path':before['runtime_path']==after['runtime_path'],'runtime_hash_matches':before['runtime_sha256']==after['runtime_sha256']==expected_runtime_hash,'same_state_path':before['state_path']==after['state_path'],'same_command_line':before['command_line']==after['command_line'],'same_cwd':before['cwd']==after['cwd']}
def replay_assertions(before,after,events):
    keys=('spent_sha256','spent_length','spent_count','execution_log_exists','execution_sha256','execution_length','execution_line_count','matching_execution_count')
    assertions={'unchanged_'+k:before[k]==after[k] for k in keys}
    assertions.update({'authorization_present_before':before['authorization_present'],'authorization_present_after':after['authorization_present'],'one_deny_auth_spent':len(events)==1 and events[0].get('stage')=='DENY' and events[0].get('reason_code')=='auth_spent','no_start':all(e.get('stage')!='START' for e in events),'no_complete':all(e.get('stage')!='COMPLETE' for e in events)})
    return assertions
def prepare_authority(root,provider,folder,case_label,session_id):
    root=Path(root); folder=Path(folder); folder.mkdir(parents=True,exist_ok=False)
    # Deterministic operation bytes/context; only issuer-generated authorization nonce is fresh.
    request=canonical({'test':'MP005','session_id':session_id,'case':case_label,'action':'software_execution'})
    context='CTX_MP005_'+case_label
    raw_write(folder/'request.json',request)
    mint=root/provider/('mint_authorization_'+provider[-1]+'.py')
    result=subprocess.run([sys.executable,'-B',str(mint),'--request-file',str((folder/'request.json').resolve()),'--context',context,'--output',str((folder/'authorization.json').resolve())],capture_output=True,text=True,timeout=15)
    raw_write(folder/'mint_stdout.txt',result.stdout.encode());raw_write(folder/'mint_stderr.txt',result.stderr.encode())
    if result.returncode: raise HarnessError('Authorization mint failed')
    package=read(folder/'authorization.json'); auth=package['authorization']; header=(folder/'authorization.json.b64').read_text(encoding='ascii')
    core={k:auth[k] for k in ('version','provider_id','request_repr','verification_context','nonce')}
    binding=digest(('NUVL_BIND_V1|'+digest(request)+'|'+context).encode()); op=digest(('NUVL-MP-OP-v1|'+binding).encode())
    if auth['request_repr']!=digest(request) or auth['verification_context']!=context or auth['authorization_id']!=digest(b'NUVL-MP-AUTH-ID-v1|'+canonical(core)): raise HarnessError('Mint output is not bound to preserved request')
    identity={'provider_id':'PROVIDER_'+provider[-1].upper(),'context':context,'request_sha256':digest(request),'package_sha256':digest((folder/'authorization.json').read_bytes()),'header_sha256':digest(header.encode('ascii')),'authorization_id':auth['authorization_id'],'authorization_nonce':auth['nonce'],'binding':binding,'operation_id':op}
    write(folder/'identity.json',identity); return identity
def preserved_request(folder):
    folder=Path(folder); ident=read(folder/'identity.json'); request=(folder/'request.json').read_bytes(); package=(folder/'authorization.json').read_bytes(); header=(folder/'authorization.json.b64').read_text(encoding='ascii')
    if (digest(request),digest(package),digest(header.encode('ascii')))!=(ident['request_sha256'],ident['package_sha256'],ident['header_sha256']): raise HarnessError('Preserved request/authority changed')
    if base64.urlsafe_b64decode(header+'='*((-len(header))%4))!=package: raise HarnessError('Header/package mismatch')
    return ident,request,header
def send_preserved(folder,url,out,simulation=False):
    if simulation: loopback(url)
    ident,request,header=preserved_request(folder)
    import urllib.request
    headers={'Content-Type':'application/octet-stream','X-Verification-Context':ident['context'],'X-Provider-'+ident['provider_id'][-1]+'-Authorization':header}
    meta={'local_send_utc':utc(),'url':url,'identity':ident,'headers':headers,'request_b64':base64.b64encode(request).decode()}
    write(Path(out)/'send.json',meta)
    try:
        with urllib.request.urlopen(urllib.request.Request(url,request,headers,method='POST'),timeout=5) as r:
            write(Path(out)/'relay_response.json',{'status':r.status,'body_b64':base64.b64encode(r.read()).decode()})
    except OSError as ex: raise HarnessError('Relay transport failed') from ex
    return ident
def log_cursor(path):
    p=Path(path)
    if not p.exists(): raise PreconditionError('Recorder log is not available')
    data=p.read_bytes()
    if data and not data.endswith(b'\n'): raise HarnessError('Recorder log has a partial trailing record; retry before send')
    return {'byte_offset':len(data),'prefix_sha256':digest(data)}
def correlate(root,path,cursor,identity):
    data=Path(path).read_bytes(); prefix=data[:cursor['byte_offset']]
    if digest(prefix)!=cursor['prefix_sha256']: raise PreconditionError('Recorder log truncated/replaced since send cursor')
    tail=data[cursor['byte_offset']:]; lines=tail.splitlines(keepends=True); matched=[]
    from cryptography.hazmat.primitives import serialization
    for line in lines:
        if not line.endswith(b'\n'): continue
        row=json.loads(line)
        if row.get('record_type')!='SUBMISSION': continue
        raw=base64.b64decode(row['raw_body_b64'],validate=True); package=json.loads(raw); e=package['event']
        if not all(e.get(k)==identity[k] for k in ('provider_id','authorization_id','operation_id')): continue
        role='provider_'+e['provider_id'][-1].lower()
        key=serialization.load_pem_public_key((Path(root)/'association/trust'/(role+'_public.pem')).read_bytes())
        rawkey=key.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        if e.get('key_id')!='sha256:'+digest(rawkey) or e.get('binding')!=identity['binding'] or e.get('authorization_nonce')!=identity['authorization_nonce']: raise HarnessError('Boundary identity mismatch')
        signature=package['signature']; sig=base64.urlsafe_b64decode(signature+'='*((-len(signature))%4))
        try:key.verify(sig,b'NUVL-MP-BOUNDARY-v1|'+canonical(e))
        except Exception as ex:raise HarnessError('Boundary signature invalid') from ex
        matched.append({'event':e,'raw_body_b64':row['raw_body_b64'],'recorder_sig_valid':row.get('sig_valid'),'record_seq':row.get('record_seq')})
    return matched
def wait_events(root,path,cursor,identity,expected,timeout=10):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        records=correlate(root,path,cursor,identity); stages=[r['event']['stage'] for r in records]
        if stages==expected: return records
        if 'COMPLETE' in stages or 'DENY' in stages: return records
        time.sleep(.05)
    raise PreconditionError('Explicit correlated provider completion timed out; do not restart')
def score_restart_case(pre_restart,post_restart,pre_consume,consumed,before_replay,after_replay,replay_events,before_fresh,after_fresh,fresh_events,expected_hash,consume_events,consumed_id,fresh_id):
    restart=restart_assertions(pre_restart,post_restart,expected_hash)
    consumed_ok=consumed['authorization_present'] and consumed['matching_execution_count']==pre_consume['matching_execution_count']+1 and consumed['execution_line_count']==pre_consume['execution_line_count']+1 and consumed['spent_count']==pre_consume['spent_count']+1 and [e['stage'] for e in consume_events]==['START','COMPLETE']
    if not consumed_ok or not all(restart.values()):return {'status':'PRECONDITION_NOT_MET','consume_proven':consumed_ok,'restart':restart}
    replay=replay_assertions(before_replay,after_replay,replay_events)
    restart_state={'same_durable_state_across_restart':consumed['spent_sha256']==before_replay['spent_sha256'],'same_execution_log_across_restart':consumed['execution_sha256']==before_replay['execution_sha256'],'same_spent_path':consumed['state_path']==before_replay['state_path']}
    fresh={'new_authorization':consumed_id!=fresh_id,'authorization_present':after_fresh['authorization_present'],'one_new_execution':after_fresh['execution_line_count']==before_fresh['execution_line_count']+1 and after_fresh['matching_execution_count']==before_fresh['matching_execution_count']+1,'one_new_spent':after_fresh['spent_count']==before_fresh['spent_count']+1,'start_complete':[e['stage'] for e in fresh_events]==['START','COMPLETE']}
    from ledger_evidence import advance_checks
    initial_ledger=advance_checks(pre_consume,consumed,consume_events)
    fresh.update(advance_checks(before_fresh,after_fresh,fresh_events))
    restart_state['same_ledger_across_restart']=consumed['ledger_sha256']==before_replay['ledger_sha256']
    restart_state['snapshot_matches_ledger']=before_replay['snapshot_matches_ledger']
    consumed_ok=consumed_ok and all(initial_ledger.values())
    status='PASS' if consumed_ok and all(replay.values()) and all(restart_state.values()) and all(fresh.values()) else 'FAIL'
    return {'status':status,'consume_proven':consumed_ok,'consume_ledger':initial_ledger,'restart':restart,'preserved_state':restart_state,'replay':replay,'fresh':fresh,'sequence_telemetry_scored':False}
