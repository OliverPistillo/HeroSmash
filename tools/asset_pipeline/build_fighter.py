"""Rebuild/export/admit Solkael using an existing Blender, with independent GLB checks."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from fighter_glb import validate

ROOT=Path(__file__).resolve().parents[2]
HERO='solkael_lionheart'


def run(blender,script,args,log_root):
    command=[blender,'--background','--factory-startup','--python-exit-code','1','--python',str(ROOT/'tools/asset_pipeline'/script),'--',*map(str,args)]
    started=time.monotonic()
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
    output=result.stdout+result.stderr
    (log_root/(Path(script).stem+'.log')).write_text(output,encoding='utf-8')
    assert result.returncode==0 and 'Traceback' not in output,output
    print(script,'PASS',round(time.monotonic()-started,2),'s',flush=True)


def build(blender,out_root,rebuild=True):
    out_root=out_root.resolve();logs=out_root/'.work/reports/fighter';logs.mkdir(parents=True,exist_ok=True)
    if rebuild:run(blender,'solkael_build.py',['--out-root',out_root],logs)
    source=out_root/'art/characters'/HERO/'source'/f'chr_{HERO}_v001.blend'
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    stage=out_root/'art/characters'/HERO/'exports'/f'chr_{HERO}_v001.glb'
    run(blender,'solkael_export.py',['--source',source,'--output',stage],logs)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash,'Exporter changed editable source'
    metrics=validate(stage)
    runtime=out_root/'game/assets/characters'/HERO/stage.name
    runtime.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(stage,runtime)
    source_meta=json.loads((out_root/'art/characters'/HERO/'solkael_asset.json').read_text())
    meta={k:source_meta[k] for k in ('hero_id','art_lock','clips','expressions')};meta['metrics']=metrics
    (runtime.parent/'fighter_presentation.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8',newline='\n')
    report=dict(status='pass',metrics=metrics,source_sha256=source_hash,export_does_not_mutate_source=True,source_rebuilt=rebuild,source=source.relative_to(out_root).as_posix(),runtime=runtime.relative_to(out_root).as_posix())
    (logs/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--blender',required=True);p.add_argument('--out-root',type=Path,default=ROOT);p.add_argument('--export-existing',action='store_true')
    a=p.parse_args();build(a.blender,a.out_root,not a.export_existing)
