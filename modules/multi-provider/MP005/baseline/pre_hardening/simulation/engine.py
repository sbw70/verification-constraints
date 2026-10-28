import argparse,base64,hashlib,json,os,platform,socket,subprocess,sys,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'harness'))
from common import *

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
    def init_valid(self):raw_write(self.state_path,canonical({'version':1,'spent':{}}))
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

def normal(s,session):
    s.init_valid();s.start_network();s.spawn_provider()
    old=prepare_authority(s.root,s.provider,s.directory/'original','S00_'+s.provider,session)
    pre=s.snap('pre_consume',old['authorization_id']);events=s.send(s.directory/'original','consume',['START','COMPLETE']);consumed=s.snap('consumed',old['authorization_id'])
    if [e['stage'] for e in events]!=['START','COMPLETE'] or not consumed['authorization_present'] or consumed['matching_execution_count']!=1:raise PreconditionError('Consume not proven; forced restart prohibited')
    before=s.identity('process_before');kill_local(s.p);s.spawn_provider();after=s.identity('process_after')
    restart=restart_assertions(before,after,digest(s.runtime.read_bytes()))
    if not all(restart.values()):return {'status':'PRECONDITION_NOT_MET','restart':restart}
    before_replay=s.snap('before_replay',old['authorization_id']);replay=s.send(s.directory/'original','replay',['DENY']);after_replay=s.snap('after_replay',old['authorization_id'])
    fresh=prepare_authority(s.root,s.provider,s.directory/'fresh','S00_FRESH_'+s.provider,session)
    bf=s.snap('before_fresh',fresh['authorization_id']);fe=s.send(s.directory/'fresh','fresh_send',['START','COMPLETE']);af=s.snap('after_fresh',fresh['authorization_id'])
    late=correlate(s.root,s.recorder.path,read(s.directory/'replay/association_cursor.json'),old)
    write(s.directory/'replay/final_boundary_records.json',late);replay=[r['event'] for r in late]
    result=score_restart_case(before,after,pre,consumed,before_replay,after_replay,replay,bf,af,fe,digest(s.runtime.read_bytes()),events,old['authorization_id'],fresh['authorization_id'])
    result['telemetry']={'local_execution_seq_values':af['local_execution_seq_values'],'process_local_sequence_may_repeat':len(af['local_execution_seq_values'])!=len(set(af['local_execution_seq_values']))}
    result['classification']='SIMULATION_ONLY_NOT_MP005_PROOF';return result
def invalid_start(s,malformed):
    if malformed:raw_write(s.state_path,canonical({'version':1,'spent':[]}))
    original=s.state_path.read_bytes() if s.state_path.exists() else None
    s.start_network();s.spawn_provider(ready=False)
    try:code=s.p.wait(timeout=6)
    except subprocess.TimeoutExpired:raise PreconditionError('Invalid-state provider did not fail startup')
    text=(s.directory/'provider_console_1.txt').read_text(encoding='utf-8',errors='replace')
    reason='spent_state_invalid' if malformed else 'spent_state_missing'
    with socket.socket() as sock:usable=sock.connect_ex(('127.0.0.1',s.port))==0
    after=s.state_path.read_bytes() if s.state_path.exists() else None
    assertions={'startup_failed':code!=0,'expected_reason':reason in text,'no_usable_server':not usable,'no_silent_state_initialization':original==after}
    return {'status':'PASS' if all(assertions.values()) else 'FAIL','assertions':assertions,'classification':'LOCAL_STARTUP_CHARACTERIZATION_NOT_PRIMARY_MP005'}
def rollback(s,session):
    s.init_valid();s0=s.state_path.read_bytes();raw_write(s.directory/'S0.json',s0);s.start_network();s.spawn_provider()
    ident=prepare_authority(s.root,s.provider,s.directory/'original','S03_'+s.provider,session);aid=ident['authorization_id']
    first=s.send(s.directory/'original','consume',['START','COMPLETE']);s1=s.snap('S1',aid)
    if [e['stage'] for e in first]!=['START','COMPLETE'] or not s1['authorization_present']:raise PreconditionError('S03 consume precondition not met')
    before=s.identity('process_before');kill_local(s.p)
    # Deliberate substitution only in this verified disposable simulation directory.
    if not s.state_path.resolve().is_relative_to((s.root/'evidence/simulated_smoke').resolve()):raise HarnessError('Rollback target outside disposable area')
    with s.state_path.open('wb') as f:f.write(s0);f.flush();os.fsync(f.fileno())
    s.spawn_provider();after=s.identity('process_after');restart=restart_assertions(before,after,digest(s.runtime.read_bytes()))
    if not all(restart.values()):return {'status':'PRECONDITION_NOT_MET','restart':restart}
    before_replay=s.snap('before_rollback_replay',aid)
    # Either actual completion or denial is collected; neither result is forced.
    observed=s.send(s.directory/'original','rollback_replay',['START','COMPLETE']);after_replay=s.snap('after_rollback_replay',aid)
    delta=after_replay['execution_line_count']-before_replay['execution_line_count']
    return {'status':'PASS','classification':'CHARACTERIZATION_COMPLETE_NOT_PRIMARY_PROPERTY_SCORE','restart':restart,'observed_events':observed,'execution_delta':delta,'rollback_reenabled_authority':delta>0,'anti_rollback_resistance':'NOT_ESTABLISHED','primary_MP005_result':'NOT_RUN','sequence_telemetry':after_replay['local_execution_seq_values']}

def run():
    require_linux();install_loopback_guard()
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--session',default='MP005_SIMULATED_SMOKE_R1');a=ap.parse_args()
    root=a.root.resolve()
    if not a.session.replace('_','').isalnum():raise HarnessError('Unsafe simulation session name')
    verify_sources(root);verify_harness(root)
    output=root/'evidence/simulated_smoke'/a.session;output.mkdir(parents=True,exist_ok=False)
    write(output/'environment.json',{'classification':'DISPOSABLE_LOCAL_SIMULATION_ONLY','platform':platform.platform(),'python':sys.version,'filesystem':filesystem_info(output),'source_hashes':verify_sources(root),'live_host_contact_permitted':False})
    results=[];stop=False
    for provider in ('provider_a','provider_b'):
        for case in ('S00','S01','S02','S03'):
            d=output/provider/case;d.mkdir(parents=True);s=Scenario(root,d,provider)
            try:
                if case=='S00':result=normal(s,a.session)
                elif case in ('S01','S02'):result=invalid_start(s,case=='S02')
                else:result=rollback(s,a.session)
            except PreconditionError as ex:result={'status':'PRECONDITION_NOT_MET','error':str(ex)};stop=True
            except Exception as ex:result={'status':'HARNESS_ERROR','error':type(ex).__name__+': '+str(ex)};stop=True
            finally:s.close()
            result.update(provider=provider,case=case,live_rehearsal='NOT_RUN',scored_MP005='NOT_RUN');write(d/'case_results.json',result);inventory(d);results.append(result)
            if stop or result['status']=='FAIL':stop=True;break
        if stop:break
    write(output/'case_results.json',{'classification':'SIMULATION_ONLY','results':results,'scored_MP005':'NOT_RUN','remaining_cases':'NOT_RUN' if stop else None,'mandatory_next_step':'STOP_FOR_OPERATOR_REVIEW'});inventory(output)
    print(json.dumps({'output':str(output),'simulation_cases':len(results),'scored_MP005':'NOT_RUN','next':'STOP_FOR_OPERATOR_REVIEW'}))
    return 2 if stop else 0
