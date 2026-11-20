"""Extract one request from an exported reassembled TCP direction; compare actual bytes."""
import argparse
import io
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "runtime"))
import wire
from artifact import digest, canonical_bytes


def extract(raw):
    stream=io.BytesIO(raw)
    method,target,fields,count=wire.request_head(stream)
    body=wire.read_exact(stream,count)
    if method!=b'POST' or target!=b'/verify' or stream.read(1):
        raise ValueError('requires exactly one complete POST /verify request in one TCP direction')
    if wire.values(fields,b'x-mh-destination')!=[b'PROVIDER_B']:
        raise ValueError('destination')
    return body


def main():
    p=argparse.ArgumentParser(description=__doc__)
    s=p.add_subparsers(dest='command',required=True)
    e=s.add_parser('extract');e.add_argument('--stream',type=Path,required=True);e.add_argument('--out',type=Path,required=True)
    c=s.add_parser('compare');c.add_argument('--producer',type=Path,required=True);c.add_argument('--relay-ingress',type=Path,required=True);c.add_argument('--relay-egress',type=Path,required=True);c.add_argument('--verifier',type=Path,required=True);c.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.command=='extract':
        raw=a.stream.read_bytes();body=extract(raw)
        with a.out.open('xb') as f:f.write(body)
        print(json.dumps(dict(stream=str(a.stream),stream_sha256=digest(raw),body=str(a.out),body_sha256=digest(body))))
    else:
        paths={n:getattr(a,n.replace('-','_')) for n in ['producer','relay-ingress','relay-egress','verifier']}
        data={n:path.read_bytes() for n,path in paths.items()}
        result=dict(equal=len(set(data.values()))==1,observations={n:dict(path=str(paths[n]),bytes=len(raw),sha256=digest(raw)) for n,raw in data.items()})
        with a.out.open('xb') as f:f.write(canonical_bytes(result))
        print(json.dumps(result,indent=2))
        if not result['equal']:raise SystemExit(1)


if __name__=='__main__':main()
