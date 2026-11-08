"""Prepare/launch the independent observer; never start it during local validation."""
import argparse
import json
from pathlib import Path
import sys
import deployment as d
import observer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['inspect', 'run', 'checkpoint', 'verify'])
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--approval', type=Path)
    parser.add_argument('--identity', type=Path)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--after', type=Path)
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--mode', choices=['fresh', 'replay'])
    args = parser.parse_args()
    d.verify_baseline()
    config = d.read(args.config)
    plan = observer.observer_plan(config)
    plan['config_path'] = args.config.resolve()
    if args.action == 'inspect':
        print(json.dumps({'status': 'PREPARATION_ONLY_OBSERVER_NOT_STARTED',
                          **{key: str(value) for key, value in plan.items()}}, indent=2))
    elif args.action == 'run':
        if d.no_redirect(plan['root']) != d.ROOT:
            raise ValueError('observer_must_be_installed_in_reviewed_MH001_run_root')
        d.require_approval(args.approval, args.config, plan['trust'])
        observer.load_registry(plan, config['session'])
        module = observer.recorder()
        module.HOST, module.PORT = config['listen']['host'], config['listen']['port']
        sys.argv = [str(d.ROOT / 'observer_support/association_recorder.py'),
                    '--session-id', config['session'], '--registry', str(plan['registry']),
                    '--manifest', str(args.config.resolve()), '--contract', str(d.ROOT / 'REVIEW.md'),
                    '--log', str(plan['log'])]
        module.main()
    elif args.action == 'checkpoint':
        if not all((args.identity, args.before, args.mode, args.output)):
            parser.error('checkpoint requires --identity --before --mode --output')
        observer.h.write(args.output, observer.checkpoint(plan, config['session'],
                         d.read(args.identity), args.before, args.mode))
    else:
        if not all((args.checkpoint, args.after, args.output)):
            parser.error('verify requires --checkpoint --after --output')
        checked = d.read(args.checkpoint)
        if checked['session'] != config['session']:
            raise ValueError('checkpoint_session_mismatch')
        result = observer.verify_outcome(plan, checked, args.after)
        observer.h.write(args.output, result)
        print(json.dumps(result, indent=2))
        if result['status'] != 'VERIFIED_PROVIDER_OUTCOME':
            raise SystemExit(2)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit('PRECONDITION_NOT_MET: ' + str(error))
