"""Reproduce the unpatched pinned failure; no Blender connection or scene access."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    assert os.environ.get('DISABLE_TELEMETRY') == 'true'
    from blender_mcp import server, telemetry, telemetry_decorator, trajectory, consent_prompt
    report = {
        'python': sys.executable, 'python_version': sys.version,
        'disable_telemetry': os.environ['DISABLE_TELEMETRY'],
        'module_paths': {m.__name__: m.__file__ for m in (server, telemetry, telemetry_decorator, trajectory, consent_prompt)},
        'config_spec': str(importlib.util.find_spec('blender_mcp.config')),
    }
    try:
        telemetry.TelemetryCollector()
    except ModuleNotFoundError as exc:
        report['exception_module'] = exc.name
        report['expected_failure_reproduced'] = exc.name == 'blender_mcp.config'
        (args.output_dir/'unpatched-traceback.txt').write_text(traceback.format_exc(), encoding='utf-8')
    else:
        report['expected_failure_reproduced'] = False
    (args.output_dir/'unpatched-reproduction.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['expected_failure_reproduced'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
