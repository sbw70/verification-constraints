"""Four-case AE001 campaign; runs unchanged role sources on isolated paths."""
import argparse,base64,copy,hashlib,json,os,socket,subprocess,sys,time,uuid
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f: f.write(canonical(v)+b'\n')
def url64(b): return base64.urlsafe_b64encode(b).decode().rstrip('=')
def un64(s): return base64.urlsafe_b64decode(s+'='*((-len(s))%4))
def checksums(root):
    p=root/'SHA256SUMS.txt'
    with p.open('x',encoding='ascii') as f:
        for item in sorted(root.rglob('*')):
            if item.is_file() and item!=p: f.write(sha(item.read_bytes())+'  '+item.relative_to(root).as_posix()+'\n')

class Campaign:
    def __init__(self,a):
        self.root=Path(a.root).resolve(); self.cfg=read(self.root/'configs/AE001_RUN_MANIFEST.json'); self.a=a
        self.ssh=['ssh','-i',str(Path(a.identity).resolve()),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(Path(a.known_hosts).resolve()),'-o','ConnectTimeout=7']
        self.run=self.root/'evidence'/a.phase/a.run_id
        self.run.mkdir(parents=True,exist_ok=False)
        self.remote_root='/home/seth/ARTIFACT_EXHANGE/'+a.run_id
        self.started={}; self.deployed=set(); self.results=[]; self.pins={}
    def remote(self,role,code):
        host=self.cfg['hosts']['relay' if role=='association' else role]
        cmd='echo '+base64.b64encode(code.encode()).decode()+' | base64 -d | python3'
        r=subprocess.run(self.ssh+['seth@'+host,'python3'],input=code,capture_output=True,text=True,timeout=45)
        if r.returncode: raise RuntimeError(role+': '+r.stderr+r.stdout)
        return json.loads(r.stdout)
    def rootcode(self,tail): return 'from pathlib import Path\nimport json,base64,hashlib,os,sys,socket,subprocess,time,signal\nr=Path('+repr(self.remote_root)+')\n'+tail
    def grab(self,role,rels):
        code=self.rootcode('files={}\nfor name in '+repr(rels)+':\n p=r/name\n files[name]=base64.b64encode(p.read_bytes()).decode() if p.exists() else None\nprint(json.dumps(files))')
        return {k:base64.b64decode(v) if v is not None else None for k,v in self.remote(role,code).items()}
    def source_check(self):
        for entry in self.cfg['files']:
            if sha((self.root/entry['path']).read_bytes())!=entry['sha256']: raise RuntimeError('Local source/config identity changed: '+entry['path'])
        lock=self.root/'configs/AE001_LOCK_SHA256SUMS.txt'
        if self.a.phase=='scored':
            for line in lock.read_text().splitlines():
                h,name=line.split('  ',1)
                if sha((self.root/'configs'/name).read_bytes())!=h: raise RuntimeError('Frozen lock mismatch')
        save(self.run/'input_identity.json',{'contract_sha256':sha((self.root/'configs/AE001_CONTRACT.md').read_bytes()),'manifest_sha256':sha((self.root/'configs/AE001_RUN_MANIFEST.json').read_bytes()),'campaign_sha256':sha(Path(__file__).read_bytes()),'phase':self.a.phase,'run_id':self.a.run_id})
        for name in ('AE001_CONTRACT.md','AE001_RUN_MANIFEST.json'):
            (self.run/name).write_bytes((self.root/'configs'/name).read_bytes())
    def deploy(self):
        for role in ('provider_a','provider_b','relay'):
            names=['scripts/launch_role.py','configs/AE001_CONTRACT.md','configs/AE001_RUN_MANIFEST.json']
            if role=='relay':
                prefixes=('source/MP003/intermediary/','source/MP003/association/')
            else: prefixes=('source/MP003/'+role+'/',)
            names += [f['path'] for f in self.cfg['files'] if f['path'].startswith(prefixes)]
            bundle={name:base64.b64encode((self.root/name).read_bytes()).decode() for name in names}
            code=self.rootcode('r.mkdir(parents=True,exist_ok=False)\nbundle='+repr(bundle)+'\nfor name,encoded in bundle.items():\n p=r/name\n p.parent.mkdir(parents=True,exist_ok=True)\n with p.open("xb") as f: f.write(base64.b64decode(encoded))\n(r/"runtime").mkdir()\n')
            if role.startswith('provider'):
                code+='d=r/"runtime"/'+repr(role)+'\nd.mkdir()\n(d/'+repr(role+'_spent_state.json')+').write_bytes(b\'{"version":1,"spent":{}}\')\n'
            code+='print(json.dumps({"deployed":True,"source_hashes":{name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in bundle},"hostname":socket.gethostname(),"python":sys.version}))'
            data=self.remote(role,code); self.deployed.add(role)
            for name,digest in data['source_hashes'].items():
                if digest!=sha((self.root/name).read_bytes()): raise RuntimeError('Deployment copy mismatch')
            save(self.run/(role+'_deployment.json'),data)
            # Preserve only relevant existing MP003 state hashes for noninterference.
            if role.startswith('provider'):
                code='from pathlib import Path\nimport hashlib,json\nr=Path('+repr('/home/seth/MULTI_PROVIDER_003/'+role)+')\nprint(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.glob("*") if p.name.endswith(("spent_state.json","execution.jsonl"))}))'
                self.pins[role]=self.remote(role,code)
        save(self.run/'canonical_state_before.json',self.pins)
    def start(self,role):
        code=self.rootcode('role='+repr(role)+'\nlog=r/"runtime"/(role+"_console.txt")\nf=log.open("xb")\nenv=dict(os.environ,PYTHONDONTWRITEBYTECODE="1")\np=subprocess.Popen([sys.executable,"-u","-B",str(r/"scripts/launch_role.py"),role,"--root",str(r)],cwd=r,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=env)\nf.close()\n(r/"runtime"/(role+".pid")).write_text(str(p.pid))\nprint(json.dumps({"pid":p.pid}))')
        pid=self.remote(role,code)['pid']; self.started[role]=pid
        host=self.cfg['hosts']['relay' if role=='association' else role]
        port=self.cfg['ports']['association' if role=='association' else 'relay' if role=='relay' else 'provider']
        deadline=time.monotonic()+12
        while time.monotonic()<deadline:
            try:
                with socket.create_connection((host,port),timeout=1): return
            except OSError: time.sleep(.15)
        raise RuntimeError('Role failed to listen: '+role)
    def snapshot(self,role):
        files=self.grab(role,['runtime/'+role+'/'+role+'_spent_state.json','runtime/'+role+'/'+role+'_execution.jsonl'])
        state=next(v for k,v in files.items() if k.endswith('spent_state.json'))
        execution=next(v for k,v in files.items() if k.endswith('execution.jsonl'))
        return {'state_bytes':state,'execution_bytes':execution,'spent':json.loads(state)['spent'],'executions':[json.loads(l) for l in (execution or b'').splitlines()]}
    def save_snapshot(self,case,role,when,s):
        (case/(role+'_state_'+when+'.json')).write_bytes(s['state_bytes'])
        # Empty file means there is no execution log yet; preserve absence separately.
        (case/(role+'_execution_'+when+'.jsonl')).write_bytes(s['execution_bytes'] or b'')
        return {'state_sha256':sha(s['state_bytes']),'execution_sha256':sha(s['execution_bytes'] or b''),'execution_log_exists':s['execution_bytes'] is not None}
    def mint(self,case,issuer,request,context):
        remote_dir='runtime/inputs/'+case.name
        body=base64.b64encode(request).decode()
        filename='source/MP003/'+issuer+'/mint_authorization_'+issuer[-1]+'.py'
        code=self.rootcode('d=r/'+repr(remote_dir)+'\nd.mkdir(parents=True,exist_ok=False)\nrequest=d/"request.json"\nrequest.write_bytes(base64.b64decode('+repr(body)+'))\noutput=d/"authorization.json"\np=subprocess.run([sys.executable,"-B",str(r/'+repr(filename)+'),"--request-file",str(request),"--context",'+repr(context)+',"--output",str(output)],capture_output=True,text=True)\nif p.returncode: raise RuntimeError(p.stderr+p.stdout)\nprint(json.dumps({"package":base64.b64encode(output.read_bytes()).decode(),"header":(d/"authorization.json.b64").read_text(),"mint_output":p.stdout}))')
        data=self.remote(issuer,code)
        package=base64.b64decode(data['package']); (case/'original_authorization.json').write_bytes(package)
        (case/'mint_output.txt').write_text(data['mint_output'],encoding='utf-8')
        return json.loads(package),data['header']
    def events(self):
        data=self.grab('association',['runtime/association.jsonl'])['runtime/association.jsonl']
        return [json.loads(line) for line in (data or b'').splitlines()]
    def case(self,name):
        case=self.run/name; case.mkdir()
        request=canonical({'action':'ae001_test','case':name,'run_id':self.a.run_id,'nonce':uuid.uuid4().hex})
        (case/'request.json').write_bytes(request)
        context='CTX_AE001_'+name; request_hash=sha(request); binding=sha(('NUVL_BIND_V1|'+request_hash+'|'+context).encode()); op=sha(('NUVL-MP-OP-v1|'+binding).encode())
        issuer='provider_a' if name=='N02' else 'provider_b'
        package,header=self.mint(case,issuer,request,context)
        issued_key=serialization.load_pem_public_key((self.root/'source/MP003'/issuer/(issuer+'_issuance_public.pem')).read_bytes())
        issued_key.verify(un64(package['signature']),b'NUVL-MP-AUTH-v1|'+canonical(package['authorization']))
        if name=='N01':
            package=copy.deepcopy(package); sig=bytearray(un64(package['signature'])); sig[0]^=1; package['signature']=url64(sig); header=url64(canonical(package))
            try: issued_key.verify(un64(package['signature']),b'NUVL-MP-AUTH-v1|'+canonical(package['authorization'])); raise RuntimeError('Tamper precondition failed')
            except InvalidSignature: pass
        (case/'sent_authorization.json').write_bytes(canonical(package)); (case/'sent_authorization.b64').write_text(header,encoding='ascii')
        expected='auth_bad_sig' if name=='N01' else 'auth_provider_mismatch' if name=='N02' else None
        before={r:self.snapshot(r) for r in ('provider_a','provider_b')}
        state_evidence={r:{'before':self.save_snapshot(case,r,'before',s)} for r,s in before.items()}
        expected_headers={'X-Verification-Context':context,'X-Provider-B-Authorization':header,'Content-Type':'application/octet-stream'}
        # Requester contacts only the relay for operation submission.
        import urllib.request
        url='http://'+self.cfg['hosts']['relay']+':'+str(self.cfg['ports']['relay'])+'/nuvl'
        req=urllib.request.Request(url,request,expected_headers,method='POST')
        with urllib.request.urlopen(req,timeout=8) as response: status=response.status; response_body=response.read()
        save(case/'requester_delivery.json',{'url':url,'headers':expected_headers,'http_status':status,'response_body_b64':base64.b64encode(response_body).decode(),'request_sha256':request_hash,'binding':binding,'operation_id':op,'target_provider':'PROVIDER_B','issuer_provider':package['authorization']['provider_id']})
        deadline=time.monotonic()+12; matched=[]
        wanted=2 if expected else 3
        while time.monotonic()<deadline:
            rows=self.events(); matched=[]
            for row in rows:
                if row.get('record_type')=='SUBMISSION':
                    raw=base64.b64decode(row['raw_body_b64']); event=json.loads(raw)['event']
                    if event['operation_id']==op: matched.append((row,raw))
            if len(matched)>=wanted: break
            time.sleep(.15)
        after={r:self.snapshot(r) for r in ('provider_a','provider_b')}
        stages={'PROVIDER_A':[],'PROVIDER_B':[]}; signatures=True; target_events=[]
        for i,(row,raw) in enumerate(matched):
            signed=json.loads(raw); e=signed['event']; provider=e['provider_id']; r='provider_'+provider[-1].lower()
            key=serialization.load_pem_public_key((self.root/'source/MP003/association/trust'/(r+'_public.pem')).read_bytes())
            rawkey=key.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
            try: key.verify(un64(signed['signature']),b'NUVL-MP-BOUNDARY-v1|'+canonical(e))
            except InvalidSignature: signatures=False
            signatures=signatures and e['key_id']=='sha256:'+sha(rawkey) and e['binding']==binding
            stages[provider].append(e['stage'])
            if provider=='PROVIDER_B': target_events.append(e)
            (case/('boundary_'+str(i+1)+'_'+provider+'_'+e['stage']+'.json')).write_bytes(raw)
        save(case/'association_records.json', [r for r,b in matched])
        delivery=self.grab('relay',['runtime/relay_delivery.jsonl'])['runtime/relay_delivery.jsonl']
        attempts=[]
        for line in delivery.splitlines():
            t=json.loads(line); body=json.loads(base64.b64decode(t['body_b64']))
            if body['request_repr']==request_hash: attempts.append((t,body))
        save(case/'relay_delivery.json',[t for t,b in attempts])
        delivered={}
        for t,b in attempts:
            role='provider_b' if self.cfg['hosts']['provider_b'] in t['url'] else 'provider_a'
            delivered[role]=(b=={'request_repr':request_hash,'verification_context':context,'binding':binding,'provider_authorization_b64':header if role=='provider_b' else ''})
        for r,s in after.items(): state_evidence[r]['after']=self.save_snapshot(case,r,'after',s)
        save(case/'state_presence_and_hashes.json',state_evidence)
        # An authenticated unexpected admission is a property failure, even
        # when it generates more events than the expected denial.
        unexpected_admission = expected and signatures and any(s in ('START','COMPLETE') for s in stages['PROVIDER_B'])
        if len(matched)!=wanted and not unexpected_admission:
            raise RuntimeError('Boundary evidence missing/extra for '+name)
        auth_id=package['authorization']['authorization_id']; nonce=package['authorization']['nonce']
        expected_stages=['DENY'] if expected else ['START','COMPLETE']
        ok=signatures and status==204 and response_body==b'' and stages['PROVIDER_A']==['DENY'] and stages['PROVIDER_B']==expected_stages and delivered=={'provider_a':True,'provider_b':True}
        a_events=[json.loads(raw)['event'] for row,raw in matched if json.loads(raw)['event']['provider_id']=='PROVIDER_A']
        ok=ok and all(e['reason_code']=='auth_missing' for e in a_events)
        ok=ok and all(e['authorization_id']==auth_id and e['authorization_nonce']==nonce and e['reason_code']==expected for e in target_events)
        ok=ok and before['provider_a']['state_bytes']==after['provider_a']['state_bytes'] and before['provider_a']['execution_bytes']==after['provider_a']['execution_bytes']
        if expected:
            ok=ok and before['provider_b']['state_bytes']==after['provider_b']['state_bytes'] and before['provider_b']['execution_bytes']==after['provider_b']['execution_bytes'] and auth_id not in after['provider_b']['spent']
        else:
            newexec=after['provider_b']['executions'][len(before['provider_b']['executions']):]
            ok=ok and auth_id in after['provider_b']['spent'] and len(after['provider_b']['spent'])==len(before['provider_b']['spent'])+1 and len(newexec)==1 and newexec[0]['authorization_id']==auth_id and newexec[0]['operation_id']==op
        result={'case':name,'status':'PASS' if ok else 'FAIL','request_sha256':request_hash,'operation_id':op,'authorization_id':auth_id,'provider_stages':stages,'reason':expected,'signatures_verified':signatures,'relay_attempts_match_inputs':delivered}
        save(case/'result.json',result); self.results.append(result)
        if not ok: raise AssertionError('Property case failed: '+name)
    def shutdown(self):
        for role in ('association','relay','provider_a','provider_b'):
            if role in self.started:
                code=self.rootcode('os.kill('+str(self.started[role])+',signal.SIGINT)\nprint(json.dumps({"signal":"SIGINT","pid":'+str(self.started[role])+'}))')
                try: self.remote(role,code)
                except Exception as ex: self.hiccup('Shutdown '+role+': '+str(ex))
        time.sleep(.5)
    def collect(self):
        for role in self.deployed:
            roles=['relay','association'] if role=='relay' else [role]
            rels=['runtime/'+r+'_console.txt' for r in roles]
            if role=='relay': rels+=['runtime/association.jsonl','runtime/relay_delivery.jsonl']
            else: rels+=['runtime/'+role+'/'+role+'_spent_state.json','runtime/'+role+'/'+role+'_execution.jsonl']
            data=self.grab(role,rels)
            for name,content in data.items():
                if content is not None:
                    p=self.run/'final'/role/Path(name).name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(content)
        after={}
        for role in self.pins:
            code='from pathlib import Path\nimport hashlib,json\nr=Path('+repr('/home/seth/MULTI_PROVIDER_003/'+role)+')\nprint(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.glob("*") if p.name.endswith(("spent_state.json","execution.jsonl"))}))'
            after[role]=self.remote(role,code)
        save(self.run/'canonical_state_after.json',after)
        if after!=self.pins: raise RuntimeError('Canonical MP003 state changed')
        if self.results:
            rows=[json.loads(line) for line in (self.run/'final/relay/association.jsonl').read_bytes().splitlines()]
            if len(self.results)==4 and (len(rows)!=12 or rows[-1]['record_type']!='SESSION_END' or rows[-1]['submission_count']!=10): raise RuntimeError('Final association coverage incomplete')
    def hiccup(self,text):
        with (self.root/'CHECK_ME/AE001_HICCUPS.txt').open('a',encoding='utf-8') as f: f.write('\n'+self.a.run_id+': '+text+'\n')
    def execute(self):
        status='INCOMPLETE'; error=None
        try:
            self.source_check(); self.deploy()
            for role in ('association','provider_a','provider_b','relay'): self.start(role)
            for case in ('B01','N01','N02','B02'): self.case(case)
            status='PASS'
        except AssertionError as ex: status='FAIL'; error=str(ex); self.hiccup(error)
        except Exception as ex: error=type(ex).__name__+': '+str(ex); self.hiccup(error)
        finally:
            self.shutdown()
            try: self.collect()
            except Exception as ex: status='INCOMPLETE'; error=(error or '')+' Collection: '+str(ex); self.hiccup(error)
        save(self.run/'SCORECARD.json',{'status':status,'run_id':self.a.run_id,'phase':self.a.phase,'cases':self.results,'error':error})
        checksums(self.run)
        print(json.dumps({'status':status,'run_id':self.a.run_id,'cases':{c['case']:c['status'] for c in self.results},'error':error}))
        return 0 if status=='PASS' else 1

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--identity',required=True); ap.add_argument('--known-hosts',required=True); ap.add_argument('--phase',choices=['preflight','scored'],required=True); ap.add_argument('--run-id',required=True); a=ap.parse_args()
    if not a.run_id.startswith('AE001_') or not a.run_id.replace('_','').isalnum(): raise ValueError('Invalid run ID')
    return Campaign(a).execute()
if __name__=='__main__': sys.exit(main())
