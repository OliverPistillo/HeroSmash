"""Raw v002 engine evidence and reproducible expression-sheet layout."""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser();p.add_argument('--godot',required=True);p.add_argument('--output',type=Path,default=ROOT/'docs/qa/evidence/v1.20');a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);logs=ROOT/'.work/reports/v120/captures';logs.mkdir(parents=True,exist_ok=True)
    def run(name,resolution='844x390',slice_scene=False,**options):
        env={k:v for k,v in os.environ.items() if not k.startswith(('HERO_FIGHTER_','HERO_SLICE_'))}
        env[('HERO_SLICE_' if slice_scene else 'HERO_FIGHTER_')+'CAPTURE']=str(out/(name+'.png'))
        for key,value in options.items():env[('HERO_SLICE_' if slice_scene else 'HERO_FIGHTER_')+key.upper()]=str(value)
        cmd=[a.godot,'--path',str(ROOT/'game'),'--rendering-method','mobile','--resolution',resolution]
        cmd+=['res://scenes/qa/two_fighter_slice.tscn'] if slice_scene else ['--script','res://tests/polish_review.gd']
        proc=subprocess.run(cmd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
        text=proc.stdout+proc.stderr;(logs/(name+'.log')).write_text(text,encoding='utf-8')
        assert proc.returncode==0 and ('SLICE_CAPTURE_PASS' if slice_scene else 'FIGHTER_REVIEW_PASS') in text and 'SCRIPT ERROR:' not in text and '\nERROR:' not in text,text[-4000:]
        print('CAPTURE_PASS',name,flush=True)
    for name,clip,pose,yaw in [('front','idle',0,29),('3quarter','idle',0,0),('side','idle',0,119),('back','idle',0,209),('guard','idle',0,0),('light','attack_light',.304,0),('heavy','attack_heavy',.7,0),('skill','skill_cast',1,0),('hit','hit_react',.20,0),('dodge','dodge',.4,0),('ko','ko',2,0),('victory','victory',1.25,0)]:run(name,clip=clip,pose=pose,yaw=yaw)
    run('face',portrait=1)
    run('gauntlet',detail='gauntlet')
    run('material',detail='material')
    names=['neutral','focused','aggressive','casting','pain_light','pain_heavy','stunned','victory','defeat','ko']
    for expression in names:run('expression-'+expression,portrait=1,expression=expression)
    for res in ('1366x768','844x390','1080x486'):
        run('two-fighter-'+res,res,slice_scene=True,scenario='04_shield_healing')
    # Contact sheet contains only unchanged engine captures plus labels.
    try:
        from PIL import Image,ImageDraw
        sheet=Image.new('RGB',(5*422,2*219),'#101b2c');draw=ImageDraw.Draw(sheet)
        for i,name in enumerate(names):
            source=Image.open(out/('expression-'+name+'.png'));source=source.resize((422,195))
            x=(i%5)*422;y=(i//5)*219;sheet.paste(source,(x,y));draw.text((x+12,y+199),name.upper(),fill='#efd9ae')
        sheet.save(out/'expression-grid.png')
    except ImportError:
        raise RuntimeError('Run with the already detected Pillow interpreter; do not install globally')


if __name__=='__main__':main()
