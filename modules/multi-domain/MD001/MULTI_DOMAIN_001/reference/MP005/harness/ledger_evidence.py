"""Independent ledger verifier and explicit Linux-only bootstrap. No network."""
import hashlib,json,os,sys
from pathlib import Path

TAG=b'NUVL-MP-CONSUME-LEDGER-v1|'
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
def sha(v):return hashlib.sha256(v).hexdigest()
def unique(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('duplicate_json_key')
        d[k]=v
    return d
def inspect(raw,provider,aid,snapshot):
    if raw and not raw.endswith(b'\n'):raise ValueError('partial ledger')
    rows=[];spent={};head=None
    for seq,line in enumerate(raw.splitlines(),1):
        e=json.loads(line.decode('utf-8'),object_pairs_hook=unique)
        if not isinstance(e,dict) or type(e.get('version')) is not int or e['version']!=1 or e.get('provider_id')!=provider:raise ValueError('version/provider')
        if type(e.get('ledger_seq')) is not int or e['ledger_seq']!=seq:raise ValueError('sequence')
        if 'previous_entry_hash' not in e or e['previous_entry_hash']!=head:raise ValueError('previous hash')
        for k in ('authorization_id','authorization_nonce','operation_id'):
            if not isinstance(e.get(k),str) or not e[k]:raise ValueError('identity')
        if e['authorization_id'] in spent:raise ValueError('duplicate authority')
        if e.get('entry_hash')!=sha(TAG+canonical({k:v for k,v in e.items() if k!='entry_hash'})):raise ValueError('entry hash')
        if canonical(e)!=line:raise ValueError('noncanonical entry')
        spent[e['authorization_id']]={'nonce':e['authorization_nonce']};head=e['entry_hash'];rows.append(e)
    expected={'version':1,'spent':spent,'ledger_seq':len(rows),'ledger_head':head}
    return {'ledger_sha256':sha(raw),'ledger_length':len(raw),'ledger_line_count':len(raw.splitlines()),'ledger_entry_count':len(rows),'ledger_seq':len(rows),'ledger_head':head,'ledger_authorization_present':aid in spent,'ledger_chain_valid':True,'ledger_entries':rows,'snapshot_ledger_seq':snapshot.get('ledger_seq'),'snapshot_ledger_head':snapshot.get('ledger_head'),'snapshot_matches_ledger':canonical(snapshot)==canonical(expected)}
def capture(state,aid,out):
    state=Path(state);out=Path(out);role=state.name.removesuffix('_spent_state.json')
    p=state.with_name(role+'_consume_ledger.jsonl');raw=p.read_bytes()
    info=inspect(raw,role.upper(),aid,json.loads(state.read_bytes(),object_pairs_hook=unique))
    with (out/'consume_ledger.jsonl').open('xb') as f:f.write(raw)
    info['ledger_path']=str(p.resolve());return info
def validate_saved(folder,metadata):
    folder=Path(folder);role=Path(metadata['state_path']).name.removesuffix('_spent_state.json')
    expected=inspect((folder/'consume_ledger.jsonl').read_bytes(),role.upper(),metadata['authorization_id'],json.loads((folder/'spent_state.json').read_bytes(),object_pairs_hook=unique))
    if any(metadata.get(k)!=v for k,v in expected.items()):raise ValueError('saved ledger metadata mismatch')
    return metadata
def bootstrap(state_dir,role):
    if sys.platform!='linux':raise RuntimeError('Linux required; no persistence emulation')
    if role not in ('provider_a','provider_b'):raise ValueError('provider')
    directory=Path(state_dir);directory.mkdir(parents=True,exist_ok=True)
    ledger=directory/(role+'_consume_ledger.jsonl');snapshot=directory/(role+'_spent_state.json')
    if ledger.exists() or snapshot.exists():raise FileExistsError('Bootstrap requires absent ledger AND snapshot')
    for p,data in ((ledger,b''),(snapshot,canonical({'version':1,'spent':{},'ledger_seq':0,'ledger_head':None}))):
        with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    fd=os.open(str(directory),os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return ledger,snapshot
def replay_checks(before,after,events):
    keys=('ledger_sha256','ledger_length','ledger_line_count','ledger_entry_count','ledger_seq','ledger_head','spent_sha256','spent_length','execution_sha256','execution_length','execution_line_count','matching_execution_count')
    result={'unchanged_'+k:before[k]==after[k] for k in keys}
    result.update(auth_stays_spent=before['ledger_authorization_present'] and after['ledger_authorization_present'] and after['authorization_present'],snapshot_matches_ledger=after['snapshot_matches_ledger'],one_deny_auth_spent=len(events)==1 and events[0].get('stage')=='DENY' and events[0].get('reason_code')=='auth_spent',no_start_complete=all(e.get('stage') not in ('START','COMPLETE') for e in events),signed_deny_head=all(e.get('ledger_seq')==before['ledger_seq'] and e.get('ledger_head')==before['ledger_head'] for e in events))
    return result
def advance_checks(before,after,events):
    rows=after['ledger_entries'];entry=rows[-1] if rows else {}
    return {'exactly_one_entry':after['ledger_entry_count']==before['ledger_entry_count']+1,'exactly_one_sequence':after['ledger_seq']==before['ledger_seq']+1,'prefix_preserved':rows[:-1]==before['ledger_entries'],'previous_hash':entry.get('previous_entry_hash')==before['ledger_head'],'new_hash_valid':after['ledger_chain_valid'] and entry.get('entry_hash')==after['ledger_head'],'authorization_matches':entry.get('authorization_id')==after['authorization_id'] and after['ledger_authorization_present'],'snapshot_matches_ledger':after['snapshot_matches_ledger'],'execution_once':after['execution_line_count']==before['execution_line_count']+1 and after['matching_execution_count']==before['matching_execution_count']+1,'signed_start_complete_head':[e.get('stage') for e in events]==['START','COMPLETE'] and all(e.get('ledger_seq')==after['ledger_seq'] and e.get('ledger_head')==after['ledger_head'] and e.get('authorization_id')==entry.get('authorization_id') and e.get('authorization_nonce')==entry.get('authorization_nonce') and e.get('operation_id')==entry.get('operation_id') for e in events)}
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description='Explicit fresh-state Linux bootstrap; never overwrites history')
    ap.add_argument('--state-dir',type=Path,required=True);ap.add_argument('--provider',choices=['provider_a','provider_b'],required=True);a=ap.parse_args()
    bootstrap(a.state_dir,a.provider)
