"""Independent v1.20 binary, UV, provenance and unchanged-baseline gate."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/asset_pipeline'))
from fighter_glb import GLB,validate


def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))*.5


def intersection(subject,clip):
    if cross(*clip)<0:clip=list(reversed(clip))
    result=list(subject)
    for a,b in zip(clip,clip[1:]+clip[:1]):
        old=result;result=[]
        if not old:break
        for p,q in zip(old,old[1:]+old[:1]):
            cp,cq=cross(a,b,p),cross(a,b,q)
            if cp>=0:result.append(p)
            if (cp>=0)!=(cq>=0):
                t=cp/(cp-cq);result.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return area(result) if len(result)>=3 else 0


def uv_check(triangles):
    bins=defaultdict(list);overlaps=[];total=0;degenerate=0
    for index,tri in enumerate(triangles):
        assert all(0<=x<=1 for p in tri for x in p),'UV outside atlas'
        size=area(tri);total+=size
        if size<1e-14:degenerate+=1;continue
        low=[int(min(p[k] for p in tri)*128) for k in (0,1)]
        high=[int(max(p[k] for p in tri)*128) for k in (0,1)]
        cells=[(x,y) for x in range(low[0],high[0]+1) for y in range(low[1],high[1]+1)]
        candidates={other for cell in cells for other in bins[cell]}
        for other in candidates:
            overlap=intersection(tri,triangles[other])
            if overlap>1e-10:overlaps.append((index,other,overlap))
        for cell in cells:bins[cell].append(index)
    assert not overlaps,f'Accidental UV overlap: {overlaps[:6]}'
    assert not degenerate,f'Degenerate UV triangles: {degenerate}'
    return dict(triangles=len(triangles),overlaps=0,degenerate=0,coverage_percent=total*100,method='128-cell broadphase + exact convex triangle clipping; shared edges excluded at 1e-10 UV area')


def asset():
    path=ROOT/'game/assets/characters/solkael_lionheart/chr_solkael_lionheart_v002.glb'
    metrics=validate(path,textured=True);glb=GLB(path);d=glb.doc
    assert metrics['materials']==1 and metrics['textures']==4
    material=d['materials'][0];pbr=material['pbrMetallicRoughness']
    for part in ('baseColorTexture','metallicRoughnessTexture'):assert part in pbr
    assert 'normalTexture' in material and 'emissiveTexture' in material
    textures=[]
    for item in d['images']:
        view=d['bufferViews'][item['bufferView']];raw=glb.binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
        assert raw[:8]==b'\x89PNG\r\n\x1a\n'
        width,height=struct.unpack_from('>II',raw,16);assert (width,height)==(2048,2048)
        textures.append(dict(name=item.get('name'),width=width,height=height,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    triangles=[]
    for primitive in d['meshes'][0]['primitives']:
        uv=glb.values(primitive['attributes']['TEXCOORD_0']);indices=[v[0] for v in glb.values(primitive['indices'])]
        triangles.extend([uv[indices[i+k]] for k in range(3)] for i in range(0,len(indices),3))
    metrics['production_uv']=uv_check(triangles);metrics['texture_details']=textures
    metrics['rgba8_mip_estimate_bytes']=4*2048*2048*4*4//3
    return metrics


def command(args):
    result=subprocess.run([str(x) for x in args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR:' not in output and '\nERROR:' not in output,output[-5000:]
    return output


def main():
    p=argparse.ArgumentParser();p.add_argument('--godot',required=True);p.add_argument('--report',type=Path,default=ROOT/'.work/reports/v120/polish-validation.json');a=p.parse_args()
    report=dict(checks=[],tested_commit=command(['git','rev-parse','HEAD']).strip())
    def check(name,fn):
        try:detail=fn();report['checks'].append(dict(name=name,status='pass',details=detail));print('PASS',name,flush=True)
        except (AssertionError,OSError,ValueError,KeyError) as e:report['checks'].append(dict(name=name,status='fail',details=str(e)));print('FAIL',name,str(e),flush=True)
    def protected():
        paths=['game/data','game/scripts/combat','game/scripts/core','game/scripts/cards','game/scripts/branches','game/scripts/economy','legacy/web-prototype','game/project.godot','references/visual/characters/solkael_lionheart/production','art/characters/solkael_lionheart/source','art/characters/solkael_lionheart/solkael_asset.json','game/assets/characters/solkael_lionheart/chr_solkael_lionheart_v001.glb','tools/asset_pipeline/solkael_build.py']
        assert not command(['git','diff','f03a1b3','--',*paths]).strip()
        return dict(baseline='f03a1b3',protected_paths=paths)
    def negative_uv():
        tri=[(0,0),(.5,0),(0,.5)]
        assert uv_check([tri,[(.5,0),(.5,.5),(0,.5)]])['overlaps']==0
        for bad in [[tri,tri],[[(0,0),(0,0),(0,0)]],[[(0,0),(2,0),(0,1)]]]:
            try:uv_check(bad)
            except AssertionError:continue
            raise AssertionError('UV malformed fixture accepted')
        return 'Shared edges pass; overlap, degeneracy and OOB fail'
    check('v119_baseline_preserved',protected)
    check('uv_negative_controls',negative_uv)
    check('asset_uv_material_rig_expression_animation',asset)
    check('godot_import',lambda:command([a.godot,'--headless','--path',ROOT/'game','--editor','--import']))
    check('two_fighter_real_streams_speeds_seek_cancel_contacts',lambda:command([a.godot,'--headless','--path',ROOT/'game','--script','res://tests/two_fighter_test.gd']))
    report['status']='pass' if all(c['status']=='pass' for c in report['checks']) else 'fail'
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if report['status']=='pass' else 1)


if __name__=='__main__':main()
