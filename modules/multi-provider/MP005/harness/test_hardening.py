"""Offline adversarial checks. No server, consume, mint, fsync shim or network."""
import base64,copy,importlib.util,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ledger_evidence import canonical,sha,TAG,inspect
from common import require_linux,PreconditionError,loopback

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def entry(provider,seq=1,previous=None,aid='authorization-X'):
    e=dict(version=1,provider_id=provider,ledger_seq=seq,authorization_id=aid,authorization_nonce='nonce-X',operation_id='operation-X',previous_entry_hash=previous)
    e['entry_hash']=sha(TAG+canonical(e));return e
def main():
    root=Path(__file__).resolve().parents[1];checks=[]
    recorder=load('offline_recorder',root/'association/association_recorder.py')
    recorder.REGISTRY,_=recorder.load_registry(root/'association/provider_registry.json')
    for role in ('provider_a','provider_b'):
        provider=role.upper();m=load('offline_'+role,root/role/(role+'.py'))
        e=entry(provider);raw=canonical(e)+b'\n';snapshot=dict(version=1,spent={'authorization-X':{'nonce':'nonce-X'}},ledger_seq=1,ledger_head=e['entry_hash'])
        assert m.validate_ledger(b'')==({},0,None)
        spent,seq,head=m.validate_ledger(raw);assert spent==snapshot['spent'] and seq==1 and head==e['entry_hash']
        assert inspect(raw,provider,'authorization-X',snapshot)['snapshot_matches_ledger']
        assert not inspect(raw,provider,'authorization-X',dict(version=1,spent={},ledger_seq=0,ledger_head=None))['snapshot_matches_ledger']
        e2=entry(provider,2,e['entry_hash'],'authorization-Y');two=raw+canonical(e2)+b'\n'
        assert m.validate_ledger(two)[1:]==(2,e2['entry_hash'])
        checks.append(role+': empty/one/two-entry roundtrip and stale snapshot detection')
        bad=[('malformed',b'{\n'),('partial',raw[:-1]),('duplicate_json_key',raw.replace(b'"version":1',b'"version":1,"version":1')),('blank',b'\n'),('noncanonical',json.dumps(e,indent=2).encode()+b'\n')]
        for field,value in [('provider_id','OTHER'),('version',2),('version',True),('ledger_seq',2),('ledger_seq',True),('previous_entry_hash','bad'),('entry_hash','0'*64),('authorization_id',''),('authorization_nonce',None),('operation_id',None)]:
            changed=dict(e);changed[field]=value;bad.append((field,canonical(changed)+b'\n'))
        duplicate=entry(provider,2,e['entry_hash']);bad.append(('duplicate_auth_valid_hash',raw+canonical(duplicate)+b'\n'))
        for label,data in bad:
            for validator in (m.validate_ledger,lambda data:inspect(data,provider,'authorization-X',snapshot)):
                try:validator(data)
                except (ValueError,TypeError,KeyError,UnicodeError):pass
                else:raise AssertionError(role+' accepted '+label)
            checks.append(role+': rejects '+label)
        m.LEDGER_SEQ=1;m.LEDGER_HEAD=e['entry_hash']
        package=m.make_boundary_package('operation-X','fixture','START','authorization-X','nonce-X')
        result=recorder.inspect_submission(canonical(package));assert result['sig_valid'] is True
        assert result['unknown_fields']['event']=={'ledger_seq':1,'ledger_head':e['entry_hash']}
        for field,value in [('ledger_head','b'*64),('ledger_seq',2)]:
            tampered=copy.deepcopy(package);tampered['event'][field]=value
            assert recorder.inspect_submission(canonical(tampered))['sig_valid'] is False
        checks.append(role+': actual candidate boundary signatures cover both ledger fields; unchanged recorder accepts')
    for url in ('http://192.168.1.106:9090','http://192.168.1.118:9090'):
        try:loopback(url)
        except PreconditionError:checks.append('non-loopback rejected without contacting '+url)
        else:raise AssertionError('lab URL accepted')
    if sys.platform!='linux':
        try:require_linux()
        except PreconditionError:checks.append('non-Linux guard refuses')
        else:raise AssertionError('platform guard failed')
    print(json.dumps({'classification':'OFFLINE_SYNTHETIC_CHECKS_ONLY','passed':len(checks),'checks':checks,'provider_server_started':False,'simulation_executed':False,'network_contact':False},indent=2))
    return 0
if __name__=='__main__':sys.exit(main())
