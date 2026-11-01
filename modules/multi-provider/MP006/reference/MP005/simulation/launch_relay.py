import argparse,importlib.util,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'harness'))
from common import require_linux,install_loopback_guard,loopback,verify_sources

def main():
    require_linux();install_loopback_guard()
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--provider',choices=['provider_a','provider_b'],required=True);ap.add_argument('--provider-url',required=True);ap.add_argument('--port',type=int,required=True);a=ap.parse_args()
    loopback(a.provider_url);root=Path(a.root).resolve();verify_sources(root)
    source=root/'intermediary/nuvl_multi_relay.py';spec=importlib.util.spec_from_file_location('mp005_loopback_relay',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.HOST='127.0.0.1';m.PORT=a.port
    # Sequential local characterization has only its target provider route.
    m.PROVIDERS=({'url':a.provider_url,'authorization_header':'X-Provider-'+a.provider[-1].upper()+'-Authorization'},)
    m.main()
if __name__=='__main__':main()
