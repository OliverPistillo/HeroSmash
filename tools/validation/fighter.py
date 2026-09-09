"""v1.19 asset admission, LFS hydration, reconstruction and real Godot checks."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/asset_pipeline'))
sys.path.insert(0,str(ROOT/'tools/art'))
from fighter_glb import validate
from reference_lock import production_references
from build_fighter import build


def command(args,timeout=180):
    run=subprocess.run(list(map(str,args)),cwd=ROOT,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=timeout)
    output=run.stdout+run.stderr
    assert run.returncode==0 and 'SCRIPT ERROR:' not in output and '\nERROR:' not in output,output
    return output


def main():
    p=argparse.ArgumentParser();p.add_argument('--godot',required=True);p.add_argument('--blender');p.add_argument('--require-clean',action='store_true');p.add_argument('--expected-branch');p.add_argument('--report',type=Path,default=ROOT/'.work/reports/fighter/gates.json')
    args=p.parse_args();args.report.parent.mkdir(parents=True,exist_ok=True)
    result=dict(tested_commit=command(['git','rev-parse','HEAD']).strip(),branch=command(['git','branch','--show-current']).strip(),checks=[],limitations=[])
    def check(name,fn):
        try:details=fn();result['checks'].append(dict(name=name,status='pass',details=details));print('PASS '+name,flush=True)
        except Exception as error:result['checks'].append(dict(name=name,status='fail',details=str(error)));print('FAIL '+name+' '+str(error),flush=True)
    def baseline():
        if args.expected_branch:assert result['branch']==args.expected_branch
        assert command(['git','rev-parse','v1.18-hero-reference-lock^{commit}']).strip()=='d5ece76e09b175e7b75d12b2d0dd4f58b6d926b9'
        command(['git','merge-base','--is-ancestor','d5ece76','HEAD'])
        old=json.loads(command(['git','show','d5ece76:docs/references/visual/reference_manifest.json']))
        now=json.loads((ROOT/'docs/references/visual/reference_manifest.json').read_text(encoding='utf-8'))
        assert old['items']==now['items'],'Legacy rights/reference data changed'
        protected=['game/data','game/scripts/combat','game/scripts/core','game/scripts/cards','game/scripts/branches','game/scripts/economy','legacy/web-prototype','game/project.godot']
        assert not command(['git','diff','d5ece76','--',*protected]).strip()
        if args.require_clean:assert not command(['git','status','--porcelain']).strip()
        return dict(baseline='d5ece76',legacy_items_unchanged=len(old['items']),gameplay_changes=0)
    check('baseline_and_protected_data',baseline)
    check('approved_packet_hashes_rights',lambda:dict(images=len(production_references())))
    hero='solkael_lionheart';asset=ROOT/'art/characters'/hero
    runtime=ROOT/'game/assets/characters'/hero
    glb=runtime/f'chr_{hero}_v001.glb';source=asset/'source'/f'chr_{hero}_v001.blend'
    def lfs():
        paths=[*production_references(),source.relative_to(ROOT).as_posix(),glb.relative_to(ROOT).as_posix()]
        for path in paths:
            blob=command(['git','show','HEAD:'+path])
            raw=(ROOT/path).read_bytes()
            assert blob.startswith('version https://git-lfs.github.com/spec/v1\n'),path
            assert 'oid sha256:'+hashlib.sha256(raw).hexdigest() in blob and 'size '+str(len(raw)) in blob,path
        command(['git','lfs','fsck'])
        return dict(hydrated_binaries=len(paths),bytes=sum((ROOT/p).stat().st_size for p in paths))
    check('lfs_hydration_and_integrity',lfs)
    check('glb_skin_materials_morphs_clips',lambda:validate(glb))
    def metadata():
        src=json.loads((asset/'solkael_asset.json').read_text(encoding='utf-8'));game=json.loads((runtime/'fighter_presentation.json').read_text(encoding='utf-8'))
        assert game['metrics']==validate(glb)
        for key in ['hero_id','art_lock','clips','expressions']:assert src[key]==game[key]
        contract=json.loads((ROOT/'docs/art/animation_contract.json').read_text(encoding='utf-8'))
        for clip in src['clips']:
            expected=next(c for c in contract['clips'] if c['name']==clip['name'])
            assert clip['loop']==expected['loop'] and clip['fps']==30 and not clip['root_motion']
            markers={m['name']:m['phase'] for m in clip['markers']}
            assert set(expected['required_markers'])<=set(markers)<=set(contract['marker_vocabulary'])
            assert all(0<=v<=1 for v in markers.values())
        return dict(clips=len(src['clips']),expressions=len(src['expressions']),bones=len(src['bones']))
    check('source_runtime_contract_consistency',metadata)
    check('negative_binary_regressions',lambda:command([sys.executable,'-X','utf8',ROOT/'tools/validation/fighter_negative_test.py']))
    if args.blender:
        def reconstruct():
            location=Path(tempfile.mkdtemp(prefix='fighter-clean-rebuild-',dir=ROOT/'.work'))
            rebuilt=build(args.blender,location,True)
            assert (location/glb.relative_to(ROOT)).read_bytes()==glb.read_bytes(),'GLB rebuild bytes differ'
            assert (location/asset.relative_to(ROOT)/'solkael_asset.json').read_bytes()==(asset/'solkael_asset.json').read_bytes()
            # Export the committed editable source too; the recipe cannot hide a stale .blend.
            from build_fighter import run
            output=location/'export-from-committed-source.glb'
            before=hashlib.sha256(source.read_bytes()).hexdigest()
            run(args.blender,'solkael_export.py',['--source',source,'--output',output],args.report.parent)
            assert output.read_bytes()==glb.read_bytes() and hashlib.sha256(source.read_bytes()).hexdigest()==before
            return dict(glb_sha256=rebuilt['metrics']['sha256'],rebuilt_source_semantics='same exported GLB and source manifest; .blend file bytes contain save/path metadata and are not deterministic',committed_source_export_identical=True)
        check('clean_reconstruction_and_saved_source_export',reconstruct)
    else:result['limitations'].append('Blender reconstruction not requested; portable profile only')
    check('godot_import',lambda:command([args.godot,'--headless','--path',ROOT/'game','--editor','--import']))
    check('godot_wrapper_event_replay_tests',lambda:command([args.godot,'--headless','--path',ROOT/'game','--script','res://tests/fighter_test.gd']))
    def clean():
        dirty=command(['git','status','--porcelain']).strip()
        if args.require_clean:assert not dirty,dirty
        return dict(clean=not bool(dirty))
    check('clean_after',clean)
    result['limitations']+=['Desktop/headless asset checks do not establish physical Android/iOS performance or signing.','Visual review, movie and prior full profiles are separately required for phase closure.']
    result['status']='pass' if all(c['status']=='pass' for c in result['checks']) else 'fail'
    args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(result['status'].upper(),args.report)
    raise SystemExit(0 if result['status']=='pass' else 1)


if __name__=='__main__':main()
