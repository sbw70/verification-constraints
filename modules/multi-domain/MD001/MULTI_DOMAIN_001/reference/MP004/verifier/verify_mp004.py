"""MP004 offline evidence verifier. Does not import the recorder."""
import argparse, base64, copy, hashlib, json, platform, re, sys
from pathlib import Path
from datetime import datetime, timezone
import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

ANCHORS = {'PROVIDER_A':'sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff', 'PROVIDER_B':'sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225'}
FIELDS = set('version operation_id binding provider_id key_id stage boundary_value authorization_id authorization_nonce reason_code'.split())
REASONS = set('binding_mismatch auth_missing auth_malformed auth_provider_mismatch auth_id_mismatch auth_bad_sig auth_request_mismatch auth_context_mismatch policy_denied auth_spent auth_state_error'.split())
def digest(b): return hashlib.sha256(b).hexdigest()
def canonical(v): return json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')
def pairs(items):
    d={}
    for k,v in items:
        if k in d: raise ValueError('duplicate JSON key')
        d[k]=v
    return d
def loads(b):
    return json.loads(b, object_pairs_hook=pairs, parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite number')))
def read(p): return loads(p.read_text(encoding='utf-8-sig'))
def save(p,v): p.write_bytes(canonical(v)+b'\n')
def safe(root, rel):
    p=(root/rel).resolve()
    if not p.is_relative_to(root.resolve()): raise ValueError('path outside workspace')
    return p
def validate_anchor(provider, key, declared_id):
    if not isinstance(key,Ed25519PublicKey): raise ValueError('not Ed25519')
    raw=key.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    if 'sha256:'+digest(raw)!=ANCHORS[provider] or declared_id!=ANCHORS[provider]: raise ValueError('trust anchor mismatch')
def hex64(v): return isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) is not None
def decode_sig(s):
    if not isinstance(s,str) or not re.fullmatch('[A-Za-z0-9_-]+',s): raise ValueError('signature encoding')
    b=base64.urlsafe_b64decode(s+'='*((-len(s))%4))
    if len(b)!=64 or base64.urlsafe_b64encode(b).decode().rstrip('=')!=s: raise ValueError('signature length/canonical encoding')
    return b
def verify(record, keys):
    r={'schema_status':'invalid','trust_status':'not_checked','cryptographic_status':'not_checked','contextual_status':'not_requested','interpretation_status':'not_requested'}
    try:
        raw=base64.b64decode(record['raw_body_b64'], validate=True)
        package=loads(raw.decode('utf-8'))
        if not isinstance(package,dict) or set(package)!= {'alg','event','signature'} or package['alg']!='Ed25519': raise ValueError('package schema')
        e=package['event']
        if not isinstance(e,dict) or set(e)!=FIELDS or type(e['version']) is not int or e['version']!=1: raise ValueError('event schema')
        if not all(hex64(e[f]) for f in ('operation_id','binding','boundary_value')): raise ValueError('hash format')
        if e['authorization_id'] is not None and not hex64(e['authorization_id']): raise ValueError('authorization id')
        if e['authorization_nonce'] is not None and (not isinstance(e['authorization_nonce'],str) or not e['authorization_nonce']): raise ValueError('nonce')
        if e['stage'] in ('START','COMPLETE'):
            if not e['authorization_id'] or not e['authorization_nonce'] or e['reason_code'] is not None: raise ValueError('lifecycle structure')
        elif e['stage']=='DENY':
            if not isinstance(e['reason_code'],str) or e['reason_code'] not in REASONS: raise ValueError('denial reason')
        else: raise ValueError('stage')
        if not isinstance(e['provider_id'],str) or not isinstance(e['key_id'],str): raise ValueError('identity type')
        sig=decode_sig(package['signature'])
        r.update(schema_status='valid',event=e,raw_sha256=digest(raw),signed_event_sha256=digest(canonical({'event':e,'signature':package['signature']})))
        if e['provider_id'] not in ANCHORS or e['key_id']!=ANCHORS[e['provider_id']]:
            r['trust_status']='rejected'; return r
        r['trust_status']='matched'
        try:
            keys[e['provider_id']].verify(sig,b'NUVL-MP-BOUNDARY-v1|'+canonical(e))
            r['cryptographic_status']='valid'
        except InvalidSignature: r['cryptographic_status']='invalid'
    except (ValueError,TypeError,KeyError,UnicodeError) as ex: r['error']=str(ex)
    return r
