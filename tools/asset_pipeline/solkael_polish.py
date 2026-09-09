"""Versioned v002 art pass; v001 recipe and assets remain immutable.

Run with Blender 5.2 --background --python-exit-code 1 --python this_file.
All surface detail is mathematically authored; reference pixels are never sampled.
"""
import json
import argparse
import math
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
import solkael_build as base
from solkael_export import validate_scene

ROOT = base.ROOT
OUT = ROOT / 'art/characters/solkael_lionheart/v002'


class PolishGeometry(base.Geometry):
    def tuft(self, start, tip, width, mat, bone):
        if bone=='jaw':
            # Beard forms overlapping fur lobes, not a row of exposed white teeth.
            if abs(start[0])<1e-6:
                self.ellipsoid((0,-.186,1.686),(.055,.032,.027),'ivory','jaw','beard',segments=18,rings=8)
            return
        first=len(self.faces)
        super().tuft(start,tip,width,mat,bone)
        self.smooth[first:]=[True]*(len(self.faces)-first)
    def tube(self, points, radii, mat, bone, region='', sides=10):
        if region=='tooth':
            s=1 if points[0][0]>0 else -1
            points=[(s*.04,-.222,1.737),(s*.036,-.232,1.716)]
        super().tube(points,radii,mat,bone,region,sides)
    def loft(self, rings, axis, mat, bone, region=''):
        """Continuous quad rings, closed caps, deterministic anatomical profile."""
        vertices=[]; count=24
        for center, radius_a, radius_b in rings:
            for i in range(count):
                a=math.tau*i/count
                offset=(0, radius_a*math.cos(a), radius_b*math.sin(a)) if axis==0 else (radius_a*math.cos(a),radius_b*math.sin(a),0)
                vertices.append(tuple(center[k]+offset[k] for k in range(3)))
        faces=[tuple(reversed(range(count)))]
        for r in range(len(rings)-1):
            for i in range(count):
                a=r*count+i; b=r*count+(i+1)%count
                faces.append((a,b,b+count,a+count))
        faces.append(tuple((len(rings)-1)*count+i for i in range(count)))
        if axis==0 and rings[-1][0][0]<rings[0][0][0]:faces=[tuple(reversed(f)) for f in faces]
        self.add(vertices,faces,mat,bone,region,True)

    def ellipsoid(self, center, radii, mat, bone, region='', segments=16, rings=10):
        if region.startswith('eye_socket_'):radii=(.037,.014,.020)
        if region.startswith('eye_') and not region.startswith('eye_socket_'):
            radii=(radii[0]*.90,radii[1],radii[2]*.72)
        if region.startswith('brow_'):mat='fur';radii=(.045,.025,.021)
        if center==(0,0,1.19):
            self.loft([((0,0,z),x,y) for z,x,y in [(.94,.23,.13),(1.02,.25,.15),(1.13,.245,.14),(1.24,.27,.15),(1.36,.32,.165),(1.46,.345,.17),(1.54,.29,.14)]],2,mat,bone,'torso')
            return
        if center==(0,0,1.4): return
        if mat=='fur' and abs(center[0])==.38:
            s=1 if center[0]>0 else -1
            self.loft([((s*x,0,1.5),y,z) for x,y,z in [(.29,.11,.12),(.34,.15,.15),(.40,.157,.158),(.47,.14,.145),(.54,.115,.126),(.60,.095,.10),(.68,.078,.079)]],0,mat,bone)
            return
        if mat=='fur' and abs(center[0])==.53:return
        if region=='face':
            # Longer nasal bridge and cheek transition; flattened forehead.
            self.loft([((0,y,z),x,d) for z,x,y,d in [(1.70,.080,-.084,.073),(1.75,.130,-.080,.10),(1.80,.146,-.082,.121),(1.85,.140,-.064,.107),(1.90,.113,-.033,.09),(1.945,.065,-.012,.057)]],2,mat,bone,region)
            return
        if region.startswith('muzzle_'):
            center=(center[0]*.91,center[1]-.012,center[2]+.009);radii=(.049,.048,.031)
        if region=='jaw':
            center=(0,-.204,1.706);radii=(.064,.047,.028)
        if region=='mouth':
            # A deep dark oral volume stays attached to the head, behind moving lips.
            center=(0,-.192,1.715);radii=(.057,.045,.038);bone='head';region='oral_cavity'
        super().ellipsoid(center,radii,mat,bone,region,segments,rings)


