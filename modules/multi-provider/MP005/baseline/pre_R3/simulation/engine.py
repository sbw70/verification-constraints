import argparse,base64,hashlib,json,os,platform,socket,subprocess,sys,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'harness'))
from common import *
from ledger_evidence import bootstrap, replay_checks, advance_checks

class Recorder:
    """Simulation-only raw package recorder, deliberately not a live association claim."""
    def __init__(self,path):
        self.path=path;self.lock=threading.Lock();raw_write(path,b'')
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                if self.path!='/boundary':self.send_error(404);return
                raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
                with owner.lock:
                    with owner.path.open('ab') as f:f.write(canonical({'record_type':'SUBMISSION','raw_body_b64':base64.b64encode(raw).decode(),'simulation_recorder':True})+b'\n');f.flush();os.fsync(f.fileno())
                self.send_response(204);self.end_headers()
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.url='http://127.0.0.1:'+str(self.server.server_port)+'/boundary'
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()

def free_port():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def wait_ready(p,port,provider=None):
    import urllib.request
    end=time.monotonic()+8
    while time.monotonic()<end:
        if p.poll() is not None:raise PreconditionError('Child exited before readiness; inspect preserved console')
        try:
            if provider:
                with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/health',timeout=.5) as response:health=json.loads(response.read())
                if health.get('provider_id')=='PROVIDER_'+provider[-1].upper():return
            else:
                with socket.create_connection(('127.0.0.1',port),timeout=.5):return
        except OSError:pass
        time.sleep(.05)
    raise PreconditionError('Loopback readiness timeout/port conflict')