def accepted(r): return r['schema_status']=='valid' and r['trust_status']=='matched' and r['cryptographic_status']=='valid'
def compare(record,r,label):
    c={'label':label,'comparisons':{}}
    values={'sig_valid':r['cryptographic_status']=='valid','registry_match':r['trust_status']=='matched','raw_sha256':r.get('raw_sha256'),'signed_event_sha256':r.get('signed_event_sha256')}
    if accepted(r): values['verification_code']='ok'
    elif r['cryptographic_status']=='invalid': values['verification_code']='signature_rejected'
    for k,v in r.get('event',{}).items(): values['claimed_'+k]=v
    for k,v in values.items():
        if k in record:
            match=(record[k]==v)
            if k=='verification_code' and r['cryptographic_status']=='invalid': match=record[k]!='ok'
            c['comparisons'][k]={'recorder':record[k],'independent':v,'matches':match}
    return c
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest',required=True); ap.add_argument('--output',required=True); args=ap.parse_args()
    root=Path.cwd().resolve(); out=safe(root,args.output)
    out.mkdir(parents=True,exist_ok=False)
    metadata={'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'cryptography':cryptography.__version__,'invocation':sys.argv,'verifier_sha256':digest(Path(__file__).read_bytes()),'status':'INCOMPLETE'}
    status='INCOMPLETE'; records=[]; comparisons=[]; cases=[]; fixture_entries=[]
    try:
        mp=safe(root,args.manifest); m=read(mp); metadata['manifest_sha256']=digest(mp.read_bytes())
        for line in (root/'configs/MP004_LOCK_SHA256SUMS.txt').read_text().splitlines():
            h,name=line.split('  ',1)
            if digest(safe(root/'configs',name).read_bytes())!=h: raise ValueError('lock mismatch: '+name)
        for name,key in [('MP004_CONTRACT.md','contract_sha256'),('MP004_SOURCE_MANIFEST.json','source_manifest_sha256'),('MP004_PUBLICATION_COMPARISON.json','publication_comparison_sha256')]:
            if digest((root/'configs'/name).read_bytes())!=m[key]: raise ValueError('manifest lock mismatch')
        sm=read(root/'configs/MP004_SOURCE_MANIFEST.json'); source=safe(root,m['source_path_base'])
        for f in sm['files']:
            b=safe(source,f['path']).read_bytes()
            if len(b)!=f['bytes'] or digest(b)!=f['sha256']: raise ValueError('source mismatch: '+f['path'])
        scored=source/'evidence/scored'
        checksum_count=0
        for line in (scored/'SHA256SUMS.txt').read_text().splitlines():
            h,name=line.split(None,1)
            if digest(safe(scored,name.lstrip('*')).read_bytes())!=h: raise ValueError('scored source checksum mismatch')
            checksum_count+=1
        metadata.update(source_files_checked=len(sm['files']),mp003_checksums_checked=checksum_count)
        registry=read(safe(root,m['trust_registry'])); keys={}
        for provider,pin in ANCHORS.items():
            entry=registry['providers'][provider]
            p=safe(safe(root,m['trust_registry']).parent,entry['public_key_file'])
            key=serialization.load_pem_public_key(p.read_bytes())
            validate_anchor(provider,key,entry['key_id'])
            keys[provider]=key
        rows=[loads(line) for line in safe(root,m['association_path']).read_bytes().splitlines()]
        submissions=[r for r in rows if r['record_type']=='SUBMISSION']
        if len(rows)!=19 or len(submissions)!=m['expected_submission_count']: raise ValueError('source coverage mismatch')
        byseq={r['record_seq']:r for r in submissions}
        if len(byseq)!=len(submissions) or set(byseq)!=set(range(2,19)): raise ValueError('record sequence coverage')
        for spec in m['records']:
            row=byseq[spec['record_seq']]
            if digest(base64.b64decode(row['raw_body_b64'],validate=True))!=spec['raw_package_sha256']: raise ValueError('package pin mismatch')
            r=verify(row,keys); r.update(record_seq=spec['record_seq'],scope=spec['scope'])
            if 'expected' in spec:
                expected=spec['expected']; auth=None
                request_hash=digest(safe(source,spec['request_path']).read_bytes())
                binding=digest(('NUVL_BIND_V1|'+request_hash+'|'+spec['context']).encode())
                op=digest(('NUVL-MP-OP-v1|'+binding).encode())
                if spec['authorization_path']: auth=read(safe(source,spec['authorization_path']))['authorization']
                independently_derived={'binding':binding,'operation_id':op,'authorization_id':auth['authorization_id'] if auth else None,'authorization_nonce':auth['nonce'] if auth else None}
                if any(expected[k]!=v for k,v in independently_derived.items()): raise ValueError('expected source derivation mismatch')
                r['contextual_status']='valid' if accepted(r) and all(r['event'].get(k)==v for k,v in expected.items()) else 'invalid'
            records.append(r)
        contextual=[r for r in records if r['contextual_status']!='not_requested']
        cases.append({'case':'B01','pass':len(records)==17 and len(contextual)==15 and all(accepted(r) for r in records) and all(r['contextual_status']=='valid' for r in contextual)})
        # Freeze fixture bytes and their manifest BEFORE evaluating negative cases.
        base=copy.deepcopy(byseq[4]); pkg=loads(base64.b64decode(base['raw_body_b64']).decode())
        n1=copy.deepcopy(base); p1=copy.deepcopy(pkg); p1['event']['boundary_value']='0'*64 if pkg['event']['boundary_value']!='0'*64 else '1'*64; n1['raw_body_b64']=base64.b64encode(canonical(p1)).decode()
        n2=copy.deepcopy(base); p2=copy.deepcopy(pkg); sig=bytearray(decode_sig(p2['signature'])); sig[0]^=1; p2['signature']=base64.urlsafe_b64encode(sig).decode().rstrip('='); n2['raw_body_b64']=base64.b64encode(canonical(p2)).decode()
        n5a=copy.deepcopy(base); n5a.update(sig_valid=False,registry_match=False,verification_code='laboratory_false_invalid')
        n5b=copy.deepcopy(n1); n5b.update(sig_valid=True,registry_match=True,verification_code='ok')
        c02=next(s['expected'] for s in m['records'] if s['record_seq']==11)
        fixture_values={'N01':n1,'N02':n2,'N03':{'source_record_seq':4,'override_provider':'PROVIDER_B'},'N04':{'provider_id':'PROVIDER_B','operation_id':c02['operation_id'],'stage':'EXECUTED','source_case':'C02'},'N05a':n5a,'N05b':n5b}
        for recipe in m['fixture_recipes']:
            path=safe(root,recipe['output']); path.parent.mkdir(parents=True,exist_ok=True); content=canonical(fixture_values[recipe['id']])+b'\n'
            if path.exists() and path.read_bytes()!=content: raise ValueError('existing fixture differs; retain and revise run')
            if not path.exists(): path.write_bytes(content)
            fixture_entries.append(dict(recipe,output_sha256=digest(content),source_raw_sha256=digest(base64.b64decode(byseq[recipe['source_record_seq']]['raw_body_b64']))))
        save(out/'fixture_manifest.json',fixture_entries); metadata['fixture_manifest_sha256']=digest((out/'fixture_manifest.json').read_bytes())
        for case in ('N01','N02','N05a','N05b'):
            r=verify(fixture_values[case],keys); r['label']=case; records.append(r)
            ok=accepted(r) if case=='N05a' else (r['schema_status']=='valid' and r['trust_status']=='matched' and r['cryptographic_status']=='invalid')
            c=compare(fixture_values[case],r,case); comparisons.append(c)
            if case.startswith('N05'): ok=ok and not c['comparisons']['sig_valid']['matches'] and not c['comparisons']['verification_code']['matches']
            cases.append({'case':case,'pass':ok,'actual':r['cryptographic_status']})
        try:
            keys['PROVIDER_B'].verify(decode_sig(pkg['signature']),b'NUVL-MP-BOUNDARY-v1|'+canonical(pkg['event'])); wrong_fails=False
        except InvalidSignature: wrong_fails=True
        # Test the production anchor loader, without altering pinned trust material.
        try:
            validate_anchor('PROVIDER_A',keys['PROVIDER_B'],ANCHORS['PROVIDER_A']); mapping_refused=False
        except ValueError: mapping_refused=True
        cases.append({'case':'N03','pass':wrong_fails and mapping_refused,'direct_signature_invalid':wrong_fails,'anchor_pin_rejects_wrong_key':mapping_refused})
        denial=verify(byseq[11],keys); summary=fixture_values['N04']
        contradiction=accepted(denial) and all(denial['event'][k]==summary[k] for k in ('provider_id','operation_id')) and denial['event']['stage']=='DENY' and denial['event']['reason_code']=='auth_provider_mismatch'
        cases.append({'case':'N04','pass':contradiction,'interpretation':'contradicted_by_authenticated_denial' if contradiction else 'unsupported','limitation':'Provider-reported denial; no universal or physical non-execution proof.'})
        # Only now consult recorder classifications for original submissions.
        comparisons.extend(compare(byseq[r['record_seq']],r,str(r['record_seq'])) for r in records if 'record_seq' in r)
        if set(c['case'] for c in cases)!=set(m['required_case_ids']) or len(cases)!=7: raise ValueError('case coverage')
        status='PASS' if all(c['pass'] for c in cases) else 'FAIL'
    except Exception as ex: metadata['error']=type(ex).__name__+': '+str(ex)
    metadata.update(status=status,finished_utc=datetime.now(timezone.utc).isoformat())
    save(out/'run_metadata.json',metadata); save(out/'case_results.json',cases)
    for name,items in [('record_results.jsonl',records),('recorder_comparison.jsonl',comparisons)]:
        (out/name).write_bytes(b''.join(canonical(v)+b'\n' for v in items))
    if not (out/'fixture_manifest.json').exists(): save(out/'fixture_manifest.json',fixture_entries)
    (out/'SUMMARY.md').write_text('# MP004 offline verification\n\nOverall: **'+status+'**\n\n'+ '\n'.join('- '+c['case']+': '+('PASS' if c['pass'] else 'FAIL') for c in cases)+'\n\nAuthenticates provider-signed statements. Does not prove physical consequences, evidence completeness, immutable storage, or global chronology. The association recorder was not invoked or imported.\n'+ ('\nError: '+metadata['error']+'\n' if 'error' in metadata else ''),encoding='utf-8')
    (out/'SHA256SUMS.txt').write_text(''.join(digest(p.read_bytes())+'  '+p.name+'\n' for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'),encoding='ascii')
    print(json.dumps({'status':status,'output':str(out),'error':metadata.get('error')}))
    return {'PASS':0,'FAIL':1,'INCOMPLETE':2}[status]
if __name__=='__main__': sys.exit(main())
