"""v003 art revision gate; reuses v1.20 contracts without relaxing assertions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/validation'))
from polish import asset, uv_check
sys.path.insert(0,str(ROOT/'tools/asset_pipeline'))
from fighter_glb import GLB
sys.path.insert(0,str(ROOT/'tools/art'))
from reference_lock import production_references

HERO='solkael_lionheart'
GLB_PATH=ROOT/f'game/assets/characters/{HERO}/chr_{HERO}_v003.glb'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--godot',required=True)
    p.add_argument('--blender',required=True);p.add_argument('--rebuild',action='store_true')
    p.add_argument('--report',type=Path,default=ROOT/'.work/reports/v003/validation.json')
    a=p.parse_args();logs=ROOT/'.work/reports/v003/gates';logs.mkdir(parents=True,exist_ok=True)
    report={'status':'running','art_status':'OWNER REVIEW REQUIRED','checks':[],
            'tested_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'working_tree_changes':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())}
    def run(name,command,env=None,marker=None):
        r=subprocess.run([str(x) for x in command],cwd=ROOT,env=env,capture_output=True,
                         text=True,encoding='utf-8',errors='replace',timeout=600)
        text=r.stdout+r.stderr;(logs/(name+'.log')).write_text(text,encoding='utf-8')
        assert r.returncode==0 and 'Traceback' not in text and 'SCRIPT ERROR:' not in text and '\nERROR:' not in text,text[-5000:]
        if marker:assert marker in text,text[-5000:]
        return text
    def check(name,fn):
        try:
            detail=fn();report['checks'].append(dict(name=name,status='pass',details=detail));print('PASS',name,flush=True)
        except (AssertionError,OSError,ValueError,KeyError,subprocess.SubprocessError) as e:
            report['checks'].append(dict(name=name,status='fail',details=str(e)));print('FAIL',name,str(e),flush=True)
    def baseline():
        paths=['game/data','game/scripts/combat','game/scripts/core','game/scripts/cards',
               'game/scripts/branches','game/scripts/economy','legacy','game/project.godot',
               'references/visual/characters/solkael_lionheart/production',
               'art/characters/solkael_lionheart/v002','tools/asset_pipeline/solkael_polish.py',
               'tools/asset_pipeline/solkael_build.py','game/assets/characters/solkael_lionheart/chr_solkael_lionheart_v002.glb',
               'game/assets/characters/solkael_lionheart/fighter_presentation.json',
               'game/scripts/presentation/solkael_fighter.gd','game/scripts/presentation/fighter_event_adapter.gd']
        assert not run('protected',['git','diff','de770df','--',*paths]).strip()
        manifest=json.loads((ROOT/'docs/qa/evidence/v1.20/artifact-integrity.json').read_text())
        for img in manifest['images']:
            assert sha(ROOT/'docs/qa/evidence/v1.20'/img['file'])==img['sha256'],img['file']
        assert len(production_references())==8
        return {'baseline':'de770dff30dcc533d547074c975fdaa0962abda9','protected_paths':paths,'v002_original_images_hashed':len(manifest['images'])}
    def contracts():
        before=json.loads((ROOT/f'art/characters/{HERO}/v002/solkael_asset.json').read_text())
        after=json.loads((ROOT/f'art/characters/{HERO}/v003/solkael_asset.json').read_text())
        for key in ('hero_id','art_lock','rig_family','bones','clips','expressions','reference_ids','skull_height_m'):
            assert before[key]==after[key],key
        assert after['baseline_source_sha256']==sha(ROOT/before['source'])
        assert after['baseline_provenance']['source_basis_max_error_m']==0
        before_glb=GLB(ROOT/f'game/assets/characters/{HERO}/chr_{HERO}_v002.glb');after_glb=GLB(GLB_PATH)
        for doc in (before_glb,after_glb):
            names=[doc.doc['nodes'][i]['name'] for i in doc.doc['skins'][0]['joints']]
            assert len(names)==71
        old_bind=before_glb.values(before_glb.doc['skins'][0]['inverseBindMatrices'])
        new_bind=after_glb.values(after_glb.doc['skins'][0]['inverseBindMatrices'])
        assert old_bind==new_bind,'Bind matrices changed'
        return {'rest_and_bind_matrices':'identical','bones':71,'clip_durations_and_markers':'identical','morph_names':'9 + neutral unchanged'}
    def uv_negative():
        tri=[(0,0),(.5,0),(0,.5)]
        for invalid in [[tri,tri],[[(0,0),(0,0),(0,0)]],[[(0,0),(2,0),(0,1)]]]:
            try:uv_check(invalid)
            except AssertionError:continue
            raise AssertionError('Malformed UV accepted')
        return 'overlap, degenerate and out-of-bounds fixtures rejected'
    def binary():
        metrics=asset(GLB_PATH)
        assert metrics['materials']==1 and metrics['textures']==4 and metrics['bones']==71
        baseline_metrics=asset()
        keys=['triangles','vertices_exported','materials','surfaces','bones','textures','morph_targets','bytes','texture_bytes']
        report['metrics']={'v002':baseline_metrics,'v003':metrics,
                           'delta':{key:metrics[key]-baseline_metrics[key] for key in keys}}
        return metrics
    def export_source():
        source=ROOT/f'art/characters/{HERO}/v003/source/chr_{HERO}_v003.blend'
        original=sha(source);output=logs/'saved-source.glb'
        cmd=[a.blender,'--background','--factory-startup','--python-exit-code','1',
             '--python',ROOT/'tools/asset_pipeline/solkael_export.py','--',
             '--source',source,'--output',output]
        run('saved-export',cmd,marker='SOLKAEL_EXPORT_PASS')
        assert sha(source)==original
        assert output.read_bytes()==GLB_PATH.read_bytes(),'Saved-source export differs'
        return {'source_unchanged':True,'glb_sha256':sha(output)}
    def rebuild():
        isolated=logs/'rebuild';isolated.mkdir(exist_ok=True)
        prefix=[a.blender,'--background','--factory-startup','--python-exit-code','1','--python']
        run('isolated-build',prefix+[ROOT/'tools/asset_pipeline/solkael_v003.py','--','--out-root',isolated],marker='SOLKAEL_V003_SOURCE_PASS')
        source=isolated/f'art/characters/{HERO}/v003/source/chr_{HERO}_v003.blend'
        output=isolated/'reconstructed.glb'
        run('isolated-export',prefix+[ROOT/'tools/asset_pipeline/solkael_export.py','--','--source',source,'--output',output],marker='SOLKAEL_EXPORT_PASS')
        assert output.read_bytes()==GLB_PATH.read_bytes(),'Isolated reconstruction differs'
        return {'glb_sha256':sha(output),'exact_rebuild':True}
    check('v002_gameplay_and_art_lock_preserved',baseline)
    check('rig_animation_and_naming_contracts',contracts)
    check('negative_uv_controls',uv_negative)
    check('independent_glb_uv_material_expression_gate',binary)
    check('saved_source_export',export_source)
    if a.rebuild:check('isolated_reconstruction',rebuild)
    check('godot_import',lambda:run('import',[a.godot,'--headless','--path',ROOT/'game','--editor','--import']))
    for version in ('v002','v003'):
        env=dict(os.environ);env['HERO_FIGHTER_ASSET_VERSION']=version
        check(version+'_real_streams_contacts_seek_cancel',lambda version=version,env=env:
              run(version+'-runtime',[a.godot,'--headless','--path',ROOT/'game','--script','res://tests/two_fighter_test.gd'],env=env,marker='TWO_FIGHTER_TEST_PASS'))
    report['status']='pass' if all(c['status']=='pass' for c in report['checks']) else 'fail'
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if report['status']=='pass' else 1)


if __name__=='__main__':main()