def start(argv,console):
    with console.open('xb') as log:
        return subprocess.Popen([sys.executable,'-u','-B']+list(map(str,argv)),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
def kill_local(p):
    # Called only by this Linux-only disposable simulation; never imported by live tooling.
    if p is not None and p.poll() is None:p.kill();p.wait(timeout=5)

class Scenario:
    def __init__(self,root,directory,provider):
        self.root=root;self.directory=directory;self.provider=provider;self.state=directory/'state';self.state.mkdir();self.runtime=root/provider/(provider+'.py');self.state_path=self.state/(provider+'_spent_state.json');self.exec_path=self.state/(provider+'_execution.jsonl');self.p=None;self.relay=None;self.recorder=None;self.port=free_port();self.generation=0
    def init_valid(self):bootstrap(self.state,self.provider)
    def start_network(self):
        self.recorder=Recorder(self.directory/'association.jsonl');self.relay_port=free_port()
        self.relay=start([self.root/'simulation/launch_relay.py','--root',self.root,'--provider',self.provider,'--provider-url','http://127.0.0.1:'+str(self.port)+'/ingest','--port',self.relay_port],self.directory/'relay_console.txt')
        wait_ready(self.relay,self.relay_port)
    def spawn_provider(self,ready=True):
        self.generation+=1
        self.p=start([self.root/'harness/launch_provider.py','--mode','simulation','--root',self.root,'--provider',self.provider,'--state-dir',self.state,'--host','127.0.0.1','--port',self.port,'--association-url',self.recorder.url],self.directory/('provider_console_'+str(self.generation)+'.txt'))
        if ready:wait_ready(self.p,self.port,self.provider)
    def identity(self,name):
        value=process_identity(self.p.pid,self.runtime,self.state_path,self.root/'harness/launch_provider.py',self.provider);write(self.directory/(name+'.json'),value);return value
    def snap(self,name,auth):return state_snapshot(self.state_path,self.exec_path,auth,self.directory/name)
    def send(self,folder,label,expected):
        ident,request,header=preserved_request(folder);d=self.directory/label;d.mkdir();cursor=log_cursor(self.recorder.path);write(d/'association_cursor.json',cursor)
        send_preserved(folder,'http://127.0.0.1:'+str(self.relay_port)+'/nuvl',d,simulation=True)
        records=wait_events(self.root,self.recorder.path,cursor,ident,expected)
        write(d/'boundary_records.json',records);return [r['event'] for r in records]
    def close(self):
        kill_local(self.p);kill_local(self.relay)
        if self.recorder:self.recorder.close()

def check_r1(root):
    folder=root/'evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R1'
    record=read(root/'notes/R1_PRESERVATION.json')
    expected=record['files']
    actual={p.relative_to(folder).as_posix():digest(p.read_bytes()) for p in folder.rglob('*') if p.is_file() and p!=folder/'SHA256SUMS.txt'}
    if actual!=expected or digest((folder/'SHA256SUMS.txt').read_bytes())!=record['inventory_sha256']:raise PreconditionError('R1 evidence changed or missing')
    return {'status':'UNCHANGED','files_checked':len(actual),'inventory_sha256':record['inventory_sha256']}

def restart_case(s,session,case):
    s.init_valid();s0=s.state_path.read_bytes();raw_write(s.directory/'S0.json',s0)
    s.start_network();s.spawn_provider()
    old=prepare_authority(s.root,s.provider,s.directory/'original',case+'_'+s.provider,session);aid=old['authorization_id']
    pre=s.snap('pre_consume',aid);events=s.send(s.directory/'original','consume',['START','COMPLETE']);consumed=s.snap('consumed',aid)
    initial=advance_checks(pre,consumed,events)
    if not all(initial.values()):raise PreconditionError('Consume not proven; forced restart prohibited: '+str(initial))
    before=s.identity('process_before');kill_local(s.p)
    if case=='S03':
        if not s.state_path.resolve().is_relative_to((s.root/'evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R2').resolve()):raise HarnessError('Rollback outside R2')
        with s.state_path.open('wb') as f:f.write(s0);f.flush();os.fsync(f.fileno())
        raw_write(s.directory/'ledger_L1_before_restart.jsonl',(s.state/(s.provider+'_consume_ledger.jsonl')).read_bytes())
    s.spawn_provider();after=s.identity('process_after')
    restart=restart_assertions(before,after,digest(s.runtime.read_bytes()))
    if not all(restart.values()):raise PreconditionError('New process identity not proven')
    br=s.snap('before_replay',aid)
    recovery={'ledger_unchanged_across_restart':br['ledger_sha256']==consumed['ledger_sha256'],'snapshot_reconciled_to_L1':br['snapshot_matches_ledger'] and br['spent_sha256']==consumed['spent_sha256'],'execution_unchanged_across_restart':br['execution_sha256']==consumed['execution_sha256'],'authority_still_spent':br['authorization_present'] and br['ledger_authorization_present']}
    if case=='S03':
        console=(s.directory/'provider_console_2.txt').read_text()
        recovery['recovery_logged']='SNAPSHOT_RECOVERED_FROM_LEDGER' in console
    replay=s.send(s.directory/'original','replay',['DENY']);ar=s.snap('after_replay',aid)
    fresh=prepare_authority(s.root,s.provider,s.directory/'fresh',case+'_FRESH_'+s.provider,session)
    bf=s.snap('before_fresh',fresh['authorization_id']);fe=s.send(s.directory/'fresh','fresh_send',['START','COMPLETE']);af=s.snap('after_fresh',fresh['authorization_id'])
    final_old=s.snap('final_original',aid)
    late=correlate(s.root,s.recorder.path,read(s.directory/'replay/association_cursor.json'),old)
    write(s.directory/'replay/final_boundary_records.json',late)
    # Revalidate saved raw material; a relay 204 is never property evidence.
    for name in ('pre_consume','consumed','before_replay','after_replay','before_fresh','after_fresh','final_original'):validate_snapshot(s.directory/name)
    validate_boundary_records(s.root,read(s.directory/'consume/boundary_records.json'),old)
    validate_boundary_records(s.root,late,old)
    validate_boundary_records(s.root,read(s.directory/'fresh_send/boundary_records.json'),fresh)
    replay=replay_checks(br,ar,[row['event'] for row in late]);fresh_checks=advance_checks(bf,af,fe)
    fresh_checks['different_authorization']=aid!=fresh['authorization_id']
    replay['stable_until_fresh_send']=all(ar[k]==bf[k] for k in ('ledger_sha256','spent_sha256','execution_sha256'))
    replay['original_execution_count_unchanged_through_fresh']=final_old['matching_execution_count']==ar['matching_execution_count']
    replay['only_fresh_execution_added']=final_old['execution_line_count']==ar['execution_line_count']+1
    passed=all(initial.values()) and all(restart.values()) and all(recovery.values()) and all(replay.values()) and all(fresh_checks.values())
    return {'status':'PASS' if passed else 'FAIL','classification':'HARDENED_LOCAL_SIMULATION_ONLY_NOT_SCORED_MP005','consume':initial,'restart':restart,'recovery':recovery,'replay':replay,'fresh':fresh_checks,'rollback_reenabled_authority':ar['matching_execution_count']>br['matching_execution_count'],'signed_boundary_evidence':{'consume':events,'replay':[row['event'] for row in late],'fresh':fe},'full_history_rollback_resistance':'NOT_ESTABLISHED','sequence_telemetry_scored':False}

def invalid_start(s,malformed):
    ledger=s.state/(s.provider+'_consume_ledger.jsonl')
    raw_write(s.state_path,canonical({'version':1,'spent':{},'ledger_seq':0,'ledger_head':None}))
    if malformed:raw_write(ledger,b'{broken-json\n')
    original=ledger.read_bytes() if ledger.exists() else None
    snapshot=s.state_path.read_bytes()
    s.start_network();s.spawn_provider(ready=False)
    try:code=s.p.wait(timeout=6)
    except subprocess.TimeoutExpired:raise PreconditionError('Invalid ledger did not fail startup')
    text=(s.directory/'provider_console_1.txt').read_text(encoding='utf-8',errors='replace')
    reason='consume_ledger_invalid' if malformed else 'consume_ledger_missing'
    with socket.socket() as sock:usable=sock.connect_ex(('127.0.0.1',s.port))==0
    after=ledger.read_bytes() if ledger.exists() else None
    assertions={'startup_failed':code!=0,'expected_reason':reason in text,'no_usable_server':not usable,'no_ledger_initialization_or_repair':original==after,'snapshot_not_used_as_authority':snapshot==s.state_path.read_bytes(),'no_execution_log':not s.exec_path.exists()}
    return {'status':'PASS' if all(assertions.values()) else 'FAIL','assertions':assertions,'classification':'HARDENED_LOCAL_STARTUP_ONLY'}

def run():
    require_linux();install_loopback_guard()
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--session',choices=['MP005_SIMULATED_SMOKE_R2'],default='MP005_SIMULATED_SMOKE_R2');a=ap.parse_args()
    root=a.root.resolve();verify_sources(root);verify_harness(root);preserved=check_r1(root)
    output=root/'evidence/simulated_smoke'/a.session;output.mkdir(parents=True,exist_ok=False)
    write(output/'environment.json',{'classification':'DISPOSABLE_LOCAL_SIMULATION_ONLY','platform':platform.platform(),'python':sys.version,'filesystem':filesystem_info(output),'implementation_hashes':verify_sources(root),'R1_preservation':preserved,'live_host_contact_permitted':False})
    results=[];stop=False
    for provider in ('provider_a','provider_b'):
        for case in ('S00','S01','S02','S03'):
            d=output/provider/case;d.mkdir(parents=True);s=Scenario(root,d,provider)
            try:
                result=restart_case(s,a.session,case) if case in ('S00','S03') else invalid_start(s,case=='S02')
            except PreconditionError as ex:result={'status':'PRECONDITION_NOT_MET','error':str(ex)};stop=True
            except Exception as ex:result={'status':'HARNESS_ERROR','error':type(ex).__name__+': '+str(ex)};stop=True
            finally:s.close()
            result.update(provider=provider,case=case,live_rehearsal='NOT_RUN',scored_MP005='NOT_RUN');write(d/'case_results.json',result);inventory(d);results.append(result)
            if stop or result['status']=='FAIL':stop=True;break
        if stop:break
    for provider in ('provider_a','provider_b'):
        for case in ('S00','S01','S02','S03'):
            if not any(row['provider']==provider and row['case']==case for row in results):results.append({'provider':provider,'case':case,'status':'NOT_RUN'})
    verify_sources(root);verify_harness(root);preserved=check_r1(root)
    write(output/'case_results.json',{'classification':'SIMULATION_ONLY','results':results,'R1_preservation':preserved,'scored_MP005':'NOT_RUN','mandatory_next_step':'STOP_FOR_OPERATOR_REVIEW'});inventory(output)
    print(json.dumps({'output':str(output),'results':[{k:row[k] for k in ('provider','case','status')} for row in results],'scored_MP005':'NOT_RUN','next':'STOP_FOR_OPERATOR_REVIEW'}))
    return 2 if stop else 0
