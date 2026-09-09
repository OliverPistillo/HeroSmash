"""Summarize measured exported costs and desktop samples without phone inference."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/validation'))
from polish import asset


def main():
    out=ROOT/'docs/qa/evidence/v1.20'
    metrics=asset()
    profile=json.loads((out/'desktop-profile.json').read_text())
    samples=[s for s in profile['samples'] if s['elapsed_s']>=5]
    def summary(key):
        values=sorted(float(s[key]) for s in samples)
        return dict(min=values[0],p50=values[len(values)//2],p95=values[min(len(values)-1,int(len(values)*.95))],max=values[-1])
    report=dict(asset=metrics,desktop=dict(source='RX7900XT / i5-13600K, Vulkan Mobile, 844x390; not physical Android',duration_s=profile['samples'][-1]['elapsed_s'],warmup_excluded_s=5,samples=len(samples),metrics={key:summary(key) for key in ['fps','process_ms','render_cpu_ms','render_gpu_ms','memory_bytes','draw_calls','primitives','texture_bytes']}),two_fighter_measured=dict(base_triangles=metrics['triangles']*2,material_surfaces=2,shared_material_resources=1,bone_instances=metrics['bones']*2,morph_channels_per_fighter=9,shared_texture_images=4,transparent_surfaces=0,shadow_casting_directional_lights=1,vfx_live_cap=12),proposed=dict(character_triangles=30000,materials_per_fighter=1,texture_sets='one shared4x2048² atlas for this mirrored QA pair',bones_per_fighter=75,morphs_per_fighter=9,vfx_live_cap=12,shadow_lights=1,arena_headroom='UNDETERMINED until physical sustained frame/memory/thermal measurements',status='PROPOSED engineering envelope, not approved mobile budget'),physical_device='BLOCKED: no authorized phone',art_status='REQUIRES OWNER REVIEW; NOT FINAL ART APPROVED')
    (out/'metrics.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    files=[p for p in out.iterdir() if p.suffix=='.png']
    integrity=dict(glb_sha256=metrics['sha256'],source_blend_sha256=hashlib.sha256((ROOT/'art/characters/solkael_lionheart/v002/source/chr_solkael_lionheart_v002.blend').read_bytes()).hexdigest(),art_recipe_sha256=hashlib.sha256((ROOT/'tools/asset_pipeline/solkael_polish.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest(),images=[dict(file=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(files)])
    (out/'artifact-integrity.json').write_text(json.dumps(integrity,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
