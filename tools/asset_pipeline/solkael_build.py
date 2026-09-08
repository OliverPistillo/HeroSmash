"""Blender 5.2: editable original mesh/rig/clip authoring from Solkael Art Lock v1.

Run via Blender --background --factory-startup --python-exit-code 1 --python ...
No image generation, tracing from legacy pixels, downloads or external libraries.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector, Quaternion, Matrix

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
HERO = "solkael_lionheart"
BASE = ROOT / "art/characters" / HERO
TAU = math.tau


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


class Geometry:
    def __init__(self):
        self.vertices, self.faces, self.materials, self.weights, self.regions, self.smooth = [], [], [], [], {}, []

    def add(self, verts, faces, mat, bone, region="", smooth=False):
        start = len(self.vertices)
        self.vertices.extend(tuple(v) for v in verts)
        self.faces.extend(tuple(start + i for i in f) for f in faces)
        self.materials.extend([mat] * len(faces))
        self.smooth.extend([smooth] * len(faces))
        self.weights.extend([bone] * len(verts))
        if region:
            self.regions.setdefault(region, []).extend(range(start, len(self.vertices)))

    def ellipsoid(self, center, radii, mat, bone, region="", segments=16, rings=10):
        verts = []
        for j in range(rings + 1):
            lat = math.pi * (j + 0.025) / (rings + 0.05)
            for i in range(segments):
                a = TAU * i / segments
                verts.append(tuple(center[k] + radii[k] * v for k, v in enumerate((math.sin(lat)*math.cos(a), math.sin(lat)*math.sin(a), math.cos(lat)))))
        faces = []
        for j in range(rings):
            for i in range(segments):
                a=j*segments+i; b=j*segments+(i+1)%segments
                faces.append((a,b,b+segments,a+segments))
        faces += [tuple(reversed(range(segments))), tuple(rings*segments+i for i in range(segments))]
        self.add(verts,faces,mat,bone,region,smooth=True)

    def tube(self, points, radii, mat, bone, region="", sides=10):
        verts=[]
        for n, (point,radius) in enumerate(zip(points,radii)):
            tangent=Vector(points[min(n+1,len(points)-1)])-Vector(points[max(0,n-1)])
            tangent.normalize()
            u=tangent.cross(Vector((0,1,0)))
            if u.length < 0.01: u=tangent.cross(Vector((1,0,0)))
            u.normalize(); v=tangent.cross(u).normalized()
            for i in range(sides):
                verts.append(Vector(point)+radius*(u*math.cos(TAU*i/sides)+v*math.sin(TAU*i/sides)))
        faces=[]
        for n in range(len(points)-1):
            for i in range(sides):
                a=n*sides+i;b=n*sides+(i+1)%sides
                faces.append((a,b,b+sides,a+sides))
        faces += [tuple(reversed(range(sides))),tuple((len(points)-1)*sides+i for i in range(sides))]
        self.add(verts,faces,mat,bone,region)

    def plate(self, outline, y, depth, mat, bone, region=""):
        """Beveled extruded X/Z outline; front faces point toward Blender -Y."""
        cx=sum(v[0] for v in outline)/len(outline);cz=sum(v[1] for v in outline)/len(outline)
        n=len(outline); verts=[]
        for factor,yy in [(0.91,y-depth/2),(1,y-depth*0.2),(1,y+depth*0.3),(0.92,y+depth/2)]:
            verts += [(cx+(x-cx)*factor,yy,cz+(z-cz)*factor) for x,z in outline]
        faces=[tuple(reversed(range(n))),tuple(3*n+i for i in range(n))]
        for r in range(3):
            for i in range(n): faces.append((r*n+i,r*n+(i+1)%n,(r+1)*n+(i+1)%n,(r+1)*n+i))
        self.add(verts,faces,mat,bone,region)

    def sun(self, x,y,z,size,bone):
        rays=[]
        for i in range(16):
            a=TAU*i/16; r=size*(1 if i%2==0 else .45)
            rays.append((x+math.sin(a)*r,z+math.cos(a)*r))
        self.plate(rays,y,.012,'gold',bone)
        self.ellipsoid((x,y-.012,z),(size*.46,.014,size*.46),'gold',bone,segments=16,rings=5)

    def tuft(self, base, tip, width, mat, bone):
        base,tip=Vector(base),Vector(tip)
        delta=tip-base
        # Sculpted solid, tapered fur clumps: no alpha cards or hair particle runtime.
        side=Vector((-delta.z,0,delta.x)).normalized()
        if side.length<.1:side=Vector((1,0,0))
        normal=Vector((0,-1,0))
        verts=[]
        for t,w in [(0,.45),(.3,1),(.68,.66),(1,.015)]:
            center=base+delta*t+normal*math.sin(t*math.pi)*width*.3
            for u,v in [(1,0),(0,1),(-1,0),(0,-.5)]:
                verts.append(center+side*width*w*u+normal*width*w*.4*v)
        faces=[(3,2,1,0),(12,13,14,15)]
        for r in range(3):
            for k in range(4):faces.append((r*4+k,r*4+(k+1)%4,(r+1)*4+(k+1)%4,(r+1)*4+k))
        self.add(verts,faces,mat,bone)


def material(name, color, metallic=0, roughness=.6, emission=0):
    def linear(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
    rgb=tuple(linear(int(color[n:n+2],16)/255) for n in (0,2,4))
    m=bpy.data.materials.new('mat_'+HERO+'_'+name);m.use_nodes=True
    m.diffuse_color=(*rgb,1)
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*rgb,1)
    bsdf.inputs['Metallic'].default_value=metallic;bsdf.inputs['Roughness'].default_value=roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value=(*rgb,1)
        bsdf.inputs['Emission Strength'].default_value=emission
    return m


def skeleton():
    family=json.loads((ROOT/'docs/art/rig_families.json').read_text())['families'][0]
    hierarchy=dict(family['base_hierarchy']); coords={
        'root':((0,0,0),(0,0,.12)), 'pelvis':((0,0,.96),(0,0,1.1)),
        'spine_01':((0,0,1.1),(0,0,1.24)), 'spine_02':((0,0,1.24),(0,0,1.39)),
        'spine_03':((0,0,1.39),(0,0,1.56)), 'neck':((0,0,1.56),(0,0,1.7)),
        'head':((0,0,1.7),(0,0,1.95)), 'jaw':((0,-.10,1.74),(0,-.23,1.68))}
    for side,sign in [('l',1),('r',-1)]:
        def pair(a,b):return (tuple(sign*x if n==0 else x for n,x in enumerate(a)),tuple(sign*x if n==0 else x for n,x in enumerate(b)))
        for name,a,b in [
            ('clavicle',(0,0,1.5),(.32,0,1.5)),('upperarm',(.32,0,1.5),(.66,0,1.5)),
            ('forearm',(.66,0,1.5),(1.04,0,1.5)),('hand',(1.04,0,1.5),(1.19,0,1.5)),
            ('thigh',(.18,0,.98),(.23,-.015,.54)),('shin',(.23,-.015,.54),(.24,0,.14)),
            ('foot',(.24,0,.14),(.24,-.16,.08)),('toe',(.24,-.16,.08),(.24,-.28,.07))]:coords[name+'_'+side]=pair(a,b)
        for digit,offset in [('thumb',-.07),('index',-.05),('middle',-.015),('ring',.025),('pinky',.06)]:
            for index in range(1,4):
                coords[f'{digit}_{index:02}_{side}']=pair((1.16+(index-1)*.037,offset,1.5),(1.16+index*.037,offset,1.5))
        name='ear_01_'+side;hierarchy[name]='head';coords[name]=pair((.13,0,1.92),(.18,0,2.01))
    for i,(a,b) in enumerate([((0,.14,1),(0,.26,.81)),((0,.26,.81),(0,.37,.6)),((0,.37,.6),(0,.51,.43)),((0,.51,.43),(0,.65,.38))],1):
        name=f'tail_{i:02}';hierarchy[name]='pelvis' if i==1 else f'tail_{i-1:02}';coords[name]=(a,b)
    for side,sign in [('l',1),('r',-1)]:
        name='mane_01_'+side;hierarchy[name]='head';coords[name]=((sign*.15,.08,1.82),(sign*.28,.10,1.63))
    for name,parent in family['sockets'].items():
        hierarchy[name]=parent;a=coords[parent][1];coords[name]=(a,(a[0],a[1],a[2]+.025))
    arm=bpy.data.armatures.new('HeroSkeleton');rig=bpy.data.objects.new('HeroSkeleton',arm)
    bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name,parent in hierarchy.items():
        bone=arm.edit_bones.new(name);bone.head,bone.tail=coords[name]
        if parent:bone.parent=arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
    return rig,coords


def body_geometry():
    g=Geometry()
    g.ellipsoid((0,0,1.19),(.255,.14,.3),'indigo','spine_01')
    g.ellipsoid((0,0,1.4),(.355,.17,.21),'indigo','spine_03')
    chest=[(-.34,1.53),(-.17,1.6),(0,1.55),(.17,1.6),(.34,1.53),(.29,1.35),(0,1.20),(-.29,1.35)]
    for y in [-.155,.14]:
        g.plate(chest,y,.04,'gold','spine_03')
        g.plate([(x*.94,1.41+(z-1.41)*.90) for x,z in chest],y+(-.026 if y<0 else .026),.016,'indigo','spine_03')
        g.sun(0,y+(-.05 if y<0 else .05),1.43,.10,'spine_03')
    g.ellipsoid((0,0,.995),(.255,.16,.075),'leather','pelvis')
    g.sun(0,-.18,1.005,.07,'pelvis')
    g.plate([(-.085,1.02),(.085,1.02),(.075,.76),(0,.715),(-.075,.76)],-.165,.035,'gold','pelvis')
    g.plate([(-.065,.99),(.065,.99),(.06,.78),(0,.742),(-.06,.78)],-.19,.012,'indigo','pelvis')
    for side,s in [('l',1),('r',-1)]:
        thigh='thigh_'+side;shin='shin_'+side;foot='foot_'+side;hand='hand_'+side;fore='forearm_'+side
        g.ellipsoid((s*.19,0,.78),(.15,.14,.245),'indigo',thigh)
        g.ellipsoid((s*.23,0,.34),(.095,.105,.23),'indigo',shin)
        g.ellipsoid((s*.24,-.08,.09),(.115,.2,.09),'fur',foot)
        for k in range(4):
            x=s*.24+(k-1.5)*.047
            g.ellipsoid((x,-.22,.06),(.028,.085,.059),'fur','toe_'+side,segments=10,rings=6)
            g.tube([(x,-.268,.07),(x,-.313,.031)],[.013,.001],'glove','toe_'+side,sides=6)
        for z,width,height,y,bone in [(.57,.108,.10,-.125,shin),(.30,.08,.16,-.103,shin),(.85,.10,.12,-.135,thigh)]:
            x=s*(.23 if z<.7 else .29)
            outline=[(x-width,z+height*.5),(x,z+height),(x+width,z+height*.5),(x+width*.6,z-height*.7),(x,z-height),(x-width*.6,z-height*.7)]
            g.plate(outline,y,.028,'gold',bone)
            g.plate([(x+(xx-x)*.75,z+(zz-z)*.77) for xx,zz in outline],y-.024,.012,'ivory' if z>.4 else 'indigo',bone)
        # Bare arms and built-in towers are authored in the skeleton T-pose.
        g.ellipsoid((s*.38,0,1.5),(.17,.155,.155),'fur','upperarm_'+side)
        g.ellipsoid((s*.53,0,1.5),(.185,.117,.125),'fur','upperarm_'+side)
        g.ellipsoid((s*.82,0,1.5),(.21,.095,.10),'glove',fore)
        g.ellipsoid((s*1.15,0,1.5),(.105,.085,.1),'glove',hand)
        for k in range(4):
            digit=['index','middle','ring','pinky'][k]
            for joint in range(1,4):
                x=s*(1.16+(joint-.5)*.037);bone=f'{digit}_{joint:02}_{side}'
                g.ellipsoid((x,-.05+k*.035,1.5),(.024,.023,.038),'glove',bone,segments=8,rings=6)
                g.ellipsoid((x,-.05+k*.035,1.532),(.018,.024,.013),'gold',bone,segments=8,rings=5)
        g.ellipsoid((s*1.15,-.095,1.47),(.065,.04,.037),'glove','thumb_01_'+side,segments=10,rings=6)
        outline=[(s*.71,1.40),(s*.76,1.35),(s*1.17,1.35),(s*1.25,1.43),(s*1.25,1.57),(s*1.17,1.65),(s*.76,1.65),(s*.71,1.6)]
        if s<0:outline.reverse()
        g.plate(outline,-.10,.17,'gold',fore)
        center=s*.98
        def inset(scale):return [(center+(x-center)*scale,1.5+(z-1.5)*scale) for x,z in outline]
        g.plate(inset(.89),-.193,.016,'emission',fore)
        g.plate(inset(.80),-.206,.014,'ivory',fore)
        g.sun(s*.97,-.223,1.5,.072,fore)
        # Back straps and angular ceramic shoulder bridges.
        for x in [.77,1.10]:g.ellipsoid((s*x,.03,1.5),(.022,.12,.14),'leather',fore,segments=10,rings=6)
        g.plate([(s*.23,1.59),(s*.31,1.65),(s*.42,1.63),(s*.41,1.53)],-.09,.07,'gold','clavicle_'+side)
        g.plate([(s*.26,1.59),(s*.32,1.63),(s*.39,1.61),(s*.38,1.55)],-.135,.016,'ivory','clavicle_'+side)
        for k in range(5):
            x=s*(.32+k*.032)
            g.tuft((x,-.09,1.58),(x+s*.06,-.10,1.48),.035,'fur','upperarm_'+side)
    # A sculpted radial layered mane with open face and distinct crown silhouette.
    g.ellipsoid((0,.065,1.8),(.245,.155,.275),'mane','head')
    for layer,(count,radius,length,y) in enumerate([(23,.17,.15,.055),(19,.16,.115,-.015),(15,.155,.085,-.08)]):
        for k in range(count):
            a=TAU*k/count+.11*layer
            dx,dz=math.sin(a),math.cos(a)
            base=(dx*radius,y,1.8+dz*radius)
            tip=(dx*(radius+length),y+.035,1.8+dz*(radius+length)-.028)
            mat='mane' if (k+layer)%3 else 'mane_light'
            g.tuft(base,tip,.047 if layer==0 else .040,mat,'mane_01_'+('l' if dx>0 else 'r'))
    # Lion facial planes; brow/eyelid/jaw components retain explicit morph regions.
    g.ellipsoid((0,-.075,1.81),(.154,.12,.14),'fur','head','face',segments=24,rings=14)
    for s,side in [(1,'l'),(-1,'r')]:
        g.ellipsoid((s*.088,-.145,1.78),(.068,.062,.065),'fur','head','cheek_'+side)
        g.ellipsoid((s*.06,-.189,1.835),(.044,.020,.025),'glove','head','eye_socket_'+side,segments=16,rings=8)
        g.ellipsoid((s*.06,-.207,1.835),(.031,.009,.017),'gold','head','eye_'+side,segments=16,rings=8)
        g.ellipsoid((s*.06,-.215,1.835),(.010,.005,.015),'glove','head','pupil_'+side,segments=12,rings=6)
        g.ellipsoid((s*.053,-.218,1.842),(.004,.002,.004),'ivory','head','eye_'+side,segments=8,rings=4)
        g.ellipsoid((s*.058,-.197,1.863),(.052,.022,.016),'mane_light','head','brow_'+side,segments=12,rings=6)
        g.ellipsoid((s*.044,-.207,1.747),(.053,.049,.035),'ivory','head','muzzle_'+side,segments=16,rings=8)
        g.ellipsoid((s*.145,-.015,1.923),(.062,.043,.062),'fur','ear_01_'+side,'ear_'+side)
        g.ellipsoid((s*.149,-.05,1.924),(.035,.012,.038),'mane','ear_01_'+side,'ear_'+side)
        for k in range(3):g.ellipsoid((s*(.035+k*.015),-.25+k*.003,1.745),(.0025,.002,.0025),'glove','head',segments=6,rings=4)
    g.ellipsoid((0,-.188,1.705),(.072,.056,.040),'ivory','jaw','jaw',segments=16,rings=10)
    g.plate([(-.031,1.785),(0,1.79),(.031,1.785),(.023,1.772),(0,1.758),(-.023,1.772)],-.239,.022,'glove','head','nose')
    g.ellipsoid((0,-.203,1.719),(.052,.030,.015),'glove','jaw','mouth',segments=16,rings=8)
    for s in [-1,1]:
        g.tube([(s*.04,-.23,1.73),(s*.035,-.238,1.699)],[.008,.001],'ivory','head','tooth',sides=8)
    for k in range(5):g.tuft(((k-2)*.015,-.16,1.704),((k-2)*.014,-.175,1.65),.022,'ivory','jaw')
    # Three sculpted gold crown facets integrated with the mane, no helmet/cape.
    for s in [-1,0,1]:
        x=s*.115;z=1.97 if s else 2.015
        g.plate([(x-.030,z),(x,z+.084),(x+.030,z),(x,z-.049)],-.05,.025,'gold','head')
    points=[(0,.14,1),(0,.26,.81),(0,.37,.60),(0,.51,.43),(0,.65,.38)]
    for k in range(4):g.tube(points[k:k+2],[.035-.004*k,.031-.004*k],'fur',f'tail_{k+1:02}',sides=12)
    for k in range(9):
        a=k*TAU/9
        g.tuft((math.sin(a)*.032,.61, .40+math.cos(a)*.032),(math.sin(a)*.016,.76,.32),.034,'mane','tail_04')
    return g


def make_mesh(g,rig):
    palette=[('fur','C89A63',0,.78,0),('mane','5B3320',0,.82,0),('mane_light','814A28',0,.8,0),('indigo','2A2F45',.15,.56,0),('ivory','E5DDD0',.05,.32,0),('gold','B8995A',.8,.30,0),('leather','4A3428',0,.85,0),('glove','1B1B1F',0,.72,0),('emission','FFB347',.15,.32,1.5)]
    mesh=bpy.data.meshes.new('mesh_'+HERO);mesh.from_pydata(g.vertices,[],g.faces);mesh.update()
    obj=bpy.data.objects.new('mesh_'+HERO,mesh);bpy.context.collection.objects.link(obj)
    names=[p[0] for p in palette]
    for p in palette:mesh.materials.append(material(*p))
    for face,mat,smooth in zip(mesh.polygons,g.materials,g.smooth):face.material_index=names.index(mat);face.use_smooth=smooth
    # Stable per-face planar UVs support valid tangent generation even with scalar
    # materials. These overlapping UVs are not claimed to be a paint-ready atlas.
    uv=mesh.uv_layers.new(name='UVMap')
    for face in mesh.polygons:
        normal=face.normal;drop=max(range(3),key=lambda k:abs(normal[k]));axes=[k for k in range(3) if k!=drop]
        points=[mesh.vertices[mesh.loops[i].vertex_index].co for i in face.loop_indices]
        lows=[min(v[k] for v in points) for k in axes];spans=[max(v[k] for v in points)-lows[n] for n,k in enumerate(axes)]
        for i,v in zip(face.loop_indices,points):uv.data[i].uv=tuple((v[k]-lows[n])/max(spans[n],1e-7) for n,k in enumerate(axes))
    for name in sorted(set(g.weights)):
        group=obj.vertex_groups.new(name=name);group.add([i for i,b in enumerate(g.weights) if b==name],1,'REPLACE')
    modifier=obj.modifiers.new('HeroSkin','ARMATURE');modifier.object=rig;obj.parent=rig
    obj.shape_key_add(name='Basis')
    expressions={
        'focused':(-.009,0,0,.5),'aggressive':(-.016,-.028,0,.15),'casting':(-.010,-.009,0,.2),
        'pain_light':(-.014,-.004,.009,.8),'pain_heavy':(-.018,-.024,.013,1),
        'stunned':(.014,-.018,0,0),'victory':(.006,0,0,.15),'defeat':(.009,-.007,0,.55),'ko':(-.005,-.01,0,1)}
    for name,(brow,jaw,asym,close) in expressions.items():
        key=obj.shape_key_add(name='expr_'+name,from_mix=False)
        key.value=0.0
        for side,s in [('l',1),('r',-1)]:
            for index in g.regions['brow_'+side]:key.data[index].co.z+=brow+s*asym
            for region in ['eye_','pupil_']:
                for index in g.regions[region+side]:
                    v=key.data[index].co;v.z=1.835+(v.z-1.835)*(1-close*.92)
            for index in g.regions['ear_'+side]:key.data[index].co.z-=close*.018
        for region in ['jaw','mouth']:
            for index in g.regions[region]:key.data[index].co.z+=jaw;key.data[index].co.y+=abs(jaw)*.2
        if name=='aggressive':
            for side in ['l','r']:
                for index in g.regions['muzzle_'+side]:key.data[index].co.z+=.012
    return obj,palette


def world_rotation(bone, degrees):
    q=Quaternion((1,0,0),math.radians(degrees[0])) @ Quaternion((0,1,0),math.radians(degrees[1])) @ Quaternion((0,0,1),math.radians(degrees[2]))
    basis=bone.bone.matrix_local.to_quaternion()
    bone.rotation_mode='QUATERNION';bone.rotation_quaternion=basis.inverted() @ q @ basis


def global_pose_rotation(bone):
    rest=bone.bone.matrix_local.to_quaternion()
    if bone.parent:
        relative=bone.parent.bone.matrix_local.to_quaternion().inverted() @ rest
        return global_pose_rotation(bone.parent) @ relative @ bone.rotation_quaternion
    return rest @ bone.rotation_quaternion


def point_bone(bone,direction):
    rest=bone.bone.matrix_local.to_quaternion()
    y=(bone.bone.tail_local-bone.bone.head_local).normalized()
    target=Vector(direction).normalized()
    def frame(axis):
        front=Vector((0,-1,0));front-=axis*front.dot(axis)
        if front.length<.05:
            front=Vector((0,0,1));front-=axis*front.dot(axis)
        front.normalize()
        return Matrix((axis,front,axis.cross(front))).transposed()
    desired=(frame(target) @ frame(y).transposed()).to_quaternion() @ rest
    parent_pose=global_pose_rotation(bone.parent) if bone.parent else Quaternion()
    relative=bone.parent.bone.matrix_local.to_quaternion().inverted() @ rest if bone.parent else rest
    bone.rotation_quaternion=relative.inverted() @ parent_pose.inverted() @ desired


def animate(rig,obj):
    spec=json.loads((ROOT/'docs/art/animation_contract.json').read_text())
    lengths={'idle':60,'idle_breathing':90,'intro':60,'attack_light':24,'attack_heavy':42,'skill_cast':60,'hit_react':18,'dodge':24,'ko':60,'victory':75}
    manifest=[]
    for clip in spec['clips']:
        name=clip['name'];frames=lengths[name]
        action=bpy.data.actions.new(name);action.use_fake_user=True
        rig.animation_data_create();rig.animation_data.action=action
        for frame in range(frames+1):
            t=frame/frames;pulse=math.sin(math.pi*t)**2
            for bone in rig.pose.bones:bone.location=(0,0,0);bone.scale=(1,1,1);world_rotation(bone,(0,0,0))
            # Forward guard; local elbow extension is rigidly skinned under towers.
            for side,s in [('l',1),('r',-1)]:
                world_rotation(rig.pose.bones['upperarm_'+side],(0,s*80,-s*10))
                world_rotation(rig.pose.bones['forearm_'+side],(0,-s*155,0))
                world_rotation(rig.pose.bones['hand_'+side],(0,0,0))
                for digit in ['index','middle','ring','pinky']:
                    for joint in [1,2,3]:world_rotation(rig.pose.bones[f'{digit}_{joint:02}_{side}'],(0,s*35,0))
            if name in ('idle','idle_breathing'):
                b=math.sin(TAU*t);world_rotation(rig.pose.bones['spine_03'],(b*.8,0,0))
                world_rotation(rig.pose.bones['tail_03'],(0,b*4,0))
            elif name in ('attack_light','attack_heavy'):
                strength=1 if name=='attack_light' else 1.25
                hit=.38 if name=='attack_light' else .5
                hitpulse=max(0,1-abs(t-hit)/(.25 if name=='attack_light' else .32))
                arm='l' if name=='attack_light' else 'r';s=1 if arm=='l' else -1
                world_rotation(rig.pose.bones['upperarm_'+arm],(0,s*(80-80*hitpulse),-s*(10+80*hitpulse)))
                world_rotation(rig.pose.bones['forearm_'+arm],(0,-s*(155-155*hitpulse),0))
                world_rotation(rig.pose.bones['spine_03'],(hitpulse*5*strength,0,-hitpulse*12*strength))
            elif name=='skill_cast':
                for side,s in [('l',1),('r',-1)]:
                    world_rotation(rig.pose.bones['upperarm_'+side],(0,s*(80-5*pulse),-s*(10+45*pulse)))
                    world_rotation(rig.pose.bones['forearm_'+side],(0,-s*(155-25*pulse),-s*30*pulse))
                world_rotation(rig.pose.bones['head'],(pulse*5,0,0))
            elif name=='hit_react':world_rotation(rig.pose.bones['spine_03'],(-pulse*15,0,pulse*8))
            elif name=='dodge':
                world_rotation(rig.pose.bones['spine_01'],(0,pulse*18,pulse*4))
                rig.pose.bones['pelvis'].location.x=-pulse*.09
            elif name=='intro':
                world_rotation(rig.pose.bones['head'],(pulse*8,0,pulse*10))
                world_rotation(rig.pose.bones['spine_03'],(-pulse*3,0,0))
            elif name=='victory':
                world_rotation(rig.pose.bones['upperarm_r'],(0,-80+90*pulse,10))
                world_rotation(rig.pose.bones['forearm_r'],(0,155-90*pulse,0))
                world_rotation(rig.pose.bones['head'],(-pulse*8,0,0))
            elif name=='ko':
                settle=t*t*(3-2*t)
                world_rotation(rig.pose.bones['pelvis'],(0,settle*80,0))
                # Pelvis motion is local visual collapse; root stays identity.
                rig.pose.bones['pelvis'].location=(0,-settle*.45,0)
                world_rotation(rig.pose.bones['head'],(settle*20,0,0))
                for side,factor in [('l',1),('r',.5)]:
                    world_rotation(rig.pose.bones['thigh_'+side],(-35*settle*factor,0,0))
                    world_rotation(rig.pose.bones['shin_'+side],(80*settle*factor,0,0))
            # Directed, fixed-length arm chains keep the integrated tower faces
            # legible and make the barrier contact distinct from the idle guard.
            if name!='ko':
                for side,s in [('l',1),('r',-1)]:
                    shoulder=Vector((s*.32,0,1.5))
                    elbow=Vector((s*.45,-.16,1.25));wrist=Vector((s*.32,-.24,1.60))
                    if name=='skill_cast':
                        elbow=elbow.lerp(Vector((s*.44,-.15,1.27)),pulse)
                        wrist=wrist.lerp(Vector((s*.075,-.30,1.32)),pulse)
                    if (name=='attack_light' and side=='l') or (name=='attack_heavy' and side=='r'):
                        elbow=elbow.lerp(Vector((s*.32,-.34,1.5)),hitpulse)
                        wrist=wrist.lerp(Vector((s*.32,-.72,1.5)),hitpulse)
                    if name=='victory' and side=='r':
                        elbow=elbow.lerp(Vector((s*.48,-.03,1.78)),pulse)
                        wrist=wrist.lerp(Vector((s*.48,-.03,2.13)),pulse)
                    point_bone(rig.pose.bones['upperarm_'+side],elbow-shoulder)
                    point_bone(rig.pose.bones['forearm_'+side],wrist-elbow)
            for side,s in [('l',1),('r',-1)]:world_rotation(rig.pose.bones['mane_01_'+side],(0,math.sin(TAU*t)*s*1.4,0))
            for bone in rig.pose.bones:
                bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=bone.name)
                if bone.name=='pelvis':bone.keyframe_insert(data_path='location',frame=frame,group=bone.name)
        action.frame_start=0;action.frame_end=frames;action.use_frame_range=True
        if name=='ko':
            # Resolve actual skinned floor contact, not an assumed pose-box height.
            for frame in range(frames+1):
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
                low=min(Vector(v).z for v in evaluated.bound_box)
                bone=rig.pose.bones['pelvis'];bone.location.y-=low
                bone.keyframe_insert(data_path='location',frame=frame,group='pelvis')
        phases={'windup_start':0,'hit':.38 if name=='attack_light' else .5,'cast':.5,'recover_start':.68,'recover_end':1,'vfx_spawn':.5}
        markers=[dict(name=m,phase=phases[m]) for m in clip['required_markers']]
        if name=='skill_cast':markers.append(dict(name='vfx_spawn',phase=.5))
        for marker in markers:action.pose_markers.new(marker['name']).frame=round(marker['phase']*frames)
        manifest.append(dict(name=name,frames=frames,fps=30,duration_seconds=frames/30,loop=clip['loop'],root_motion=False,markers=markers))
    rig.animation_data.action=None
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    return manifest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out-root',type=Path,default=ROOT);parser.add_argument('--fixture',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    assert bpy.app.version[:2]==(5,2),bpy.app.version_string
    sys.path.insert(0,str(ROOT/'tools/art'));from reference_lock import production_references
    refs=production_references();assert len(refs)==8
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.data.orphans_purge(do_recursive=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.fps=30
    scene.frame_start=0;scene.frame_end=90
    scene.collection.children[0].name='SOLKAEL_EXPORT' if not args.fixture else 'CONVENTION_FIXTURE'
    if args.fixture:
        g=Geometry();g.plate([(-.2,0),(.2,0),(.2,1),(-.2,1)],0,.2,'gold','root')
        g.tube([(0,-.10,.5),(0,-.4,.5)],[.035,.005],'ivory','root')
        rig,_=skeleton();obj,_=make_mesh_fixture(g,rig)
        out=args.out_root/'.work/fighter-fixture';out.mkdir(parents=True,exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'convention.blend'))
        bpy.ops.export_scene.gltf(filepath=str(out/'convention.glb'),export_format='GLB',export_yup=True,export_animations=False,export_skins=True)
        print('CONVENTION_FIXTURE_PASS');return
    rig,coords=skeleton();g=body_geometry();obj,palette=make_mesh(g,rig);clips=animate(rig,obj)
    scene.frame_set(0)
    source=args.out_root/'art/characters'/HERO/'source'/f'chr_{HERO}_v001.blend'
    source.parent.mkdir(parents=True,exist_ok=True)
    rig['art_lock']='v1';rig['hero_id']=HERO;rig['root_motion']=False
    obj['source']='eight owner-approved references; procedural editable project mesh'
    scene['asset_stage']='first production pipeline fighter; visual review required'
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
    manifest=dict(schema_version=1,hero_id=HERO,art_lock='v1',blender=bpy.app.version_string,skull_height_m=1.95,reference_ids=[r['id'] for r in refs.values()],rig_family='medium_biped',clips=clips,expressions=['neutral']+list(k.name.removeprefix('expr_') for k in obj.data.shape_keys.key_blocks if k.name!='Basis'),palette=[dict(part=p[0],srgb='#'+p[1],metallic=p[2],roughness=p[3],emission_strength=p[4]) for p in palette],bones={b.name:dict(parent=b.parent.name if b.parent else None,head=list(b.head_local),tail=list(b.tail_local),rest_matrix=[list(r) for r in b.matrix_local]) for b in rig.data.bones},mesh_vertices=len(g.vertices),source=str(source.relative_to(args.out_root)).replace('\\','/'),morphology='solid sculpted fur clumps; no transparent fur cards; paired forearm towers; five glove digits',texture_policy='Scalar PBR colors from approved palette; no reference pixels embedded as textures')
    save_json(args.out_root/'art/characters'/HERO/'solkael_asset.json',manifest)
    print('SOLKAEL_SOURCE_PASS '+str(source))


def make_mesh_fixture(g,rig):
    mesh=bpy.data.meshes.new('fixture');mesh.from_pydata(g.vertices,[],g.faces);mesh.update()
    obj=bpy.data.objects.new('fixture',mesh);bpy.context.collection.objects.link(obj)
    mesh.materials.append(material('fixture','B8995A'))
    obj.parent=rig;mod=obj.modifiers.new('skin','ARMATURE');mod.object=rig
    group=obj.vertex_groups.new(name='root');group.add(list(range(len(g.vertices))),1,'REPLACE')
    return obj,[]


if __name__=='__main__':main()
