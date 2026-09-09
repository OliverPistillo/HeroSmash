"""Orchestrate Godot fights and aggregate measurements; contains no combat implementation."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def command(godot,*args,timeout=300):
    cmd=[str(godot),"--headless","--path",str(ROOT/"game"),"--script","res://tests/combat_cli.gd","--",*map(str,args)]
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
    output=result.stdout+result.stderr
    summaries=[json.loads(line) for line in output.splitlines() if line.startswith('{')]
    if result.returncode or "SCRIPT ERROR" in output or "ERROR:" in output or len(summaries)!=1 or not summaries[0].get("ok"):
        raise RuntimeError(f"{cmd}: {output}")
    return summaries[0]

def distribution(values):
    values=sorted(values)
    return dict(mean=statistics.mean(values),median=statistics.median(values),p90=values[math.ceil(len(values)*.90)-1],p99=values[math.ceil(len(values)*.99)-1],minimum=values[0],maximum=values[-1])

def deterministic_digest(document):
    rows=[{k:v for k,v in row.items() if k!="runtime_us"} for row in document["records"]]
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def aggregate(document):
    rows=document["records"]
    outcomes=Counter(row["outcome"] for row in rows)
    winners=Counter(row["winner"] for row in rows if row["winner"])
    result=dict(scenarioId=document["scenarioId"],fights=len(rows),outcomes=dict(outcomes),wins=dict(winners),winRates={key:value/len(rows) for key,value in winners.items()},drawRate=outcomes['draw']/len(rows),timeoutRate=outcomes['timeout']/len(rows),duration_ms=distribution([r['duration_ms'] for r in rows]),event_count=distribution([r['event_count'] for r in rows]),runtime_us=distribution([r['runtime_us'] for r in rows]),deterministicMetricsHash=deterministic_digest(document),actors={})
    for identity in ('alpha','beta'):
        actors=[next(a for a in row['actors'] if a['id']==identity) for row in rows]
        totals=Counter()
        uptime=Counter()
        lethal=Counter()
        for actor in actors:
            for key,value in actor['metrics'].items():
                if isinstance(value,int):totals[key]+=value
            uptime.update(actor['metrics']['status_uptime_ms'])
            if actor['metrics']['lethal_source']:lethal[actor['metrics']['lethal_source']]+=1
        result['actors'][identity]=dict(totals=dict(totals),meanPerFight={k:v/len(rows) for k,v in totals.items()},statusUptimeMeanMs={k:v/len(rows) for k,v in uptime.items()},lethalSources=dict(lethal),remainingHpMilli=distribution([a['hp_milli'] for a in actors]),critRate=totals['crit_count']/totals['crit_attempts'] if totals['crit_attempts'] else 0,dodgeRate=totals['dodge_count']/totals['dodge_attempts'] if totals['dodge_attempts'] else 0)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'.work/reports/combat-lab')
    parser.add_argument('--count',type=int,default=1000)
    parser.add_argument('--first-seed',type=int,default=0)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--horizon-ms',type=int,default=45000)
    parser.add_argument('--compare',type=Path,help='prior summary from another clean checkout')
    args=parser.parse_args()
    if not 1<=args.workers<=8 or not 1<=args.count<=100000:parser.error('invalid workers/count')
    args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=True)
    godot=args.godot.resolve()
    version=subprocess.check_output([godot,'--version'],text=True).strip()
    if not version.startswith('4.7.2.stable.'):raise ValueError('Godot4.7.2 required')
    ids=command(godot,'list')['scenarios']
    if len(ids)!=12:raise ValueError('exactly12 scenarios required')
    started=time.perf_counter()
    timings=[]
    documents={}
    for pass_index in range(2):
        pass_start=time.perf_counter()
        directory=args.output/f'pass{pass_index+1}'
        directory.mkdir(exist_ok=True)
        def run(scenario):
            output=directory/(scenario+'.json')
            command(godot,'batch',scenario,args.first_seed,args.count,output,args.horizon_ms)
            return scenario,read(output)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for future in as_completed([pool.submit(run,scenario) for scenario in ids]):
                scenario,document=future.result()
                documents[(pass_index,scenario)]=document
                print(f'pass{pass_index+1} {scenario}: {document["count"]} fights',flush=True)
        timings.append(time.perf_counter()-pass_start)
    failures=[]
    summaries=[]
    for scenario in ids:
        first=documents[(0,scenario)];second=documents[(1,scenario)]
        for a,b in zip(first['records'],second['records'],strict=True):
            if a['seed']!=b['seed'] or a['eventHash']!=b['eventHash'] or a['resultHash']!=b['resultHash']:failures.append(dict(scenarioId=scenario,seed=a['seed'],reason='repeat'))
        if deterministic_digest(first)!=deterministic_digest(second):failures.append(dict(scenarioId=scenario,reason='metrics'))
        replay=args.output/(scenario+'-seed0.replay.json')
        command(godot,'run',scenario,args.first_seed,replay,args.horizon_ms)
        command(godot,'verify',replay)
        summaries.append(aggregate(first))
    for a,b in zip(documents[(0,'11_cross_timed')]['records'],documents[(0,'12_mirrored_sides')]['records'],strict=True):
        if a['eventHash']!=b['eventHash'] or a['resultHash']!=b['resultHash']:failures.append(dict(seed=a['seed'],reason='mirror'))
    if args.compare:
        previous=read(args.compare)
        if previous['firstSeed']!=args.first_seed or previous['seedsPerScenario']!=args.count or previous['horizon_ms']!=args.horizon_ms:raise ValueError('incomparable corpus')
        for old,new in zip(previous['scenarios'],summaries,strict=True):
            if old['scenarioId']!=new['scenarioId'] or old['deterministicMetricsHash']!=new['deterministicMetricsHash']:failures.append(dict(scenarioId=new['scenarioId'],reason='clean_checkout_comparison'))
    report=dict(phase='v1.17',status='pass' if not failures else 'fail',rulesetVersion='combat_v1.17.1',canonicalDataVersion='v1.16.1',dataHash=documents[(0,ids[0])]['dataHash'],commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),godot=version,platform=platform.platform(),python=platform.python_version(),workers=args.workers,firstSeed=args.first_seed,seedsPerScenario=args.count,horizon_ms=args.horizon_ms,uniqueFights=len(ids)*args.count,repeatedFights=len(ids)*args.count,replayRoundTrips=12,mirrorComparisons=args.count,replayHashFailures=len(failures),failures=failures,fullCorpusPassSeconds=timings,totalWallSeconds=time.perf_counter()-started,cleanCheckoutComparison=str(args.compare) if args.compare else None,scenarios=summaries,limits=['Mechanics fixtures, no balance tuning or production meta claim.','Desktop headless runtime is not mobile performance.','Explicit source-only multi-level bindings remain unresolved.'])
    write(args.output/'summary.json',report)
    print(json.dumps({k:report[k] for k in ('status','uniqueFights','repeatedFights','replayHashFailures','fullCorpusPassSeconds','totalWallSeconds')}))
    return int(bool(failures))

if __name__=='__main__':raise SystemExit(main())
