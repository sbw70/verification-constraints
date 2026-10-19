import base64, copy, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mp004',ROOT/'verifier/verify_mp004.py')
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
class IndependentVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=next(json.loads(s) for s in (ROOT/'source/MP003/evidence/scored/association.jsonl').read_text().splitlines() if json.loads(s)['record_seq']==4)
        cls.keys={p:v.serialization.load_pem_public_key((ROOT/'source/MP003/association/trust'/('provider_'+p[-1].lower()+'_public.pem')).read_bytes()) for p in v.ANCHORS}
    def package(self,alter):
        r=copy.deepcopy(self.record); p=v.loads(base64.b64decode(r['raw_body_b64'])); alter(p); r['raw_body_b64']=base64.b64encode(v.canonical(p)).decode(); return v.verify(r,self.keys)
    def test_metadata_absence(self):
        r=v.verify({'raw_body_b64':self.record['raw_body_b64']},self.keys)
        self.assertTrue(v.accepted(r))
    def test_unknown_claims_cannot_select_key(self):
        self.assertEqual(self.package(lambda p:p['event'].update(provider_id='UNKNOWN'))['trust_status'],'rejected')
    def test_boolean_version_is_not_integer_version(self):
        self.assertEqual(self.package(lambda p:p['event'].update(version=True))['schema_status'],'invalid')
    def test_unicode_signed_change_fails(self):
        self.assertEqual(self.package(lambda p:p['event'].update(authorization_nonce='α'))['cryptographic_status'],'invalid')
    def test_duplicate_fields_rejected(self):
        with self.assertRaises(ValueError): v.loads('{"alg":"Ed25519","alg":"Ed25519"}')
    def test_nonfinite_json_rejected(self):
        with self.assertRaises(ValueError): v.loads('{"value":NaN}')
    def test_padded_signature_rejected(self):
        def alter(p): p['signature']+='='
        self.assertEqual(self.package(alter)['schema_status'],'invalid')
    def test_production_trust_loader_rejects_swapped_key(self):
        with self.assertRaises(ValueError): v.validate_anchor('PROVIDER_A',self.keys['PROVIDER_B'],v.ANCHORS['PROVIDER_A'])
    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError): v.safe(ROOT,'../MULTI_PROVIDER_003/configs/MP003_CONTRACT.md')
if __name__=='__main__': unittest.main(verbosity=2)
