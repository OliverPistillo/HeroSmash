"""Raw Godot Mobile screenshots, animated timing samples and MJPEG footage."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import hashlib

ROOT=Path(__file__).resolve().parents[2]


def capture(godot,out,project_root=ROOT,movies_only=False):
    out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    results=[]
    def run(name,resolution='844x390',**options):
        env={k:v for k,v in os.environ.items() if not k.startswith('HERO_FIGHTER_')}
        env['HERO_FIGHTER_CAPTURE']=str(out/(name+'.png'))
        for key,value in options.items():env['HERO_FIGHTER_'+key.upper()]=str(value)
        cmd=[godot,'--path',str(project_root/'game'),'--rendering-method','mobile','--resolution',resolution,'--script','res://tests/fighter_review.gd']
        if options.get('video'):cmd+=['--write-movie',str(out/(name+'.avi')),'--fixed-fps','30']
        proc=subprocess.run(cmd,cwd=project_root,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=300)
        text=proc.stdout+proc.stderr
        (out/(name+'.log')).write_text(text,encoding='utf-8')
        assert proc.returncode==0 and 'FIGHTER_REVIEW_PASS' in text and 'SCRIPT ERROR:' not in text and '\nERROR:' not in text,text
        assert 'Forward Mobile' in text and 'Vulkan' in text
        report=json.loads((out/(name+'.json')).read_text(encoding='utf-8'))
        assert report['resolution']==list(map(int,resolution.split('x'))) and not report['adapter_errors']
        results.append(dict(name=name,report=report))
        print('CAPTURE_PASS',name,flush=True)
    if not movies_only:
        for resolution in ['1366x768','844x390']:run('profile-'+resolution,resolution,profile=1,clip='idle')
        for name,clip,pose,yaw in [('front','idle',0,29),('side','idle',0,119),('back','idle',0,209),('light-contact','attack_light',.304,0),('heavy-contact','attack_heavy',.7,0),('bulwark-contact','skill_cast',1,0),('ko','ko',2,0),('victory','victory',1.25,0),('dodge','dodge',.4,0)]:run(name,clip=clip,pose=pose,yaw=yaw)
        for expression in ['neutral','focused','aggressive','casting','pain_light','pain_heavy','stunned','victory','defeat','ko']:run('expression-'+expression,clip='idle',expression=expression,portrait=1)
    # Match the project MovieWriter viewport, avoiding rescaled/cropped UI.
    run('animation-catalog','1366x768',video=1)
    run('resolver-replay','1366x768',video=1,replay=1)
    run('resolver-barrier','1366x768',video=1,replay=1,scenario='04_shield_healing')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=project_root,text=True).strip()
    summary=dict(status='pass',tested_commit=commit,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),captures=results,notes='Raw engine screenshots and movie output. Profile captures use animated poses; movie-mode timings are not performance conclusions.')
    (out/'capture-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--godot',required=True);p.add_argument('--output',type=Path,default=ROOT/'.work/reports/fighter-review')
    p.add_argument('--project-root',type=Path,default=ROOT)
    p.add_argument('--movies-only',action='store_true')
    a=p.parse_args();capture(a.godot,a.output,a.project_root.resolve(),a.movies_only)
