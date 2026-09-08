"""Execute v1.17 headless gates, including full repeated lab unless explicitly smoke-only."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
BASELINE='87c1d0e4ba519e082feaf70848c84862acedc0ff'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'.work/reports/combat')
    parser.add_argument('--require-clean',action='store_true')
    parser.add_argument('--compare',type=Path)
    parser.add_argument('--smoke-only',action='store_true',help='10 seeds/scenario; cannot close the phase')
    args=parser.parse_args();args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=True)
    godot=args.godot.resolve();checks=[]
    def check(name,command,expected=None,summary=False,timeout=90):
        try:
            run=subprocess.run(list(map(str,command)),cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
            output=run.stdout+run.stderr
            passed=run.returncode==0 and 'SCRIPT ERROR' not in output and 'ERROR:' not in output
            if expected is not None:passed=passed and output.strip()==expected
            if summary:
                rows=[json.loads(line) for line in output.splitlines() if line.startswith('{')]
                passed=passed and len(rows)==1 and rows[0].get('assertions',0)>0 and not rows[0].get('failures')
            result=dict(name=name,status='pass' if passed else 'fail',command=list(map(str,command)),exit_code=run.returncode,output=output)
        except (OSError,subprocess.TimeoutExpired,ValueError) as error:result=dict(name=name,status='fail',error=str(error))
        checks.append(result);print(name+': '+result['status'],flush=True)
        return result['status']=='pass'
    if args.require_clean:check('clean_before',['git','status','--porcelain'],expected='')
    check('baseline_tag',['git','rev-parse','v1.16-canonical-data^{commit}'],expected=BASELINE)
    check('baseline_ancestor',['git','merge-base','--is-ancestor',BASELINE,'HEAD'])
    check('godot_version',[godot,'--version'],expected='4.7.2.stable.official.ed1daf0bf')
    check('generated_source_parity',[sys.executable,'tools/migration/combat_data.py','--check'])
    check('schema_source_levels_and_metrics',[sys.executable,'tools/validation/test_combat_data.py'])
    check('legacy_divergence_and_582_level_oracle',['node','tools/validation/combat_legacy_oracle.mjs'],summary=True)
    check('godot_import',[godot,'--headless','--path','game','--editor','--import','--quit'])
    for suite in ('combat','combat_replay'):check(suite+'_headless',[godot,'--headless','--path','game','--script',f'res://tests/{suite}_test.gd'],summary=True)
    if all(c['status']=='pass' for c in checks):
        command=[sys.executable,'tools/balance_lab/run.py','--godot',godot,'--output',args.output/'lab','--count',10 if args.smoke_only else 1000]
        if args.compare:command+=['--compare',args.compare]
        check('repeated_lab_and_replays',command,timeout=900)
        if (args.output/'lab/summary.json').exists():
            summary=json.loads((args.output/'lab/summary.json').read_text(encoding='utf-8'))
            sys.path.insert(0,str(ROOT/'tools/migration'))
            import combat_data
            try:
                for path in (args.output/'lab').glob('*.replay.json'):combat_data.validate(ROOT,'replay',json.loads(path.read_text(encoding='utf-8')))
                checks.append(dict(name='serialized_replay_schema',status='pass'))
            except ValueError as error:checks.append(dict(name='serialized_replay_schema',status='fail',error=str(error)))
            if summary['status']!='pass':checks.append(dict(name='lab_report_status',status='fail'))
    if args.require_clean:check('clean_after',['git','status','--porcelain'],expected='')
    report=dict(phase='v1.17',status='pass' if all(c['status']=='pass' for c in checks) else 'fail',profile='smoke_only' if args.smoke_only else 'full_12000_repeated',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),baseline=BASELINE,cleanCheckout=args.require_clean,checks=checks,limits=['Foundation and canonical full profiles remain separate required gates.','No physical-device, Android/iOS export, UI or final-art production validation claimed.','A local pass is not evidence of remote CI execution.'])
    (args.output/'gates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'profile':report['profile'],'checks':len(checks),'report':str(args.output/'gates.json')}))
    return int(report['status']!='pass')

if __name__=='__main__':raise SystemExit(main())