def geometry():
    original=base.Geometry
    try:
        base.Geometry=PolishGeometry
        g=base.body_geometry()
    finally:base.Geometry=original
    # Mouth is a continuous interior volume with separate lower dentition/tongue.
    g.regions['mouth']=[]
    g.ellipsoid((0,-.175,1.800),(.047,.045,.061),'fur','head','nose_bridge',segments=20,rings=12)
    g.ellipsoid((0,-.226,1.702),(.034,.021,.006),'mane_light','jaw','tongue',segments=16,rings=5)
    for s in (-1,1):
        for k in range(3):
            x=s*(.011+k*.011)
            g.ellipsoid((x,-.220,1.737),(.005,.008,.006),'ivory','head','upper_teeth',segments=8,rings=5)
            g.ellipsoid((x,-.220,1.724),(.005,.007,.004),'ivory','jaw','lower_teeth',segments=8,rings=5)
        # Actual eyelid arcs cover intact eyeballs, instead of crushing their volume.
        side='l' if s>0 else 'r'
        for upper in (True,False):
            points=[]
            for k in range(13):
                a=math.pi*k/12
                points.append((s*.06+.032*math.cos(a),-.218,1.835+(.018 if upper else -.018)*math.sin(a)))
            g.tube(points,[.004]*13,'fur','head',('upper_lid_' if upper else 'lower_lid_')+side,sides=6)
            fixed_z=1.865 if upper else 1.808
            vertices=[(x,y-.003,z) for x,y,z in points]+[(x,y-.003,fixed_z) for x,y,z in points]
            faces=[(k,k+1,k+14,k+13) for k in range(12)]
            if upper:faces=[tuple(reversed(f)) for f in faces]
            g.add(vertices,faces,'fur','head',('upper_lid_surface_' if upper else 'lower_lid_surface_')+side,True)
        # Connected bridge, lip line and muzzle crease.
        g.tube([(s*.012,-.258,1.751),(s*.026,-.258,1.740),(s*.050,-.245,1.735)],[.0025]*3,'glove','head','lip_'+side,sides=6)
        for k in range(8):
            # Back mane layers sweep down the neck, breaking the radial star shape.
            z=1.98-k*.045
            g.tuft((s*.075,.17,z),(s*(.12+.016*k),.22, z-.15),.058,'mane' if k%2 else 'mane_light','head')
        # Forearm functional hardware, not separate shields.
        for x in (.77,1.10):
            for z in (1.40,1.60):
                g.ellipsoid((s*x,-.19,z),(.013,.007,.013),'gold','forearm_'+side,segments=8,rings=5)
        for k in range(4):
            g.tube([(s*1.255,-.05+k*.035,1.50),(s*1.29,-.05+k*.035,1.47)],[.011,.001],'glove',f'{["index","middle","ring","pinky"][k]}_03_'+side,sides=6)
    return g


def facial_and_weights(obj,g):
    if 'spine_02' not in obj.vertex_groups:obj.vertex_groups.new(name='spine_02')
    basis=obj.data.shape_keys.key_blocks[0]
    closes=dict(focused=.5,aggressive=.15,casting=.2,pain_light=.8,pain_heavy=1,stunned=0,victory=.15,defeat=.55,ko=1)
    for key in obj.data.shape_keys.key_blocks[1:]:
        name=key.name.removeprefix('expr_'); close=closes[name]
        jaw_delta=key.data[g.regions['jaw'][0]].co-basis.data[g.regions['jaw'][0]].co
        for region in ('tongue','lower_teeth','beard'):
            for i in g.regions[region]:key.data[i].co+=jaw_delta
        for side in ('l','r'):
            for region in ('eye_','pupil_'):
                for i in g.regions[region+side]:key.data[i].co=basis.data[i].co
            for i in g.regions['upper_lid_'+side]:
                v=key.data[i].co;v.z-=max(0,v.z-1.817)*close
            for i in g.regions['lower_lid_'+side]:
                v=key.data[i].co;v.z+=max(0,1.830-v.z)*close*.35
            for i in g.regions['upper_lid_surface_'+side][:13]:
                v=key.data[i].co;v.z+=(1.824-v.z)*close
            for i in g.regions['lower_lid_surface_'+side][:13]:
                v=key.data[i].co;v.z+=(1.830-v.z)*close
    # Smooth torso bend across continuous rings; armor remains rigid per segment.
    for i in g.regions['torso']:
        z=obj.data.vertices[i].co.z
        for group in obj.vertex_groups:group.remove([i])
        positions=[('pelvis',1.0),('spine_01',1.13),('spine_02',1.29),('spine_03',1.45)]
        weights=[max(0,1-abs(z-h)/.18) for _,h in positions]
        total=sum(weights)
        for (name,_),w in zip(positions,weights):
            if w:obj.vertex_groups[name].add([i],w/total,'REPLACE')


