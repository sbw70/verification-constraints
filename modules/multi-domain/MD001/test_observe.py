"""Offline checks of extraction/comparison boundaries; synthetic streams only."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import uuid
from observe import extract
import wire


def main():
    b=Path(__file__).resolve().parent
    out=b/'validation'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_')+uuid.uuid4().hex[:8])
    out.mkdir(parents=True)
    body=b'{"event":"synthetic transport fixture"}'
    head=b'POST /verify HTTP/1.1\r\nHost: 127.0.0.1\r\nX-MH-Destination: PROVIDER_B\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'
    packet=head+body
    checks=[dict(name='valid_one_direction_body_exact',passed=extract(packet)==body)]
    for name,data in [('truncated',packet[:-1]),('extra_request',packet+packet),('wrong_path',packet.replace(b'/verify',b'/wrong')),('wrong_destination',packet.replace(b'PROVIDER_B',b'PROVIDER_A')),('chunked',packet.replace(b'Content-Length:',b'Transfer-Encoding: chunked\r\nContent-Length:'))]:
        try:extract(data);ok=False
        except (ValueError,wire.WireError):ok=True
        checks.append(dict(name=name+'_rejected',passed=ok))
    result=dict(mode='SYNTHETIC_REASSEMBLED_STREAM_UNIT_CHECKS',checks=checks,passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),physical_capture_validated=False)
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(directory=str(out),**result),indent=2))
    return int(result['failed']!=0)


if __name__=='__main__':raise SystemExit(main())
