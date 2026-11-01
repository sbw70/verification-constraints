"""Independent read-only R3 review. Writes findings outside simulation evidence."""
import ast,base64,difflib,hashlib,json
from pathlib import Path
from cryptography.hazmat.primitives import serialization

import argparse
ap=argparse.ArgumentParser(description='Read-only complete R3 evidence review; writes findings outside evidence')
ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ROOT=ap.parse_args().root.resolve()
E=ROOT/'evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R3'
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def filemap(root):return {p.relative_to(root).as_posix():digest(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
def inventory(folder):
    inv=folder/'SHA256SUMS.txt';entries={}
    for line in inv.read_text().splitlines():
        expected,relative=line.split('  ',1);p=(folder/relative).resolve()
        assert p.is_relative_to(folder.resolve()) and relative not in entries
        assert digest(p.read_bytes())==expected,relative
        entries[relative]=expected
    assert set(entries)=={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p!=inv}
    return len(entries)
if not E.is_dir():raise SystemExit('R3_NOT_RUN: complete local R3 evidence required; no review generated')
R3_START=filemap(E);R1=ROOT/'evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R1';R1_START=filemap(R1)
inventory_counts={'.':inventory(E)}
for p in sorted(p for p in E.rglob('SHA256SUMS.txt') if p!=E/'SHA256SUMS.txt'):inventory_counts[p.parent.relative_to(E).as_posix()]=inventory(p.parent)
preserved=load(ROOT/'notes/R1_PRESERVATION.json')
assert {k:v for k,v in R1_START.items() if k!='SHA256SUMS.txt'}==preserved['files']
assert R1_START['SHA256SUMS.txt']==preserved['inventory_sha256'];inventory(R1)
env=load(E/'environment.json');source=load(ROOT/'configs/MP005_SOURCE_MANIFEST.json')
for entry in source['frozen_implementation']:
    assert digest((ROOT/entry['path']).read_bytes())==entry['sha256']==env['implementation_hashes'][entry['path']]
saved_harness=load(E/'MP005_HARNESS_MANIFEST.json');assert digest((E/'MP005_HARNESS_MANIFEST.json').read_bytes())==env['harness_manifest_sha256']
for entry in saved_harness['mp005_harness_test_code']:assert digest((ROOT/entry['path']).read_bytes())==entry['sha256']
runtime_hashes={role:env['implementation_hashes'][role+'/'+role+'.py'] for role in ('provider_a','provider_b')}
TAG=b'NUVL-MP-CONSUME-LEDGER-v1|'
def chain(raw,provider):
    rows=[];spent={};head=None
    assert not raw or raw.endswith(b'\n')
    for seq,line in enumerate(raw.splitlines(),1):
        row=json.loads(line);assert canon(row)==line
        assert type(row['version']) is int and row['version']==1 and row['provider_id']==provider
        assert type(row['ledger_seq']) is int and row['ledger_seq']==seq and row['previous_entry_hash']==head
        assert row['entry_hash']==digest(TAG+canon({k:v for k,v in row.items() if k!='entry_hash'}))
        assert row['authorization_id'] not in spent
        assert all(isinstance(row[k],str) and row[k] for k in ('authorization_id','authorization_nonce','operation_id'))
        spent[row['authorization_id']]={'nonce':row['authorization_nonce']};head=row['entry_hash'];rows.append(row)
    return rows,{'version':1,'spent':spent,'ledger_seq':len(rows),'ledger_head':head}
def snap(folder,provider):
    raw={name:(folder/name).read_bytes() for name in ('consume_ledger.jsonl','spent_state.json','execution.jsonl')}
    ledger,expected=chain(raw['consume_ledger.jsonl'],provider)
    actual=json.loads(raw['spent_state.json']);assert actual==expected
    execution=[json.loads(x) for x in raw['execution.jsonl'].splitlines()]
    for x in execution:assert x['provider_id']==provider and x['result']=='executed'
    metadata=load(folder/'snapshot.json');aid=metadata['authorization_id']
    derived={'ledger_sha256':digest(raw['consume_ledger.jsonl']),'ledger_length':len(raw['consume_ledger.jsonl']),'ledger_line_count':len(raw['consume_ledger.jsonl'].splitlines()),'ledger_entry_count':len(ledger),'ledger_seq':len(ledger),'ledger_head':expected['ledger_head'],'ledger_entries':ledger,'ledger_authorization_present':aid in expected['spent'],'ledger_chain_valid':True,'spent_sha256':digest(raw['spent_state.json']),'spent_length':len(raw['spent_state.json']),'spent_count':len(expected['spent']),'authorization_present':aid in expected['spent'],'snapshot_ledger_seq':len(ledger),'snapshot_ledger_head':expected['ledger_head'],'snapshot_matches_ledger':True,'execution_sha256':digest(raw['execution.jsonl']),'execution_length':len(raw['execution.jsonl']),'execution_line_count':len(execution),'matching_execution_count':sum(x['authorization_id']==aid for x in execution)}
    assert all(metadata[k]==v for k,v in derived.items()),folder
    return {'raw':raw,'ledger':ledger,'snapshot':actual,'execution':execution,'metadata':metadata}
def key(role,issuance=False):
    path=ROOT/role/(role+('_issuance_public.pem' if issuance else '_public.pem'))
    return serialization.load_pem_public_key(path.read_bytes())
def decode(s):return base64.urlsafe_b64decode(s+'='*((-len(s))%4))
def authority(folder,role):
    ident=load(folder/'identity.json');request=(folder/'request.json').read_bytes();package=(folder/'authorization.json').read_bytes();header=(folder/'authorization.json.b64').read_text()
    assert digest(request)==ident['request_sha256'] and digest(package)==ident['package_sha256'] and digest(header.encode())==ident['header_sha256'] and decode(header)==package
    envelope=json.loads(package);a=envelope['authorization'];assert envelope['alg']=='Ed25519'
    key(role,True).verify(decode(envelope['signature']),b'NUVL-MP-AUTH-v1|'+canon(a))
    core={k:a[k] for k in ('version','provider_id','request_repr','verification_context','nonce')}
    assert a['authorization_id']==digest(b'NUVL-MP-AUTH-ID-v1|'+canon(core))==ident['authorization_id']
    assert a['provider_id']==role.upper()==ident['provider_id'] and a['nonce']==ident['authorization_nonce']
    assert a['request_repr']==digest(request) and a['verification_context']==ident['context']
    binding=digest(('NUVL_BIND_V1|'+digest(request)+'|'+ident['context']).encode())
    assert ident['binding']==binding and ident['operation_id']==digest(('NUVL-MP-OP-v1|'+binding).encode())
    return ident
def events(d,phase,ident,role):
    cursor=load(d/phase/'association_cursor.json');stream=(d/'association.jsonl').read_bytes()
    assert digest(stream[:cursor['byte_offset']])==cursor['prefix_sha256']
    matches=[];raw_matches=[]
    for line in stream[cursor['byte_offset']:].splitlines():
        record=json.loads(line);raw=base64.b64decode(record['raw_body_b64'],validate=True);p=json.loads(raw);e=p['event']
        if any(e.get(k)!=ident[k] for k in ('provider_id','authorization_id','operation_id')):continue
        assert all(e[k]==ident[k] for k in ('binding','authorization_nonce')) and p['alg']=='Ed25519'
        pub=key(role);assert e['key_id']=='sha256:'+digest(pub.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw))
        pub.verify(decode(p['signature']),b'NUVL-MP-BOUNDARY-v1|'+canon(e));matches.append(e);raw_matches.append(record['raw_body_b64'])
    saved=load(d/phase/'boundary_records.json')
    # Cursor may include replay later for the same original identity; phase saves only its initial completion.
    initial=matches[:len(saved)]
    assert [x['event'] for x in saved]==initial and [x['raw_body_b64'] for x in saved]==raw_matches[:len(saved)]
    if phase=='consume':assert [e['stage'] for e in initial]==['START','COMPLETE'];return initial
    assert len(matches)==len(saved)
    return matches
def advance(before,after,ev,ident):
    assert after['ledger'][:-1]==before['ledger'] and len(after['ledger'])==len(before['ledger'])+1
    e=after['ledger'][-1];assert e['previous_entry_hash']==before['snapshot']['ledger_head']
    assert all(e[k]==ident[k] for k in ('authorization_id','authorization_nonce','operation_id'))
    assert after['execution'][:-1]==before['execution'] and len(after['execution'])==len(before['execution'])+1
    assert all(after['execution'][-1][k]==ident[k] for k in ('authorization_id','operation_id'))
    assert [x['stage'] for x in ev]==['START','COMPLETE']
    assert all(x['ledger_seq']==e['ledger_seq'] and x['ledger_head']==e['entry_hash'] for x in ev)
def restart(d,role):
    b=load(d/'process_before.json');a=load(d/'process_after.json')
    for name in ('hostname','boot_id','command_line','cwd','runtime_path','state_path'):assert b[name]==a[name]
    assert a['hostname']=='xer0trust-4' and (b['pid'],b['start_ticks'])!=(a['pid'],a['start_ticks']) and a['start_ticks']>b['start_ticks']
    assert a['runtime_sha256']==b['runtime_sha256']==runtime_hashes[role]
    args=a['command_line'];assert args[args.index('--provider')+1]==role and args[args.index('--host')+1]=='127.0.0.1'
    assert args[args.index('--association-url')+1].startswith('http://127.0.0.1:')
    return {'before_pid':b['pid'],'after_pid':a['pid'],'before_start_ticks':b['start_ticks'],'after_start_ticks':a['start_ticks'],'boot_id':a['boot_id']}
cases=[];all_snapshots=0
for role in ('provider_a','provider_b'):
    provider=role.upper()
    code=(ROOT/role/(role+'.py')).read_text();tree=ast.parse(code)
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    assert ast.unparse(main.body[1]).startswith('SPENT = load_spent_state()')
    for case in ('S00','S01','S02','S03'):
        d=E/role/case
        if case in ('S01','S02'):
            console=(d/'provider_console_1.txt').read_text();reason='consume_ledger_missing' if case=='S01' else 'consume_ledger_invalid'
            assert console.rstrip().endswith('RuntimeError: '+reason) and 'Listening on' not in console
            assert not (d/'state'/(role+'_execution.jsonl')).exists() and not (d/'association.jsonl').read_bytes()
            observation=load(d/'startup_observation.json');assert observation['return_code']!=0 and observation['listener_usable'] is False and observation['runtime_sha256']==runtime_hashes[role]
            ledger=d/'state'/(role+'_consume_ledger.jsonl')
            if case=='S01':assert not ledger.exists()
            else:assert ledger.read_bytes()==b'{broken-json\n'
            assert load(d/'state'/(role+'_spent_state.json'))=={'version':1,'spent':{},'ledger_seq':0,'ledger_head':None}
            cases.append({'provider':role,'case':case,'verdict':'PASS','startup_reason':reason,'listener_verdict':'No server creation: uncaught load exception precedes HTTP server in matching source; preserved startup_observation records nonzero exit and failed loopback listener probe.','no_initialization_or_repair':True})
            continue
        snapshots={p.name:snap(p,provider) for p in d.iterdir() if p.is_dir() and (p/'snapshot.json').exists()};all_snapshots+=len(snapshots)
        old=authority(d/'original',role);fresh=authority(d/'fresh',role);assert old['authorization_id']!=fresh['authorization_id']
        pre=snapshots['pre_consume'];consumed=snapshots['consumed'];br=snapshots['before_replay'];ar=snapshots['after_replay'];bf=snapshots['before_fresh'];af=snapshots['after_fresh'];final=snapshots['final_original']
        ce=events(d,'consume',old,role);re=events(d,'replay',old,role);fe=events(d,'fresh_send',fresh,role)
        advance(pre,consumed,ce,old);proof=restart(d,role)
        assert consumed['raw']==br['raw']==ar['raw']==bf['raw']
        assert old['authorization_id'] in br['snapshot']['spent'] and old['authorization_id'] in ar['snapshot']['spent']
        assert len(re)==1 and re[0]['stage']=='DENY' and re[0]['reason_code']=='auth_spent'
        assert re[0]['ledger_seq']==1 and re[0]['ledger_head']==br['snapshot']['ledger_head']
        advance(bf,af,fe,fresh);assert af['raw']==final['raw']
        assert sum(x['authorization_id']==old['authorization_id'] for x in final['execution'])==1
        # Preserved transport uses the exact authority/header/request for both sends.
        for phase,identity,folder in [('consume',old,'original'),('replay',old,'original'),('fresh_send',fresh,'fresh')]:
            sent=load(d/phase/'send.json');assert sent['identity']==identity
            assert base64.b64decode(sent['request_b64'])==(d/folder/'request.json').read_bytes()
            assert sent['headers']['X-Verification-Context']==identity['context']
            assert sent['headers']['X-Provider-'+role[-1].upper()+'-Authorization']==(d/folder/'authorization.json.b64').read_text()
            assert sent['url'].startswith('http://127.0.0.1:')
        # Final provider-local files must equal the last captured raw evidence.
        for name,filename in [('consume_ledger.jsonl',role+'_consume_ledger.jsonl'),('spent_state.json',role+'_spent_state.json'),('execution.jsonl',role+'_execution.jsonl')]:assert (d/'state'/filename).read_bytes()==af['raw'][name]
        recovery=None
        if case=='S03':
            assert (d/'snapshot_restored_before_restart.json').read_bytes()==(d/'S0.json').read_bytes()
            assert load(d/'S0.json')==pre['snapshot']=={'version':1,'spent':{},'ledger_seq':0,'ledger_head':None}
            assert (d/'ledger_L1_before_restart.jsonl').read_bytes()==consumed['raw']['consume_ledger.jsonl']==br['raw']['consume_ledger.jsonl']
            lines=(d/'provider_console_2.txt').read_text().splitlines();recovery=json.loads(lines[0])
            assert recovery['event']=='SNAPSHOT_RECOVERED_FROM_LEDGER' and recovery['reason']=='valid_prefix_behind'
            assert recovery['ledger_seq']==1 and recovery['ledger_head']==br['snapshot']['ledger_head']
        cases.append({'provider':role,'case':case,'verdict':'PASS','restart':proof,'consumed_authority_remains_spent':True,'snapshot_rollback_resurrected':False if case=='S03' else None,'replay':{'reason':'auth_spent','START':0,'COMPLETE':0,'ledger_entries_delta':0,'ledger_bytes_delta':0,'execution_delta':0,'ledger_seq':1,'ledger_head':br['snapshot']['ledger_head']},'fresh':{'ledger_entries_delta':1,'ledger_sequence_delta':1,'execution_delta':1,'ledger_seq':2,'ledger_head':af['snapshot']['ledger_head']},'signed_boundary_examples':{'consume':ce,'replay':re,'fresh':fe},'recovery':recovery})
# Minimum additional reconciliation characterization: S04 ahead and S05 head/spent separately.
for role in ('provider_a','provider_b'):
    for case,variants in [('S04',['ahead']),('S05',['head','spent'])]:
        observations=[]
        for variant in variants:
            d=E/role/case if variant=='ahead' else E/role/case/variant
            history,reference=chain((d/'reference_history.jsonl').read_bytes(),role.upper())
            _,ledger_state=chain((d/'initial_ledger.jsonl').read_bytes(),role.upper())
            actual=load(d/'initial_snapshot.json')
            if variant=='ahead':assert actual==reference and actual['ledger_seq']>ledger_state['ledger_seq']
            elif variant=='head':assert actual['ledger_seq']==ledger_state['ledger_seq'] and actual['spent']==ledger_state['spent'] and actual['ledger_head']!=ledger_state['ledger_head']
            else:assert actual['ledger_seq']==ledger_state['ledger_seq'] and actual['ledger_head']==ledger_state['ledger_head'] and actual['spent']!=ledger_state['spent']
            assert (d/'state'/(role+'_consume_ledger.jsonl')).read_bytes()==(d/'initial_ledger.jsonl').read_bytes()
            assert (d/'state'/(role+'_spent_state.json')).read_bytes()==(d/'initial_snapshot.json').read_bytes()
            assert not (d/'state'/(role+'_execution.jsonl')).exists() and not (d/'association.jsonl').read_bytes()
            observation=load(d/'startup_observation.json');assert observation['return_code']!=0 and observation['listener_usable'] is False and observation['connect_ex_result']!=0 and observation['runtime_sha256']==runtime_hashes[role]
            console=(d/'provider_console_1.txt').read_text();reason='snapshot_ahead_of_ledger' if variant=='ahead' else 'snapshot_equal_seq_divergent'
            assert console.rstrip().endswith('RuntimeError: '+reason) and 'Listening on' not in console and 'SNAPSHOT_RECOVERED_FROM_LEDGER' not in console
            observations.append({'variant':variant,'verdict':'PASS','reason':reason,'snapshot_preserved':True,'ledger_preserved':True,'listener_usable':False})
        cases.append({'provider':role,'case':case,'verdict':'PASS','startup_observations':observations})
assert len(cases)==12 and all(x['verdict']=='PASS' for x in cases)
# Capture exact baseline/candidate differences without modifying implementations.
differences={}
for role in ('provider_a','provider_b'):
    name=role+'/'+role+'.py';base=ROOT/'baseline/pre_hardening'/name;current=ROOT/name
    expected=next(x for x in source['baseline_source'] if x['path']==name)['sha256'];assert digest(base.read_bytes())==expected
    differences[role]={'baseline_sha256':expected,'hardened_sha256':digest(current.read_bytes()),'different':base.read_bytes()!=current.read_bytes()}
    patch=''.join(difflib.unified_diff(base.read_text(encoding='utf-8-sig').splitlines(keepends=True),current.read_text().splitlines(keepends=True),fromfile='baseline/'+name,tofile='hardened/'+name))
    output=ROOT/'notes'/(role+'_R3_REVIEW_BASELINE_DIFF.patch');assert not output.exists();output.write_text(patch,encoding='utf-8')
semantics={'actual_implementation':'Exact match accepted; only a verified ledger-prefix snapshot may safe-forward. Missing cache rebuilds. Ahead, equal-sequence divergence, non-prefix older state and parseable invalid schema fail closed. Malformed JSON bytes are durably preserved before documented cache recovery; unreadable state fails closed.','runtime_coverage':'R3 S03 verifies safe-forward from genesis prefix; S04 verifies ahead failure; S05 separately verifies equal-sequence head and spent divergence. Other prefix/classification paths have offline pure tests; malformed archive recovery is not an added Linux runtime case.','freeze_recommendation':'REQUIRES_SEPARATE_OPERATOR_REVIEW_AND_VERIFIED_LIVE_CONFIGURATION; NO_PHASE_AUTHORIZATION'}
for old_session in ('R1','R2'):
    old_root=ROOT/'evidence/simulated_smoke'/('MP005_SIMULATED_SMOKE_'+old_session)
    pin=load(ROOT/'notes'/('MP005_'+old_session+'_R3_PRESERVATION.json'))['files']
    assert filemap(old_root)==pin
assert filemap(E)==R3_START and filemap(R1)==R1_START
report={'verdict':'PASS_FOR_TESTED_R3_RECONCILIATION_SCOPE','review_basis':'Raw captured evidence independently recomputed; no reliance on PASS labels; no provider/server/test execution','cases':cases,'inventory_entries_verified':inventory_counts,'snapshots_independently_revalidated':all_snapshots,'runtime_identities':differences,'R1_unchanged':True,'R2_unchanged':True,'R3_unchanged':True,'R1_file_count':len(R1_START),'R3_file_count':len(R3_START),'R1_inventory_sha256':R1_START['SHA256SUMS.txt'],'R3_inventory_sha256':R3_START['SHA256SUMS.txt'],'R3_all_file_hashes':R3_START,'ledger_validation':'All captured and final valid histories have contiguous 1-based integer seq, correct provider/version/domain-separated recomputed hashes/links, no duplicate authorization IDs, matching snapshots. S02 intentionally invalid ledgers preserved unmodified.','snapshot_reconciliation':semantics,'limitations':['No resistance to rolling back BOTH ledger and snapshot to older mutually consistent history.','S01/S02/S04/S05 retain startup exit/probe observation JSON plus raw traceback and matching source; this is application evidence, not an OS trace.','S03 captures the restored S0 bytes before restart as well as preserved L1 and recovery output.','R3 preserves the harness/config manifests and their hash; OS-level execution attestation is not claimed.','Durable fsync-before-START ordering is confirmed statically in matching provider code; evidence is not an OS syscall trace or power-loss/crash-window experiment.'],'live_topology_contact':False,'live_rehearsal':'NOT_RUN','scored_MP005':'NOT_RUN','GitHub_mutation':False,'final_lock_created':False}
out=ROOT/'notes/MP005_R3_INDEPENDENT_REVIEW.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'verdict':report['verdict'],'cases':[{'provider':x['provider'],'case':x['case'],'verdict':x['verdict'],'replay':x.get('replay'),'fresh':x.get('fresh')} for x in cases],'snapshots_checked':all_snapshots,'R1_files':len(R1_START),'R3_files':len(R3_START),'hashes':differences,'reconciliation':semantics},indent=2))
