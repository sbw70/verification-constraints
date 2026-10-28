"""Single Linux-only local characterization entry point. No live mode."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'harness'))
from common import require_linux,PreconditionError

def main():
    # Deliberately before provider imports, argument processing, output creation or subprocesses.
    require_linux()
    from engine import run
    return run()
if __name__=='__main__':
    try:sys.exit(main())
    except PreconditionError as ex:
        print(json.dumps({'status':'PRECONDITION_NOT_MET','provider_started':False,'S00':'NOT_RUN','S01':'NOT_RUN','S02':'NOT_RUN','S03':'NOT_RUN','reason':str(ex)}));sys.exit(2)
