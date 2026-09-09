"""Package actual engine captures and exact-pixel v002/v003 comparisons."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/qa/evidence/v1.20/v003'
MAPPING=[('01_front','front'),('02_3quarter','3quarter'),('03_side','side'),
         ('04_back','back'),('05_face_closeup','face'),('06_gauntlets_closeup','gauntlet'),
         ('07_materials_closeup','material'),('08_expressions','expression-grid'),
         ('09_guard','guard'),('10_light_punch','light'),('11_heavy_punch','heavy'),
         ('12_skill_barrier','skill'),('13_hit','hit'),('14_dodge','dodge'),
         ('15_ko','ko'),('16_victory','victory'),
         ('17_two_fighter_1366x768','two-fighter-1366x768'),
         ('18_two_fighter_844x390','two-fighter-844x390')]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')


def make_zip(path,files):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,source in sorted(files.items()):z.write(source,name)
    with zipfile.ZipFile(path) as z:
        assert set(z.namelist())==set(files) and len(z.infolist())==len(files)
        assert z.testzip() is None
        for name,source in files.items():assert z.read(name)==source.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),files=len(files),bytes=path.stat().st_size,sha256=sha(path))


def main():
    owner=OUT/'owner-review';comparison=OUT/'comparison'
    owner.mkdir(parents=True,exist_ok=True);comparison.mkdir(parents=True,exist_ok=True)
    glb=ROOT/'game/assets/characters/solkael_lionheart/chr_solkael_lionheart_v003.glb'
    glb_hash=sha(glb)
    baseline=json.loads((OUT.parent/'artifact-integrity.json').read_text())
    old_hash={i['file']:i['sha256'] for i in baseline['images']}
    records=[]
    font=ImageFont.load_default(size=20)
    for numbered,original in MAPPING:
        before=OUT.parent/(original+'.png');after=OUT/(original+'.png')
        assert sha(before)==old_hash[before.name]
        if original!='expression-grid':
            meta=json.loads(after.with_suffix('.json').read_text())
            assert meta['asset_version']=='v003' and meta['glb_sha256']==glb_hash
        with Image.open(before) as b,Image.open(after) as a:
            b.load();a.load();assert b.size==a.size
            width,height=a.size
            sheet=Image.new('RGB',(width*2,height+40),'#101b2c')
            sheet.paste(b,(0,40));sheet.paste(a,(width,40))
            draw=ImageDraw.Draw(sheet)
            draw.text((16,9),'v002 / BEFORE',font=font,fill='#efd9ae')
            draw.text((width+16,9),'v003 / OWNER REVIEW REQUIRED',font=font,fill='#efd9ae')
            sheet.save(comparison/(numbered+'.png'))
            # Pixel checks prove the comparison does not retouch either render.
            assert sheet.crop((0,40,width,height+40)).tobytes()==b.convert('RGB').tobytes()
            assert sheet.crop((width,40,width*2,height+40)).tobytes()==a.convert('RGB').tobytes()
        shutil.copy2(after,owner/(numbered+'.png'))
        assert sha(owner/(numbered+'.png'))==sha(after)
        records.append(dict(file=numbered+'.png',source=original+'.png',resolution=[width,height],
                            before_sha256=sha(before),after_sha256=sha(after),
                            comparison_sha256=sha(comparison/(numbered+'.png'))))
    gate=json.loads((OUT/'validation.json').read_text())
    assert gate['status']=='pass' and gate['metrics']['v003']['sha256']==glb_hash
    metrics=gate['metrics']
    profile=json.loads((OUT/'desktop-profile.json').read_text())
    samples=[s for s in profile['samples'] if s['elapsed_s']>=5]
    def summary(key):
        values=sorted(float(s[key]) for s in samples)
        return dict(p50=values[len(values)//2],p95=values[min(len(values)-1,int(len(values)*.95))])
    metrics.update(art_status='OWNER REVIEW REQUIRED',physical_device='BLOCKED: no authorized physical phone connected',
                   desktop=dict(adapter='RX7900XT / i5-13600K',renderer='Godot 4.7.2 Mobile/Vulkan',
                                resolution=[844,390],duration_s=profile['samples'][-1]['elapsed_s'],
                                warmup_excluded_s=5,samples=len(samples),
                                metrics={k:summary(k) for k in ('fps','process_ms','render_cpu_ms','render_gpu_ms','draw_calls','primitives','texture_bytes')}))
    save(OUT/'metrics.json',metrics)
    rows=['# Solkael v002 / v003 — before and after','',
          'Status: **OWNER REVIEW REQUIRED**. Sinistra: v002; destra: v003.',
          'Le coppie conservano tutti i pixel dei render originali e la stessa risoluzione,',
          'camera, luce e fotogramma contrattuale. Solo la fascia superiore con le etichette',
          'è aggiunta. Le pose modificate fanno parte del polish. Nessuna immagine è ritoccata.',
          'Il timing del fermo barriera nella scena replay dipende dal frame di presentazione;',
          'gli screenshot confrontano lo stesso scenario/evento, non un tempo sub-frame garantito.','',
          '| Metrica | v002 | v003 | Delta |','| --- | ---: | ---: | ---: |']
    for key,label in [('triangles','Triangles'),('vertices_exported','Export vertices'),('materials','Materials'),
                      ('surfaces','Surfaces'),('textures','Textures'),('bones','Bones'),('morph_targets','Blend shapes'),('bytes','GLB bytes')]:
        rows.append(f"| {label} | {metrics['v002'][key]} | {metrics['v003'][key]} | {metrics['delta'][key]:+d} |")
    rows+=['','Quattro mappe da 2048 × 2048; dieci espressioni contando neutral e nove morph.',
           'Le dieci clip mantengono nomi, durata, marker e 30 fps. Rest e bind matrix identiche.',
           'Le metriche desktop non certificano prestazioni Android/iOS.','']
    for numbered,_ in MAPPING:rows += [f'![{numbered}]({numbered}.png)','']
    (comparison/'BEFORE_AFTER.md').write_text('\n'.join(rows),encoding='utf-8')
    shutil.copy2(OUT/'REVIEW.md',owner/'OWNER_REVIEW.md')
    expected={numbered+'.png' for numbered,_ in MAPPING}|{'OWNER_REVIEW.md'}
    assert {p.name for p in owner.iterdir()}==expected
    integrity=dict(art_status='OWNER REVIEW REQUIRED',glb_sha256=glb_hash,
                   source_blend_sha256=sha(ROOT/'art/characters/solkael_lionheart/v003/source/chr_solkael_lionheart_v003.blend'),
                   recipe_sha256=sha(ROOT/'tools/asset_pipeline/solkael_v003.py'),images=records,
                   comparisons='unmodified source pixels, labelled canvas only')
    save(OUT/'artifact-integrity.json',integrity)
    packages=ROOT/'.work/review-packages';packages.mkdir(parents=True,exist_ok=True)
    owner_zip=make_zip(packages/'Solkael_v003_OWNER_REVIEW.zip',{p.name:p for p in owner.iterdir()})
    files={'owner-review/'+p.name:p for p in owner.iterdir()}
    files.update({'comparison/'+p.name:p for p in comparison.iterdir()})
    for name in ('metrics.json','validation.json','artifact-integrity.json','CHANGES.md'):
        files[name]=OUT/name
    for name in ('android-export.json','device.json','movie-validation.json','roster-validation.json','fresh-checkout.json'):
        if (OUT/name).is_file():files[name]=OUT/name
    if (OUT/'animation-set.avi').is_file():files['animation-set.avi']=OUT/'animation-set.avi'
    bundle=make_zip(packages/'Solkael_v003_REVIEW_BUNDLE.zip',files)
    save(ROOT/'.work/reports/v003/packages.json',{'owner':owner_zip,'bundle':bundle})
    print(json.dumps({'owner':owner_zip,'bundle':bundle},indent=2))


if __name__=='__main__':main()
