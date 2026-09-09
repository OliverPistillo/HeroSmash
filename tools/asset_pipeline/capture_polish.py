"""Raw v002 engine evidence and reproducible expression-sheet layout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser();p.add_argument('--godot',required=True);p.add_argument('--output',type=Path,default=ROOT/'docs/qa/evidence/v1.20')
    p.add_argument('--asset-version',choices=['v002','v003'],default='v002')
    p.add_argument('--views',nargs='+',help='Optional subset for iterative art inspection')
    a=p.parse_args()
    if a.asset_version=='v003':
        assert a.output.resolve()!=(ROOT/'docs/qa/evidence/v1.20').resolve(), 'Do not overwrite baseline evidence'
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    logs=ROOT/('.work/reports/v003/captures' if a.asset_version=='v003' else '.work/reports/v120/captures')
    logs.mkdir(parents=True,exist_ok=True)
    def run(name,resolution='844x390',slice_scene=False,**options):
        if a.views and name not in a.views:return
        env={k:v for k,v in os.environ.items() if not k.startswith(('HERO_FIGHTER_','HERO_SLICE_'))}
        env[('HERO_SLICE_' if slice_scene else 'HERO_FIGHTER_')+'CAPTURE']=str(out/(name+'.png'))
        env['HERO_FIGHTER_ASSET_VERSION']=a.asset_version
        for key,value in options.items():env[('HERO_SLICE_' if slice_scene else 'HERO_FIGHTER_')+key.upper()]=str(value)
        cmd=[a.godot,'--path',str(ROOT/'game'),'--rendering-method','mobile','--resolution',resolution]
        scene='two_fighter_slice_v003.tscn' if a.asset_version=='v003' else 'two_fighter_slice.tscn'
        cmd+=['res://scenes/qa/'+scene] if slice_scene else ['--script','res://tests/polish_review.gd']
        proc=subprocess.run(cmd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
        text=proc.stdout+proc.stderr;(logs/(name+'.log')).write_text(text,encoding='utf-8')
        assert proc.returncode==0 and ('SLICE_CAPTURE_PASS' if slice_scene else 'FIGHTER_REVIEW_PASS') in text and 'SCRIPT ERROR:' not in text and '\nERROR:' not in text,text[-4000:]
        if a.asset_version=='v003':
            metadata=out/(name+'.json')
            detail=json.loads(metadata.read_text(encoding='utf-8'))
            asset=ROOT/'game/assets/characters/solkael_lionheart/chr_solkael_lionheart_v003.glb'
            detail.update(asset_version='v003',glb_sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),capture_options=options)
            metadata.write_text(json.dumps(detail,indent=2)+'\n',encoding='utf-8')
        print('CAPTURE_PASS',name,flush=True)
    for name,clip,pose,yaw in [('front','idle',0,29),('3quarter','idle',0,0),('side','idle',0,119),('back','idle',0,209),('guard','idle',0,0),('light','attack_light',.304,0),('heavy','attack_heavy',.7,0),('skill','skill_cast',1,0),('hit','hit_react',.20,0),('dodge','dodge',.4,0),('ko','ko',2,0),('victory','victory',1.25,0)]:run(name,clip=clip,pose=pose,yaw=yaw)
    run('face',portrait=1)
    run('gauntlet',detail='gauntlet')
    run('material',detail='material')
    names=['neutral','focused','aggressive','casting','pain_light','pain_heavy','stunned','victory','defeat','ko']
    for expression in names:run('expression-'+expression,portrait=1,expression=expression)
    for res in ('1366x768','844x390','1080x486'):
        run('two-fighter-'+res,res,slice_scene=True,scenario='04_shield_healing',hold_barrier=1,profile_seconds=4)
    run('desktop-profile',slice_scene=True,profile_seconds=60)
    # Contact sheet contains only unchanged engine captures plus labels.
    if a.views and not all((out/('expression-'+n+'.png')).is_file() for n in names):return
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
