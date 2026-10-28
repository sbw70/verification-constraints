"""Offline synthetic helper checks. These are NOT S00–S03 or provider execution."""
import copy,json,sys,unittest,uuid
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import common

@contextmanager
def build_fixture():
    p=Path(__file__).resolve().parents[1]/'operator/build_checks/helper_fixtures'/uuid.uuid4().hex
    p.mkdir(parents=True,exist_ok=False)
    yield str(p)  # Retain synthetic helper fixtures; these are not provider/simulation evidence.

class EvidenceHelpers(unittest.TestCase):
    def test_non_linux_guard_refuses(self):
        with patch.object(common.sys,'platform','win32'):
            with self.assertRaises(common.PreconditionError):common.require_linux()
    def test_simulation_url_rejects_lab_addresses(self):
        for host in ('192.168.1.100','192.168.1.102','192.168.1.106','192.168.1.118'):
            with self.assertRaises(common.PreconditionError):common.loopback('http://'+host+':9191/boundary')
    def test_same_pid_does_not_prove_restart(self):
        p={'hostname':'synthetic','boot_id':'synthetic','pid':10,'start_ticks':20,'runtime_path':'/x.py','runtime_sha256':'h','state_path':'/state','command_line':['python','/x.py'],'cwd':'/'}
        self.assertFalse(common.restart_assertions(p,copy.deepcopy(p),'h')['new_process_instance'])
    def test_later_pid_without_runtime_identity_fails(self):
        p={'hostname':'synthetic','boot_id':'synthetic','pid':10,'start_ticks':20,'runtime_path':'/x.py','runtime_sha256':'h','state_path':'/state','command_line':['python','/x.py'],'cwd':'/'}
        q=dict(p,pid=11,start_ticks=30,runtime_path='/other.py')
        self.assertFalse(all(common.restart_assertions(p,q,'h').values()))
    def test_snapshot_hashes_are_bound_to_raw_files(self):
        with build_fixture() as d:
            p=Path(d);(p/'state.json').write_text('{"version":1,"spent":{"x":{"nonce":"n"}}}')
            s=common.state_snapshot(p/'state.json',p/'absent.jsonl','x',p/'snapshot')
            self.assertFalse(s['execution_log_exists']);self.assertEqual(common.validate_snapshot(p/'snapshot')['spent_count'],1)
            (p/'snapshot/spent_state.json').write_text('{"version":1,"spent":{}}')
            with self.assertRaises(common.HarnessError):common.validate_snapshot(p/'snapshot')
    def test_log_cursor_rejects_replaced_history(self):
        with build_fixture() as d:
            p=Path(d)/'association.jsonl';p.write_bytes(b'{}\n');cursor=common.log_cursor(p);p.write_bytes(b'[]\n')
            with self.assertRaises(common.PreconditionError):common.correlate(Path(d),p,cursor,{'provider_id':'PROVIDER_A'})
    def test_http_response_without_signed_deny_is_not_replay_pass(self):
        s={'spent_sha256':'s','spent_length':3,'spent_count':1,'execution_log_exists':True,'execution_sha256':'e','execution_length':2,'execution_line_count':1,'matching_execution_count':1,'authorization_present':True}
        self.assertFalse(all(common.replay_assertions(s,dict(s),[]).values()))
    def test_extra_execution_defeats_signed_deny(self):
        s={'spent_sha256':'s','spent_length':3,'spent_count':1,'execution_log_exists':True,'execution_sha256':'e','execution_length':2,'execution_line_count':1,'matching_execution_count':1,'authorization_present':True}
        changed=dict(s,execution_sha256='new',execution_length=4,execution_line_count=2,matching_execution_count=2)
        self.assertFalse(all(common.replay_assertions(s,changed,[{'stage':'DENY','reason_code':'auth_spent'}]).values()))

if __name__=='__main__':unittest.main(verbosity=2)
