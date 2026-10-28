"""Offline pure reconciliation tests. No provider startup or persistence emulation."""
import copy,importlib.util,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ledger_evidence import canonical,sha,TAG

def main():
    root=Path(__file__).resolve().parents[1];passed=[]
    for role in ('provider_a','provider_b'):
        spec=importlib.util.spec_from_file_location('reconciliation_'+role,root/role/(role+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        rows=[];spent={};snapshots=[dict(version=1,spent={},ledger_seq=0,ledger_head=None)]
        for seq in (1,2):
            e=dict(version=1,provider_id=role.upper(),ledger_seq=seq,authorization_id='AUTH_'+str(seq),authorization_nonce='NONCE_'+str(seq),operation_id='OP_'+str(seq),previous_entry_hash=rows[-1]['entry_hash'] if rows else None)
            e['entry_hash']=sha(TAG+canonical(e));rows.append(e);spent[e['authorization_id']]={'nonce':e['authorization_nonce']}
            snapshots.append(dict(version=1,spent=copy.deepcopy(spent),ledger_seq=seq,ledger_head=e['entry_hash']))
        raw=b''.join(canonical(e)+b'\n' for e in rows)
        assert m.classify_snapshot(snapshots[2],raw,snapshots[2]) is None;passed.append(role+': exact accepted')
        for index in (0,1):
            assert m.classify_snapshot(snapshots[index],raw,snapshots[2])=='valid_prefix_behind';passed.append(role+': valid prefix '+str(index)+' safe-forwards')
        bad=[]
        bad.append(('ahead',snapshots[2],canonical(rows[0])+b'\n',snapshots[1],'snapshot_ahead_of_ledger'))
        for seq in (1,2):
            for field in ('ledger_head','spent'):
                actual=copy.deepcopy(snapshots[seq])
                if field=='ledger_head':actual[field]='0'*64
                else:actual[field]['AUTH_1']['nonce']='DIVERGENT'
                reason='snapshot_not_valid_prefix' if seq==1 else 'snapshot_equal_seq_divergent'
                bad.append(('seq '+str(seq)+' '+field,actual,raw,snapshots[2],reason))
        for field,value in (('ledger_seq',True),('ledger_seq',-1),('version',True),('version',2),('spent',[])):
            actual=copy.deepcopy(snapshots[2]);actual[field]=value;bad.append(('invalid '+field,actual,raw,snapshots[2],'snapshot_structure_invalid'))
        for label,actual,history,expected,reason in bad:
            before=canonical(actual)
            try:m.classify_snapshot(actual,history,expected)
            except RuntimeError as ex:assert str(ex)==reason,(label,str(ex),reason)
            else:raise AssertionError('Accepted '+label)
            assert canonical(actual)==before;passed.append(role+': '+label+' fails closed without changing input')
        for malformed in (b'{broken-json',b'\xff',b'{"a":1,"a":2}',b'{"x":NaN}'):
            try:json.loads(malformed.decode('utf-8'),object_pairs_hook=m.strict_object,parse_constant=m.reject_json_constant)
            except (ValueError,UnicodeError):passed.append(role+': malformed JSON classified for preservation-first recovery')
            else:raise AssertionError('Malformed accepted')
    print(json.dumps({'classification':'OFFLINE_PURE_TESTS_NOT_R3_EXECUTION','passed':len(passed),'checks':passed,'providers_started':False,'network_contact':False},indent=2));return 0
if __name__=='__main__':sys.exit(main())
