"""Scoped v003 edits of the hydrated, saved v002 source; no new rig or hero.

The v002 recipe supplies semantic face/part indices only after every Basis vertex
is compared with the actual saved source. Untouched geometry comes from that
source, and its existing armature/actions are retained. No reference pixels are
sampled. Run in the already installed Blender 5.2 LTS.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Vector, Quaternion

sys.path.insert(0, str(Path(__file__).parent))
import solkael_build as base
import solkael_polish as v2
from solkael_export import validate_scene

ROOT = base.ROOT
BASELINE = ROOT / 'art/characters/solkael_lionheart/v002'
SOURCE_SHA = '9d4165f9cc7dc562db5bda05e4f0420bdccd53908004a828d93ea9acb036ff0b'
EXPRESSIONS = ['focused', 'aggressive', 'casting', 'pain_light', 'pain_heavy',
               'stunned', 'victory', 'defeat', 'ko']
PALETTE = [
    ('fur', 'C89A63', 0, .80, 0), ('mane', '5B3320', 0, .86, 0),
    ('mane_light', '814A28', 0, .78, 0), ('indigo', '2A2F45', .22, .48, 0),
    ('ivory', 'E5DDD0', 0, .39, 0), ('gold', 'B8995A', .88, .36, 0),
    ('leather', '4A3428', 0, .83, 0), ('glove', '1B1B1F', 0, .76, 0),
    ('emission', 'FFB347', .1, .32, 1),
    # Tonal variations within the approved overall palette; still one atlas.
    ('muzzle_fur', 'D4B386', 0, .82, 0), ('eye', 'DCA43F', .05, .23, 0),
    ('fur_shadow', 'A77542', 0, .85, 0), ('fabric', '242A3D', 0, .88, 0),
]


class Sculpture(base.Geometry):
    loft = v2.PolishGeometry.loft

    def lock(self, controls, width, depth, mat, bone, region='mane_flow'):
        """Broad curved opaque hair lock with a central ridge and tapered hook."""
        controls = [Vector(p) for p in controls]
        verts = []
        steps, sides = 6, 6
        for row in range(steps):
            t = row / (steps - 1)
            center = ((1-t)**3*controls[0] + 3*(1-t)**2*t*controls[1]
                      + 3*(1-t)*t*t*controls[2] + t**3*controls[3])
            tangent = (3*(1-t)**2*(controls[1]-controls[0])
                       + 6*(1-t)*t*(controls[2]-controls[1])
                       + 3*t*t*(controls[3]-controls[2])).normalized()
            side = tangent.cross(Vector((0, -1, 0))).normalized()
            if side.length < .1:
                side = Vector((1, 0, 0))
            normal = tangent.cross(side).normalized()
            profile = (.52 + .6*math.sin(math.pi*t))*(1-t)**.65 + .008
            for k in range(sides):
                a = math.tau*k/sides
                verts.append(center + side*width*profile*math.cos(a)
                             + normal*depth*profile*math.sin(a))
        faces = [tuple(reversed(range(sides)))]
        for row in range(steps-1):
            for k in range(sides):
                a = row*sides+k; b = row*sides+(k+1)%sides
                faces.append((a, b, b+sides, a+sides))
        faces.append(tuple((steps-1)*sides+k for k in range(sides)))
        self.add(verts, faces, mat, bone, region, True)

    def wrap(self, cx, z, rx, ry, height, bone, mat='leather', region='straps'):
        self.loft([((cx, 0, z+dz), rx, ry) for dz in (-height/2, height/2)],
                  2, mat, bone, region)


def part_components(g):
    parent = list(range(len(g.vertices)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for face in g.faces:
        r = find(face[0])
        for i in face[1:]: parent[find(i)] = r
    groups = {}
    for i in range(len(parent)): groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def retain_and_reshape(old, obj):
    """Delete only targeted connected parts; keep source vertex/face provenance."""
    basis = obj.data.shape_keys.key_blocks['Basis']
    assert len(old.vertices) == len(basis.data)
    assert len(old.faces) == len(obj.data.polygons)
    error = max((Vector(a)-b.co).length for a, b in zip(old.vertices, basis.data))
    assert error < 1e-6, ('Saved v002 and semantic indices disagree', error)
    old.vertices = [tuple(v.co) for v in basis.data]
    regions = {i: name for name, ids in old.regions.items() for i in ids}
    remove = set()
    for ids in part_components(old):
        bone = old.weights[ids[0]]
        # Face/mane/crown and complete leg shells are the specifically authorized
        # art replacements. Ears, feet, digits, rig and source actions survive.
        if bone in ('head', 'jaw', 'mane_01_l', 'mane_01_r'):
            remove.update(ids)
        if bone.startswith(('thigh_', 'shin_')):
            remove.update(ids)
    g = Sculpture(); mapping = {}
    for i, vertex in enumerate(old.vertices):
        if i in remove: continue
        x, y, z = vertex; bone = old.weights[i]
        region = regions.get(i, '')
        if region == 'torso':
            weight = math.exp(-((z-1.43)/.19)**2)
            x *= 1+.11*weight; y *= 1+.24*weight
        elif bone == 'spine_03':
            x *= 1.06
            y *= 1.08
            if y < 0: y -= .015 + .035*(1-min(1, abs(x)/.38))
        elif bone.startswith('upperarm_'):
            # Deltoid peak, defined biceps/triceps, and a smaller elbow bridge.
            f = math.exp(-((abs(x)-.395)/.105)**2)
            y *= 1+.14*f; z = 1.5+(z-1.5)*(1+.16*f)
        elif bone.startswith(('foot_', 'toe_')):
            # Preserve the contact floor while giving toes a knuckle/arch.
            center = .24 if x > 0 else -.24
            x = center+(x-center)*1.08
            z *= 1+.14*max(0, 1-abs(y+.11)/.19)
        elif bone.startswith('ear_'):
            center = .145 if x > 0 else -.145
            x = center+(x-center)*.70
            y = -.015+(y+.015)*.70+.032
            z = 1.923+(z-1.923)*.70
        mapping[i] = len(g.vertices)
        g.vertices.append((x, y, z)); g.weights.append(bone)
    for face, mat, smooth in zip(old.faces, old.materials, old.smooth):
        if face[0] in remove: continue
        ids = tuple(mapping[i] for i in face)
        # Restrict the emitter to side channels; remove the broad luminous rim.
        if mat == 'emission': mat = 'gold'
        g.faces.append(ids); g.materials.append(mat); g.smooth.append(smooth)
    for name, ids in old.regions.items():
        g.regions[name] = [mapping[i] for i in ids if i in mapping]
    return g, dict(source_basis_max_error_m=error, retained_vertices=len(mapping),
                   replaced_vertices=len(remove), source_vertices=len(old.vertices))


def face(g):
    # Longer angular nasal plane and cheek/chin hierarchy, smaller forehead dome.
    g.loft([((0, y, z), x, d) for z, x, y, d in [
        (1.69,.065,-.072,.070),(1.73,.096,-.073,.080),
        (1.78,.128,-.070,.104),(1.82,.133,-.065,.123),
        (1.85,.132,-.080,.131),(1.885,.117,-.055,.115),(1.914,.091,-.026,.094),
        (1.944,.041,-.001,.044)]], 2, 'fur', 'head', 'face')
    g.loft([((0, y, z), x, d) for z, x, y, d in [
        (1.759,.031,-.200,.058),(1.785,.041,-.175,.071),
        (1.823,.032,-.154,.067),(1.852,.027,-.123,.049),
        (1.876,.039,-.100,.034)]], 2, 'fur', 'head', 'bridge')
    g.ellipsoid((0,-.191,1.712),(.059,.043,.028),'glove','head','oral_cavity',segments=18,rings=7)
    g.ellipsoid((0,-.198,1.692),(.066,.053,.033),'muzzle_fur','jaw','jaw',segments=20,rings=8)
    # Taper the chin into a short cream beard, distinct from ceramic armor.
    for k in range(7):
        x=(k-3)*.013
        g.lock([(x,-.218,1.689),(x,-.239,1.674),(x*.8,-.235,1.656),
                (x*.7,-.217,1.638+abs(x)*.22)], .017,.006,
               'muzzle_fur','jaw','beard')
    g.plate([(-.033,1.781),(-.018,1.785),(0,1.780),(.018,1.785),
             (.033,1.781),(.026,1.764),(0,1.749),(-.026,1.764)],
            -.260,.027,'glove','head','nose')
    g.tube([(0,-.274,1.752),(0,-.276,1.733),(0,-.269,1.719)],
           [.0025,.002,.002],'glove','head','philtrum',sides=6)
    for s, side in [(1,'l'),(-1,'r')]:
        web=[]
        for z,x,y in [(1.733,.061,-.212),(1.719,.067,-.210),
                      (1.701,.064,-.212),(1.685,.052,-.215)]:
            web.extend([(s*x,y,z),(s*(x-.009),y-.012,z)])
        g.add(web,[(k,k+1,k+3,k+2) for k in (0,2,4)],
              'muzzle_fur','head','mouth_web',True)
        g.ellipsoid((s*.096,-.109,1.782),(.044,.054,.058),
                    'fur','head','cheek_'+side,segments=18,rings=10)
        g.ellipsoid((s*.036,-.216,1.741),(.044,.054,.037),
                    'muzzle_fur','head','muzzle_'+side,segments=20,rings=10)
        # A narrow tear stripe seats the eye in the bridge and feline cheek.
        g.tube([(s*.033,-.209,1.823),(s*.043,-.215,1.802),
                (s*.059,-.205,1.779)],[.0035,.003,.0009],
               'fur_shadow','head','cheek_'+side,sides=6)
        g.tube([(0,-.272,1.720),(s*.025,-.269,1.712),(s*.050,-.254,1.714),
                (s*.067,-.235,1.726)],[.002,.003,.0025,.001],
               'glove','head','lip_'+side,sides=6)
        for k in range(3):
            g.ellipsoid((s*(.026+.014*k),-.267+.004*k,1.741-.003*k),
                        (.002,.0014,.002),'glove','head','muzzle_'+side,segments=6,rings=4)
            g.ellipsoid((s*(.012+.012*k),-.235,1.715),(.005,.008,.007),
                        'ivory','head','upper_teeth',segments=8,rings=4)
            g.ellipsoid((s*(.012+.012*k),-.234,1.707),(.004,.007,.004),
                        'ivory','jaw','lower_teeth',segments=8,rings=4)
        g.tube([(s*.048,-.228,1.719),(s*.049,-.232,1.704),(s*.044,-.236,1.694)],
               [.007,.005,.0007],'ivory','head','upper_teeth',sides=8)
        g.ellipsoid((s*.024,-.273,1.773),(.009,.003,.004),
                    'fur_shadow','head','nose',segments=10,rings=4)
        eye(g, s, side)
    g.ellipsoid((0,-.224,1.701),(.032,.016,.004),'mane_light','jaw','tongue',segments=12,rings=4)


def eye(g, s, side):
    cx, cy, cz = s*.061, -.182, 1.846
    g.ellipsoid((cx,cy,cz),(.030,.025,.021),'muzzle_fur','head','eyeball_'+side,segments=16,rings=8)
    g.ellipsoid((cx,cy-.024,cz),(.012,.002,.014),'eye','head','iris_'+side,segments=16,rings=6)
    g.ellipsoid((cx,cy-.026,cz),(.0045,.002,.011),'glove','head','pupil_'+side,segments=12,rings=6)
    g.ellipsoid((cx-s*.004,cy-.028,cz+.006),(.0026,.001,.0026),'ivory','head','glint_'+side,segments=8,rings=4)
    for upper in (True,False):
        verts=[]; n=17
        for row in range(4):
            t=row/3
            for k in range(n):
                a=math.pi*k/(n-1); dx=.030*math.cos(a)
                tilt=s*dx*.15
                inner=(.011 if upper else -.009)*math.sin(a)+tilt
                outer=(.031 if upper else -.026)*math.sin(a)+tilt
                dz=inner*(1-t)+outer*t
                xx=dx*(1+.3*t)
                # Curved eyelid surfaces sit on the eye ellipsoid, not flat cards.
                yy=cy-.025*math.sqrt(max(.025,1-(xx/.030)**2-(dz/.021)**2))-.005
                verts.append((cx+xx,yy,cz+dz))
        faces=[]
        for row in range(3):
            for k in range(n-1):
                a=row*n+k; f=(a,a+1,a+1+n,a+n)
                faces.append(tuple(reversed(f)) if upper else f)
        region=('upper_lid_' if upper else 'lower_lid_')+side
        g.add(verts,faces,'fur','head',region,True)
        rim=verts[:n]
        g.tube(rim,[.0018]*n,'glove','head',('upper_rim_' if upper else 'lower_rim_')+side,sides=6)
    # Sloped brows form a stern V; no floating rectangular eyebrow blocks.
    points=[(s*.026,-.182,1.862),(s*.044,-.193,1.866),(s*.070,-.191,1.875),
            (s*.097,-.164,1.870)]
    g.tube(points,[.014,.017,.014,.004],'fur','head','brow_'+side,sides=10)
    for k in range(3):
        x=s*(.097+k*.012)
        g.lock([(x,-.126,1.798-k*.027),(x+s*.022,-.150,1.786-k*.027),
                (x+s*.027,-.121,1.760-k*.025),(x+s*.032,-.085,1.746-k*.024)],
               .025,.009,'fur','head','cheek_'+side)


def mane(g):
    g.ellipsoid((0,.076,1.805),(.218,.148,.243),'mane','head','mane_mass',segments=24,rings=12)
    # Flow fans follow the approved crown: upward at the crest, backward/downward
    # beside the cheeks. Variation is deterministic, with no evenly radial cones.
    for s, side in [(1,'l'),(-1,'r')]:
        for k in range(6):
            z=1.965-k*.057
            x=.073+min(k,3)*.015
            g.lock([(s*x,-.065,z),(s*(x+.055),-.096,z+.019),
                    (s*(x+.098),-.064,z-.055),(s*(x+.102),-.019,z-.099)],
                   .046,.013,'mane_light' if k in (1,4) else 'mane',
                   'head','front_mane')
        for layer in range(2):
            for k in range(8):
                z=1.956-k*.050
                x=.065+.012*k+layer*.046
                y=.003+layer*.082
                lift=.07 if k<2 else -.045-.006*k
                g.lock([(s*x,y,z),(s*(x+.09),y-.010,z+.038),
                        (s*(x+.14),y+.04,z+lift),
                        (s*(x+.13+.012*math.sin(k*1.8)),y+.09,z+lift-.027)],
                       .051 if layer==0 else .06,.016,
                       'mane_light' if (k+layer)%4==1 else 'mane',
                       'mane_01_'+side)
        for k in range(5):
            z=1.98-k*.07
            g.lock([(s*.035,.17,z),(s*.13,.23,z-.02),
                    (s*.18,.24,z-.10),(s*.14,.21,z-.18)],
                   .06,.022,'mane' if k%3 else 'mane_light','head','back_mane')
        for k in range(3):
            x=s*(.09+.031*k)
            g.lock([(x,-.010,1.72),(x+s*.026,-.083,1.655),
                    (x-s*.012,-.043,1.59),(x-s*.040,.004,1.55+.02*k)],
                   .044,.014,'mane_light' if k==0 else 'mane','head','mane_beard')
    for k in range(-2,3):
        x=k*.044
        g.lock([(x,.008,1.916),(x*1.50,-.016,2.002),
                (x*2.15,.04,2.075-abs(k)*.018),(x*1.98,.075,2.135-abs(k)*.027)],
               .055,.017,'mane_light' if abs(k)==1 else 'mane','head','crown_mane')
    for s in (-1,0,1):
        x=s*.101; z=1.990 if s else 2.037
        g.plate([(x-.024,z),(x+s*.035,z+.059),(x+.026,z+.010),
                 (x,z-.034)],-.070,.014,'gold','head','crown')


def body_and_armor(g):
    for s,side in [(1,'l'),(-1,'r')]:
        thigh,shin,fore='thigh_'+side,'shin_'+side,'forearm_'+side
        # Anterior quadriceps and posterior calf use tapered, angled ring profiles.
        g.loft([((s*x,y,z),rx,ry) for z,x,y,rx,ry in [
            (.52,.231,-.009,.090,.086),(.60,.231,-.012,.102,.104),
            (.71,.218,.002,.135,.126),(.84,.196,.007,.166,.144),
            (.955,.183,.016,.141,.132),(.998,.182,.016,.099,.09)]],
            2,'fabric',thigh,'thigh_'+side)
        g.loft([((s*x,y,z),rx,ry) for z,x,y,rx,ry in [
            (.115,.24,0,.075,.074),(.22,.24,.012,.068,.076),
            (.34,.236,.031,.082,.111),(.44,.233,.023,.103,.119),
            (.53,.23,-.008,.091,.087),(.568,.23,-.011,.073,.077)]],
            2,'fabric',shin,'shin_'+side)
        for z,cx,rx,ry,bone in [(.70,s*.214,.140,.130,thigh),(.465,s*.232,.103,.127,shin),(.19,s*.24,.076,.085,shin)]:
            g.wrap(cx,z,rx,ry,.030,bone)
        for z,cx,w,h,y,bone,mat in [(.845,s*.285,.10,.14,-.136,thigh,'ivory'),
                                  (.55,s*.23,.094,.095,-.113,shin,'ivory'),
                                  (.319,s*.235,.076,.18,-.108,shin,'indigo')]:
            outline=[(cx-w,z+h*.65),(cx,z+h),(cx+w,z+h*.48),
                     (cx+w*.73,z-h*.60),(cx,z-h),(cx-w*.65,z-h*.5)]
            start=len(g.vertices)
            g.plate(outline,y,.032,'gold',bone,'leg_armor')
            g.plate([(cx+(x-cx)*.79,z+(zz-z)*.8) for x,zz in outline],y-.023,.014,mat,bone,'leg_armor')
            for i in range(start,len(g.vertices)):
                x,yy,zz=g.vertices[i]
                yy += .058*(abs(x-cx)/w)**1.5
                g.vertices[i]=(x,yy,zz)
        # Ankle cuffs overlap the foot rather than ending above a sphere.
        for y in (-.025,-.10):
            pts=[(s*.24+dx,y,.10+.056*math.sqrt(max(0,1-(dx/.12)**2))) for dx in (-.11,-.07,0,.07,.11)]
            g.tube(pts,[.012]*5,'leather','foot_'+side,'ankle_strap',sides=6)
        # Upper arm strap and elbow volume bridge the existing limb and tower.
        g.tube([(s*.604,0,1.5),(s*.665,0,1.5)],[.091,.087],
               'fur','upperarm_'+side,'elbow_'+side,sides=16)
        ring=[(s*.564,.124*math.cos(a),1.5+.131*math.sin(a)) for a in [math.tau*k/16 for k in range(17)]]
        g.tube(ring,[.013]*17,'leather','upperarm_'+side,'arm_strap',sides=6)
        # Curved flank inserts, belly lamellae and collar separate fabric/armor.
        for k in range(3):
            z=1.115+k*.084; x=s*(.15+k*.014)
            g.plate([(x-s*.027,z+.08),(x+s*.043,z+.10),
                     (x+s*.059,z+.028),(x+s*.028,z-.018)],
                    -.164-k*.018,.022,'gold','spine_02','flank_armor')
            g.plate([(x-s*.006,z+.071),(x+s*.027,z+.080),
                     (x+s*.039,z+.030),(x+s*.023,z)],
                    -.18-k*.018,.009,'ivory','spine_02','flank_armor')
        g.plate([(s*.14,1.55),(s*.22,1.61),(s*.21,1.66),(s*.12,1.64)],
                -.07,.13,'indigo','spine_03','collar')
        g.tube([(s*.145,-.142,1.56),(s*.215,-.142,1.611),(s*.207,-.142,1.65)],
               [.005]*3,'gold','spine_03','collar',sides=6)


def gauntlets(g):
    for s,side in [(1,'l'),(-1,'r')]:
        bone='forearm_'+side
        # Recessed channels and stepped end caps interrupt the old white box.
        for zz in (1.378,1.622):
            pts=[(s*.79,-.218,zz),(s*.90,-.226,zz),(s*1.12,-.225,zz)]
            g.tube(pts,[.008]*3,'glove',bone,'gauntlet_channel',sides=6)
            g.tube([(x,y-.003,z) for x,y,z in pts],[.003]*3,
                   'emission',bone,'gauntlet_emissive',sides=6)
        for x in (.76,1.175):
            for z in (1.402,1.598):
                outline=[(s*(x-.047),z+.023),(s*(x+.025),z+.034),
                         (s*(x+.050),z-.009),(s*(x-.019),z-.031)]
                if s<0:outline.reverse()
                g.plate(outline,-.232,.028,'gold',bone,'gauntlet_braces')
                g.ellipsoid((s*x,-.251,z),(.006,.003,.006),'glove',bone,
                            'gauntlet_rivets',segments=8,rings=4)
        # Layered inset nose/tail panels and a metallic central boss.
        for x in (.795,1.14):
            outline=[(s*(x-.036),1.43),(s*(x+.036),1.45),
                     (s*(x+.036),1.55),(s*(x-.036),1.57)]
            if s<0:outline.reverse()
            g.plate(outline,-.227,.018,'indigo',bone,'gauntlet_inset')
        for z in (1.425,1.575):
            g.plate([(s*.87,z),(s*.96,1.5),(s*1.07,z),
                     (s*.973,1.5+(.048 if z>1.5 else -.048))],
                    -.240,.014,'gold',bone,'sun_rays')
        circle=[(s*.97+.045*math.cos(a),-.248,1.5+.045*math.sin(a))
                for a in [math.tau*k/24 for k in range(25)]]
        g.tube(circle,[.004]*25,'glove',bone,'sun_bezel',sides=6)
        # Side ribs sit on the forearm housing, not on a separate shield object.
        for x in (.82,.97,1.10):
            for z in (1.361,1.639):
                g.tube([(s*x,-.15,z),(s*x,.015,z)],[.009,.009],
                       'gold',bone,'gauntlet_ribs',sides=6)


def merge_facial_planes(g):
    """Union only the edited facial skin volumes into a continuous sculpt surface."""
    names=['face','bridge','cheek_l','cheek_r','muzzle_l','muzzle_r','brow_l','brow_r']
    removed={i for name in names for i in g.regions[name]}
    indices=sorted(removed);lookup={i:k for k,i in enumerate(indices)}
    mesh=bpy.data.meshes.new('v003_facial_sculpt_work')
    mesh.from_pydata([g.vertices[i] for i in indices],[],
                     [tuple(lookup[i] for i in f) for f in g.faces if all(i in removed for i in f)])
    mesh.update();temp=bpy.data.objects.new('v003_facial_sculpt_work',mesh)
    bpy.context.collection.objects.link(temp)
    bpy.ops.object.select_all(action='DESELECT');temp.select_set(True)
    bpy.context.view_layer.objects.active=temp
    remesh=temp.modifiers.new('Facial union','REMESH');remesh.mode='VOXEL'
    remesh.voxel_size=.004;remesh.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=temp.modifiers.new('Surface continuity','SMOOTH');smooth.factor=.7;smooth.iterations=5
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    dec=temp.modifiers.new('Mobile facial topology','DECIMATE');dec.ratio=.055
    bpy.ops.object.modifier_apply(modifier=dec.name)
    result=Sculpture();mapping={}
    for i,v in enumerate(g.vertices):
        if i not in removed:
            mapping[i]=len(result.vertices);result.vertices.append(v);result.weights.append(g.weights[i])
    for f,m,s in zip(g.faces,g.materials,g.smooth):
        if f[0] not in removed:
            result.faces.append(tuple(mapping[i] for i in f));result.materials.append(m);result.smooth.append(s)
    for name,ids in g.regions.items():result.regions[name]=[mapping[i] for i in ids if i in mapping]
    offset=len(result.vertices)
    result.add([v.co[:] for v in temp.data.vertices],[tuple(f.vertices) for f in temp.data.polygons],
               'fur','head','face',True)
    for i in range(offset,len(result.vertices)):
        x,y,z=result.vertices[i]
        if y<-.185 and z<1.777:
            side='l' if x>=0 else 'r'
            result.regions['muzzle_'+side].append(i)
        if y<-.145 and 1.855<z<1.89 and abs(x)>.020:
            result.regions['brow_'+('l' if x>=0 else 'r')].append(i)
    work_mesh=temp.data;bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(work_mesh)
    return result


def mesh_and_face(g, rig):
    mesh=bpy.data.meshes.new('mesh_solkael_lionheart')
    mesh.from_pydata(g.vertices,[],g.faces); mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free();mesh.update()
    obj=bpy.data.objects.new('mesh_solkael_lionheart',mesh)
    bpy.context.collection.objects.link(obj)
    names=[p[0] for p in PALETTE]
    for p in PALETTE: mesh.materials.append(base.material(*p))
    for poly,mat,smooth in zip(mesh.polygons,g.materials,g.smooth):
        poly.material_index=names.index(mat); poly.use_smooth=smooth
    for name in sorted(set(g.weights)|{'spine_02'}):
        group=obj.vertex_groups.new(name=name)
        indices=[i for i,b in enumerate(g.weights) if b==name]
        if indices: group.add(indices,1,'REPLACE')
    obj.parent=rig; obj.modifiers.new('HeroSkin','ARMATURE').object=rig
    obj.shape_key_add(name='Basis')
    # brow height, jaw opening, left/right closure, snarl, smile, asymmetry
    specs={
        'focused':(-.008,0,.55,.55,0,0,0),
        'aggressive':(-.013,.038,.28,.28,.013,0,0),
        'casting':(-.005,.011,.28,.48,0,0,.004),
        'pain_light':(-.009,.013,.96,.55,.006,0,.006),
        'pain_heavy':(-.013,.031,1,1,.010,0,.003),
        'stunned':(.016,.021,-.36,-.36,0,0,0),
        'victory':(.006,.002,.12,.12,0,.009,0),
        'defeat':(.006,.004,.62,.62,0,-.004,0),
        'ko':(-.003,.014,1,1,0,0,0),
    }
    basis=obj.data.shape_keys.key_blocks['Basis']
    for name,(brow,jaw,cl,cr,snarl,smile,asym) in specs.items():
        key=obj.shape_key_add(name='expr_'+name,from_mix=False)
        key.relative_key=basis
        key.value=0.0
        for side,s,close in [('l',1,cl),('r',-1,cr)]:
            for i in g.regions.get('brow_'+side,[]):
                v=key.data[i].co; inner=max(0,1-abs(v.x)/.11)
                v.z += brow*(.4+.6*inner)+asym*s
            for stem in ('upper_lid_','lower_lid_','upper_rim_','lower_rim_'):
                for i in g.regions.get(stem+side,[]):
                    v=key.data[i].co; cx=s*.061; cz=1.846
                    dx=v.x-cx; dz=v.z-cz
                    fall=max(0,1-abs(dx)/.038)
                    upper=stem.startswith('upper')
                    shift=(-.021 if upper else .010)*close*fall
                    v.z+=shift
                    v.y=-.182-.025*math.sqrt(max(.025,1-(dx/.030)**2-((v.z-cz)/.021)**2))-.005
            for stem in ('muzzle_','lip_','cheek_'):
                for i in g.regions.get(stem+side,[]):
                    v=key.data[i].co; outer=min(1,abs(v.x)/.07)
                    v.z+=snarl*(1-.35*outer)+smile*outer
                    v.x+=s*snarl*.12
            for i in g.regions.get('ear_'+side,[]): key.data[i].co.z-=max(cl,cr)*.012
        for region in ('jaw','beard','tongue','lower_teeth'):
            for i in g.regions.get(region,[]):
                v=key.data[i].co; v.z-=jaw; v.y+=jaw*.16
        for i in g.regions['mouth_web']:
            v=key.data[i].co;weight=max(0,min(1,(1.733-v.z)/.048))
            v.z-=jaw*weight;v.y+=jaw*.16*weight
    for i in g.regions.get('torso',[]):
        z=mesh.vertices[i].co.z
        for group in obj.vertex_groups: group.remove([i])
        positions=[('pelvis',1.0),('spine_01',1.13),('spine_02',1.29),('spine_03',1.45)]
        weights=[max(0,1-abs(z-h)/.18) for _,h in positions]; total=sum(weights)
        for (name,_),w in zip(positions,weights):
            if w: obj.vertex_groups[name].add([i],w/total,'REPLACE')
    return obj


def atlas(obj, out):
    """Same four-map atlas contract; surface-space restrained original patterns."""
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY',ngon_method='BEAUTY')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60),island_margin=.003,
                            area_weight=1.0,correct_aspect=True,scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh=obj.data;mesh.calc_loop_triangles();size=2048
    repaired=repair_uv_charts(mesh)
    maps={n:np.zeros((size,size,4),dtype=np.float32) for n in ('base_color','normal','orm','emissive')}
    for p in maps.values(): p[:,:,3]=1
    maps['normal'][:,:,:3]=(.5,.5,1); maps['orm'][:,:,:3]=(1,.7,0)
    coverage=np.zeros((size,size),dtype=bool);uv=mesh.uv_layers.active.data
    for tri in mesh.loop_triangles:
        pts=np.array([uv[i].uv[:] for i in tri.loops])*size
        low=np.maximum(np.floor(pts.min(axis=0)).astype(int),0)
        high=np.minimum(np.ceil(pts.max(axis=0)).astype(int),size-1)
        x,y=np.meshgrid(np.arange(low[0],high[0]+1)+.5,np.arange(low[1],high[1]+1)+.5)
        a,b,c=pts;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:continue
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;w=1-u-v
        inside=(u>=0)&(v>=0)&(w>=0)
        if not inside.any():continue
        iy,ix=np.nonzero(inside);yy=iy+low[1];xx=ix+low[0]
        coords=np.array([mesh.vertices[i].co[:] for i in tri.vertices])
        world=u[inside,None]*coords[0]+v[inside,None]*coords[1]+w[inside,None]*coords[2]
        wx,wy,wz=world.T
        part,color,metal,rough,emission=PALETTE[mesh.polygons[tri.polygon_index].material_index]
        rgb=np.array([int(color[k:k+2],16)/255 for k in (0,2,4)])
        noise=np.sin(wx*917+wy*413)*np.sin(wz*1097+wy*149)
        broad=np.sin(wx*39+wy*27)*np.cos(wz*47-wy*19)
        grain=.008;shade=np.ones_like(noise);nstrength=.006
        if part in ('fur','mane','mane_light','muzzle_fur','fur_shadow'):
            flow=np.sin(wx*820+np.sin(wz*21)*3+wy*150)
            shade=.94+.05*broad+.025*flow;grain=.015;nstrength=.015
        elif part=='ivory':
            vein=np.exp(-np.abs(np.sin(wx*53+np.sin(wz*31)*.4+wy*17))*65)
            shade=.99-.055*vein+.012*broad;grain=.005
        elif part=='gold': shade=.93+.025*broad;grain=.018;nstrength=.009
        elif part in ('fabric','glove','leather'):
            weave=np.sin(wx*1700)*np.sin(wz*1700)
            shade=.91+.025*weave+.035*broad;grain=.012;nstrength=.025
        elif part=='indigo': shade=.93+.04*broad;grain=.006
        encoded=np.clip(rgb[None,:]*(shade+grain*noise)[:,None],0,1)
        if part=='fur':
            # A smooth cream muzzle transition belongs to fur, never ceramic.
            cream=np.array([.831,.702,.525])
            mask=np.clip((-.17-wy)/.055,0,1)*np.clip((1.785-wz)/.04,0,1)*np.clip((.102-np.abs(wx))/.035,0,1)
            mask*=((wz>1.67)&(wz<1.8))
            encoded=encoded*(1-mask[:,None])+cream[None,:]*shade[:,None]*mask[:,None]
        maps['base_color'][yy,xx,:3]=encoded
        maps['orm'][yy,xx,:3]=np.stack([np.ones_like(noise),np.clip(rough+noise*.018+broad*.025,0,1),np.full_like(noise,metal)],axis=1)
        maps['normal'][yy,xx,0]=.5+noise*nstrength
        maps['normal'][yy,xx,1]=.5+np.cos(wz*1270+wx*170)*nstrength
        if emission:maps['emissive'][yy,xx,:3]=rgb
        coverage[yy,xx]=True
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
    images={};folder=out/'textures';folder.mkdir(parents=True,exist_ok=True)
    for name,pixels in maps.items():
        img=bpy.data.images.new('tex_solkael_v003_'+name,width=size,height=size,alpha=False)
        img.colorspace_settings.name='sRGB' if name in ('base_color','emissive') else 'Non-Color'
        img.pixels.foreach_set(pixels.ravel());img.filepath_raw=str(folder/(name+'.png'))
        img.file_format='PNG';img.save();img.pack();images[name]=img
    mat=bpy.data.materials.new('mat_solkael_lionheart_atlas_v003');mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=nodes.get('Principled BSDF');tex={}
    for name,img in images.items():
        tex[name]=nodes.new('ShaderNodeTexImage');tex[name].image=img;tex[name].label=name
    links.new(tex['base_color'].outputs['Color'],bsdf.inputs['Base Color'])
    norm=nodes.new('ShaderNodeNormalMap');links.new(tex['normal'].outputs['Color'],norm.inputs['Color']);links.new(norm.outputs['Normal'],bsdf.inputs['Normal'])
    sep=nodes.new('ShaderNodeSeparateColor');links.new(tex['orm'].outputs['Color'],sep.inputs['Color'])
    links.new(sep.outputs['Green'],bsdf.inputs['Roughness']);links.new(sep.outputs['Blue'],bsdf.inputs['Metallic'])
    links.new(tex['emissive'].outputs['Color'],bsdf.inputs['Emission Color']);bsdf.inputs['Emission Strength'].default_value=1.15
    mesh.materials.clear();mesh.materials.append(mat)
    for poly in mesh.polygons:poly.material_index=0
    return dict(size=[size,size],channels=list(images),material_count=1,island_margin=.003, repaired_uv_triangles=repaired,
                gutter_pixels=8,alpha=False,uv_method='Unique Smart Project 60 degrees, isolated folded triangles; triangulated source for stable curved charts')


def repair_uv_charts(mesh):
    """Isolate folded projection triangles into reserved, non-overlapping charts.

    Curved opaque lock tips can fold in a planar smart-project chart. Actual
    triangle islands replace those coordinates; the independent gate is unchanged.
    """
    from collections import defaultdict
    sys.path.insert(0,str(ROOT/'tools/validation'))
    from polish import area, intersection
    uv=mesh.uv_layers.active.data
    triangles=[[tuple(uv[i].uv) for i in tri.loops] for tri in mesh.loop_triangles]
    bins=defaultdict(list);bad=set()
    for i,tri in enumerate(triangles):
        if area(tri)<1e-14:bad.add(i);continue
        lo=[int(min(p[k] for p in tri)*128) for k in (0,1)]
        hi=[int(max(p[k] for p in tri)*128) for k in (0,1)]
        cells=[(x,y) for x in range(lo[0],hi[0]+1) for y in range(lo[1],hi[1]+1)]
        for j in {j for c in cells for j in bins[c]}:
            if intersection(tri,triangles[j])>1e-10:bad.update((i,j))
        for c in cells:bins[c].append(i)
    if not bad:return 0
    # 32px cells with 8px margins preserve the existing gutter policy.
    columns=64;rows=math.ceil(len(bad)/columns);strip=(rows*32+16)/2048
    assert strip<.2,'Unexpectedly widespread projection failure'
    for entry in uv:entry.uv.y=strip+entry.uv.y*(1-strip)
    for cell,i in enumerate(sorted(bad)):
        x=(cell%columns*32+8)/2048;y=(cell//columns*32+8)/2048
        coords=[(x,y),(x+16/2048,y),(x,y+16/2048)]
        for loop,point in zip(mesh.loop_triangles[i].loops,coords):uv[loop].uv=point
    return len(bad)


def animation_polish(rig,obj):
    """Add secondary weight to saved actions without changing timing/markers."""
    scene=bpy.context.scene
    for action in bpy.data.actions:
        rig.animation_data.action=action;frames=int(action.frame_end)
        # Sample first so newly inserted keys never feed later source evaluation.
        samples=[]
        for frame in range(frames+1):
            scene.frame_set(frame)
            samples.append({b.name:(b.rotation_quaternion.copy(),b.location.copy()) for b in rig.pose.bones})
        for frame,sample in enumerate(samples):
            scene.frame_set(frame);t=frame/frames;p=math.sin(math.pi*t)**2
            for b in rig.pose.bones:b.rotation_quaternion,b.location=sample[b.name]
            changes={'tail_02':((0,1,0),6*math.sin(math.tau*t)),
                     'tail_04':((1,0,0),5*math.sin(math.tau*t+.4)-5*math.sin(.4))}
            if action.name in ('attack_light','attack_heavy'):
                hit=.38 if action.name=='attack_light' else .5
                wind=math.sin(math.pi*t/hit)**2 if t<hit else 0
                recoil=math.sin(math.pi*(t-hit)/(1-hit))**2 if t>=hit else 0
                strength=1 if action.name=='attack_light' else 2
                # Both additions vanish exactly at contact; validated reach is kept.
                changes.update({'spine_01':((0,1,0),strength*(-4*wind+2*recoil)),
                                'spine_03':((0,0,1),strength*(6*wind-3*recoil)),
                                'head':((1,0,0),strength*(-2*wind+recoil))})
            elif action.name=='dodge':
                changes.update({'spine_02':((1,0,0),-13*p),'head':((0,0,1),-10*p),
                                'thigh_l':((1,0,0),-10*p),'shin_l':((1,0,0),18*p),
                                'thigh_r':((1,0,0),-8*p),'shin_r':((1,0,0),16*p)})
            elif action.name=='skill_cast':
                # Two forearms form a horizontal connected bulwark, chin above it.
                for side,s in [('l',1),('r',-1)]:
                    shoulder=Vector((s*.32,0,1.5))
                    elbow=Vector((s*.45,-.16,1.25)).lerp(Vector((s*.46,-.17,1.40)),p)
                    wrist=Vector((s*.32,-.24,1.60)).lerp(Vector((s*.09,-.35,1.44)),p)
                    base.point_bone(rig.pose.bones['upperarm_'+side],elbow-shoulder)
                    base.point_bone(rig.pose.bones['forearm_'+side],wrist-elbow)
                changes.update({'head':((1,0,0),-5*p)})
            elif action.name=='victory':
                changes.update({'spine_03':((1,0,0),-4*p),'head':((0,0,1),7*p),
                                'tail_01':((0,1,0),15*p)})
            elif action.name=='ko':
                settle=t*t*(3-2*t)
                for side,s in [('l',1),('r',-1)]:
                    for name,direction in [('upperarm_'+side,(-.22,-.20*s,.08)),
                                           ('forearm_'+side,(-.37,.05*s,-.02)),
                                           ('thigh_'+side,(-.40,.13*s,.08)),
                                           ('shin_'+side,(-.36,-.08*s,-.02))]:
                        bone=rig.pose.bones[name];original=bone.rotation_quaternion.copy()
                        base.point_bone(bone,direction)
                        bone.rotation_quaternion=original.slerp(bone.rotation_quaternion,settle)
                changes.update({'head':((0,0,1),-14*settle),
                                'tail_02':((0,1,0),-14*settle),
                                'tail_04':((1,0,0),9*math.sin(t*math.pi*3)*math.exp(-3*t))})
            for name,(axis,degrees) in changes.items():
                bone=rig.pose.bones[name]
                bone.rotation_quaternion=bone.rotation_quaternion @ Quaternion(axis,math.radians(degrees))
            for bone in rig.pose.bones:
                bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=bone.name)
        # Same evaluated-floor correction as v002; bone rest/root remain unchanged.
        for frame in range(frames+1):
            scene.frame_set(frame);bpy.context.view_layer.update()
            evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            low=min(Vector(v).z for v in evaluated.bound_box)
            bone=rig.pose.bones['pelvis'];bone.location.y-=low
            bone.keyframe_insert(data_path='location',frame=frame,group='pelvis')
    rig.animation_data.action=None
    for bone in rig.pose.bones:bone.matrix_basis.identity()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out-root',type=Path,default=ROOT)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert bpy.app.version[:2]==(5,2)
    source=BASELINE/'source/chr_solkael_lionheart_v002.blend'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA
    sys.path.insert(0,str(ROOT/'tools/art'))
    from reference_lock import production_references
    refs=production_references();assert len(refs)==8
    bpy.ops.wm.open_mainfile(filepath=str(source))
    rig=bpy.data.objects['HeroSkeleton'];old_obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    rig.animation_data.action=None
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    semantic=v2.geometry();g,provenance=retain_and_reshape(semantic,old_obj)
    old_mesh=old_obj.data;bpy.data.objects.remove(old_obj,do_unlink=True);bpy.data.meshes.remove(old_mesh)
    face(g);mane(g);body_and_armor(g);gauntlets(g)
    g=merge_facial_planes(g)
    obj=mesh_and_face(g,rig)
    out=args.out_root/'art/characters/solkael_lionheart/v003'
    textures=atlas(obj,out)
    animation_polish(rig,obj)
    manifest=json.loads((BASELINE/'solkael_asset.json').read_text(encoding='utf-8'))
    target=out/'source/chr_solkael_lionheart_v003.blend';target.parent.mkdir(parents=True,exist_ok=True)
    manifest.update(asset_version='v003',art_status='OWNER REVIEW REQUIRED',
        source=target.relative_to(args.out_root).as_posix(),mesh_vertices=len(g.vertices),
        textures=textures,palette=[dict(part=p[0],srgb='#'+p[1],metallic=p[2],roughness=p[3],emission_strength=p[4]) for p in PALETTE],
        baseline_source_sha256=SOURCE_SHA,baseline_provenance=provenance,
        morphology='v002-derived feline facial planes, curved lids, swept opaque mane, athletic-heavy limbs, layered integrated tower hardware',
        texture_policy='Four original procedural PBR maps; approved palette, no reference pixels')
    # Persist useful selection sets without adding runtime bone influences.
    obj['art_status']='OWNER REVIEW REQUIRED';rig['asset_version']='v003'
    bpy.context.scene['asset_stage']='v1.20 targeted v003 polish; OWNER REVIEW REQUIRED'
    base.save_json(out/'solkael_asset.json',manifest)
    validate_scene(manifest)
    bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA
    print('SOLKAEL_V003_SOURCE_PASS '+json.dumps(provenance),flush=True)


if __name__=='__main__':main()