def atlas(obj,palette):
    """Unique area-weighted islands, procedural PBR raster, no source imagery."""
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(72),island_margin=.003,area_weight=1.0,correct_aspect=True,scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh=obj.data;mesh.calc_loop_triangles();size=2048
    maps={name:np.zeros((size,size,4),dtype=np.float32) for name in ['base_color','normal','orm','emissive']}
    for pixels in maps.values():pixels[:,:,3]=1
    maps['normal'][:,:,:3]=(.5,.5,1); maps['orm'][:,:,:3]=(1,.7,0)
    coverage=np.zeros((size,size),dtype=bool)
    uv=mesh.uv_layers.active.data
    for tri in mesh.loop_triangles:
        points=np.array([uv[i].uv[:] for i in tri.loops])*size
        low=np.maximum(np.floor(points.min(axis=0)).astype(int),0);high=np.minimum(np.ceil(points.max(axis=0)).astype(int),size-1)
        x,y=np.meshgrid(np.arange(low[0],high[0]+1)+.5,np.arange(low[1],high[1]+1)+.5)
        a,b,c=points;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:continue
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;w=1-u-v
        inside=(u>=0)&(v>=0)&(w>=0)
        if not inside.any():continue
        yy,xx=np.nonzero(inside);yy+=low[1];xx+=low[0]
        coverage[yy,xx]=True
        part,color,metal,rough,emission=palette[mesh.polygons[tri.polygon_index].material_index]
        rgb=np.array([int(color[k:k+2],16)/255 for k in (0,2,4)])
        # Deterministic fine brush/tooth pattern, restrained to protect readability.
        noise=np.sin(xx*.43+np.sin(yy*.071))*np.sin(yy*.67+xx*.11)
        grain=.035 if part in ('fur','mane','mane_light','leather') else .013
        maps['base_color'][yy,xx,:3]=np.clip(rgb[None,:]*(1+grain*noise[:,None]),0,1)
        maps['orm'][yy,xx,:3]=np.stack([np.ones_like(noise),np.clip(rough+noise*.025,0,1),np.full_like(noise,metal)],axis=1)
        maps['normal'][yy,xx,0]=.5+noise*grain*.4
        maps['normal'][yy,xx,1]=.5+np.cos(yy*.67)*grain*.4
        if emission:maps['emissive'][yy,xx,:3]=rgb
    # Eight-pixel gutter dilation for mipmap filtering; never overwrites island pixels.
    for _ in range(8):
        original=coverage.copy()
        for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            valid=np.roll(original,(dy,dx),(0,1))&~coverage
            if dy<0:valid[-1,:]=False
            if dy>0:valid[0,:]=False
            if dx<0:valid[:,-1]=False
            if dx>0:valid[:,0]=False
            for pixels in maps.values():pixels[valid]=np.roll(pixels,(dy,dx),(0,1))[valid]
            coverage|=valid
    images={};out=OUT/'textures';out.mkdir(parents=True,exist_ok=True)
    for name,pixels in maps.items():
        image=bpy.data.images.new('tex_solkael_v002_'+name,width=size,height=size,alpha=False)
        image.colorspace_settings.name='sRGB' if name in ('base_color','emissive') else 'Non-Color'
        # Byte-backed generated images store encoded sRGB; do not linearize twice.
        image.pixels.foreach_set(pixels.ravel());image.filepath_raw=str(out/(name+'.png'));image.file_format='PNG';image.save();image.pack();images[name]=image
    mat=bpy.data.materials.new('mat_solkael_lionheart_atlas_v002');mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=nodes.get('Principled BSDF')
    textures={}
    for name,img in images.items():
        tex=nodes.new('ShaderNodeTexImage');tex.image=img;tex.label=name;textures[name]=tex
    links.new(textures['base_color'].outputs['Color'],bsdf.inputs['Base Color'])
    normal=nodes.new('ShaderNodeNormalMap');links.new(textures['normal'].outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
    sep=nodes.new('ShaderNodeSeparateColor');links.new(textures['orm'].outputs['Color'],sep.inputs['Color']);links.new(sep.outputs['Green'],bsdf.inputs['Roughness']);links.new(sep.outputs['Blue'],bsdf.inputs['Metallic'])
    links.new(textures['emissive'].outputs['Color'],bsdf.inputs['Emission Color']);bsdf.inputs['Emission Strength'].default_value=1.15
    mesh.materials.clear();mesh.materials.append(mat)
    for polygon in mesh.polygons:polygon.material_index=0
    return dict(size=[size,size],channels=list(images),material_count=1,island_margin=.003,gutter_pixels=8,alpha=False,uv_method='Smart Project 72 degrees, area weighted; unique packed atlas')


def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--out-root',type=Path,default=ROOT)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    OUT=args.out_root/'art/characters/solkael_lionheart/v002'
    assert bpy.app.version[:2]==(5,2)
    sys.path.insert(0,str(ROOT/'tools/art'));from reference_lock import production_references
    refs=production_references();assert len(refs)==8
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.data.orphans_purge(do_recursive=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.fps=30
    rig,_=base.skeleton();g=geometry();obj,palette=base.make_mesh(g,rig)
    facial_and_weights(obj,g);textures=atlas(obj,palette);clips=base.animate(rig,obj)
    polish_animation(rig)
    manifest=json.loads((base.BASE/'solkael_asset.json').read_text())
    manifest.update(asset_version='v002',clips=clips,texture_policy='Original procedural PBR atlas; no reference pixels',textures=textures)
    source=OUT/'source/chr_solkael_lionheart_v002.blend';source.parent.mkdir(parents=True,exist_ok=True)
    manifest['source']=source.relative_to(args.out_root).as_posix()
    manifest['mesh_vertices']=len(obj.data.vertices)
    manifest['morphology']='Continuous torso and upper-arm lofts, layered opaque mane, oral volume and eyelids; paired integrated forearm towers'
    base.save_json(OUT/'solkael_asset.json',manifest)
    validate_scene(manifest)
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
    print('SOLKAEL_V002_SOURCE_PASS',flush=True)


def polish_animation(rig):
    from mathutils import Quaternion
    for action in bpy.data.actions:
        rig.animation_data.action=action
        frames=int(action.frame_end)
        for frame in range(frames+1):
            bpy.context.scene.frame_set(frame)
            t=frame/frames
            if action.name in ('attack_light','attack_heavy'):
                hit=.38 if action.name=='attack_light' else .5
                anticipation=math.sin(math.pi*t/hit)**2 if t<hit else 0
                recovery=math.sin(math.pi*(t-hit)/(1-hit))*math.exp(-4*(t-hit)) if t>=hit else 0
                strength=1 if action.name=='attack_light' else 1.6
                changes={'spine_02':((1,0,0),(-4*anticipation+2*recovery)*strength),'head':((0,0,1),2*recovery),'tail_03':((1,0,0),-5*anticipation+8*recovery)}
            elif action.name=='hit_react':
                changes={'head':((1,0,0),-7*math.sin(math.pi*t)*math.exp(-2*t)),'tail_03':((0,1,0),8*math.sin(math.pi*t))}
            else:changes={}
            for name,(axis,degrees) in changes.items():
                bone=rig.pose.bones[name]
                bone.rotation_quaternion=bone.rotation_quaternion @ Quaternion(axis,math.radians(degrees))
                bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=name)
    rig.animation_data.action=None
    for bone in rig.pose.bones:bone.matrix_basis.identity()


if __name__=='__main__':main()
