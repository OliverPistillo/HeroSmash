"""Independent, dependency-free GLB inspection for the first production fighter."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import re
import struct


class GLB:
    def __init__(self,path):
        self.raw=Path(path).read_bytes()
        assert len(self.raw)>=20 and self.raw[:4]==b'glTF','Not a hydrated GLB'
        magic,version,length=struct.unpack_from('<4sII',self.raw)
        assert version==2 and length==len(self.raw)
        chunks={};offset=12
        while offset<length:
            size,kind=struct.unpack_from('<II',self.raw,offset)
            assert size%4==0 and offset+8+size<=length and kind not in chunks
            chunks[kind]=self.raw[offset+8:offset+8+size];offset+=8+size
        assert offset==length and set(chunks)=={0x4e4f534a,0x004e4942}
        self.doc=json.loads(chunks[0x4e4f534a]);self.binary=chunks[0x004e4942]
        assert self.doc['asset']['version']=='2.0'
        assert len(self.doc['buffers'])==1 and 'uri' not in self.doc['buffers'][0]
        assert self.doc['buffers'][0]['byteLength']<=len(self.binary)
        for view in self.doc['bufferViews']:
            assert view.get('buffer',0)==0 and view.get('byteOffset',0)>=0
            assert view.get('byteOffset',0)+view['byteLength']<=len(self.binary)
        for i in range(len(self.doc['accessors'])):self.values(i)

    def values(self,index):
        a=self.doc['accessors'][index]
        fmt='<'+{5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
        size=struct.calcsize(fmt)
        assert a['count']>0
        if 'bufferView' in a:
            v=self.doc['bufferViews'][a['bufferView']];stride=v.get('byteStride',size);off=a.get('byteOffset',0)
            assert stride>=size and off>=0 and off+(a['count']-1)*stride+size<=v['byteLength']
            result=[struct.unpack_from(fmt,self.binary,v.get('byteOffset',0)+off+i*stride) for i in range(a['count'])]
        else:
            assert 'sparse' in a
            result=[struct.unpack(fmt,bytes(size))]*a['count']
        if 'sparse' in a:
            sparse=a['sparse'];assert 0<sparse['count']<=a['count']
            def span(part,width):
                view=self.doc['bufferViews'][part['bufferView']];off=part.get('byteOffset',0)
                assert off>=0 and off+sparse['count']*width<=view['byteLength']
                return view.get('byteOffset',0)+off
            idx_fmt='<'+{5121:'B',5123:'H',5125:'I'}[sparse['indices']['componentType']]
            width=struct.calcsize(idx_fmt);start=span(sparse['indices'],width);values=span(sparse['values'],size)
            previous=-1
            for n in range(sparse['count']):
                idx=struct.unpack_from(idx_fmt,self.binary,start+n*width)[0]
                assert previous<idx<a['count'];previous=idx
                result[idx]=struct.unpack_from(fmt,self.binary,values+n*size)
        assert all(math.isfinite(x) for row in result for x in row),'Nonfinite accessor'
        return result


def validate(path, fixture=False):
    glb=GLB(path);d=glb.doc
    assert not d.get('cameras') and not d.get('lights')
    assert not d.get('images') and not d.get('textures'),'First fighter scalar-PBR policy; no hidden image source'
    assert len(d['skins'])==1 and len(d['meshes'])==1
    names=[n.get('name','') for n in d['nodes']]
    assert len(names)==len(set(names)), 'Duplicate node/bone names'
    assert 'HeroSkeleton' in names and 'root' in names
    skin=d['skins'][0];joints=skin['joints'];assert len(joints)==len(set(joints))
    assert len(glb.values(skin['inverseBindMatrices']))==len(joints)
    assert all(re.fullmatch('[a-z][a-z0-9_]*',names[j]) for j in joints)
    for n in d['nodes']:assert all(abs(s-1)<1e-5 for s in n.get('scale',[1,1,1])),'Nonidentity scale'
    for m in d['materials']:
        assert re.fullmatch('mat_[a-z0-9_]+',m['name'])
        assert m.get('alphaMode','OPAQUE')=='OPAQUE'
    positions=[];triangles=0
    for p in d['meshes'][0]['primitives']:
        assert p.get('mode',4)==4 and 0<=p['material']<len(d['materials'])
        a=p['attributes'];assert {'POSITION','NORMAL','JOINTS_0','WEIGHTS_0'}<=a.keys()
        pos=glb.values(a['POSITION']);positions.extend(pos)
        indices=glb.values(p['indices']);assert len(indices)%3==0 and all(0<=i[0]<len(pos) for i in indices)
        triangles+=len(indices)//3
        weights=glb.values(a['WEIGHTS_0']);js=glb.values(a['JOINTS_0'])
        assert len(weights)==len(js)==len(pos)
        assert all(abs(sum(w)-1)<1e-5 and all(0<=v<=1 for v in w) for w in weights),'Skin weights'
        assert all(all(0<=v<len(joints) for v in row) for row in js),'Joint index'
        assert all(abs(sum(x*x for x in n)-1)<.001 for n in glb.values(a['NORMAL'])),'Normals'
    bounds=[[min(p[i] for p in positions),max(p[i] for p in positions)] for i in range(3)]
    assert -.005<=bounds[1][0]<=.005,'Y-up floor origin'
    if fixture:
        assert abs(bounds[1][1]-1)<1e-4 and bounds[2][1]>.39,'Axis/scale fixture'
    else:
        assert 1.95<bounds[1][1]<2.25,'Skull/mane scale'
        root=names.index('root')
        clips=d.get('animations',[])
        expected={'idle','intro','attack_light','attack_heavy','skill_cast','hit_react','dodge','ko','victory','idle_breathing'}
        assert {c['name'] for c in clips}==expected and len(clips)==len(expected),'Clip coverage'
        for clip in clips:
            changed=False
            for channel in clip['channels']:
                sampler=clip['samplers'][channel['sampler']]
                times=glb.values(sampler['input']);vals=glb.values(sampler['output'])
                assert all(t[0]>=0 for t in times) and all(a[0]<b[0] for a,b in zip(times,times[1:]))
                assert all(abs(t[0]*30-round(t[0]*30))<.0001 for t in times),'30 FPS grid'
                assert channel['target']['path'] in {'rotation','translation','scale','weights'}
                if channel['target']['node']==root:assert all(all(abs(x-y)<1e-6 for x,y in zip(v,vals[0])) for v in vals),'Root motion'
                if len(set(vals))>1:changed=True
                if clip['name'] in {'idle','idle_breathing'}:assert all(abs(x-y)<1e-5 for x,y in zip(vals[0],vals[-1])),'Loop discontinuity'
            assert changed,'Empty pose animation'
        morphs=d['meshes'][0].get('extras',{}).get('targetNames',[])
        assert len(morphs)==9 and set(morphs)=={'expr_'+n for n in ['focused','aggressive','casting','pain_light','pain_heavy','stunned','victory','defeat','ko']}
        assert all(w==0 for w in d['meshes'][0].get('weights',[])), 'Export must start with neutral face'
        for p in d['meshes'][0]['primitives']:
            assert len(p['targets'])==9
            for target in p['targets']:
                assert all(sum(x*x for x in v)<.05**2 for v in glb.values(target['POSITION'])),'Excessive morph displacement'
    return dict(status='pass',sha256=hashlib.sha256(glb.raw).hexdigest(),bytes=len(glb.raw),triangles=triangles,vertices_exported=len(positions),materials=len(d['materials']),meshes=len(d['meshes']),surfaces=len(d['meshes'][0]['primitives']),bones=len(joints),textures=0,texture_bytes=0,morph_targets=0 if fixture else 9,expressions=0 if fixture else 10,clips=[c['name'] for c in d.get('animations',[])],bounds_m=bounds,axis='Godot Y-up, model +Z front',root_motion=False)


if __name__=='__main__':
    import sys
    print(json.dumps(validate(sys.argv[1],fixture='--fixture' in sys.argv),indent=2))
