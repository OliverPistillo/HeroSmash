"""Export an existing validated Blender source; never regenerates/replaces its mesh."""
from pathlib import Path
import argparse
import json
import re
import sys
import bpy

ROOT=Path(__file__).resolve().parents[2]
HERO='solkael_lionheart'


def validate_scene():
    assert bpy.app.version[:2]==(5,2)
    scene=bpy.context.scene
    assert scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1 and scene.render.fps==30
    rigs=[o for o in scene.objects if o.type=='ARMATURE']
    assert len(rigs)==1 and rigs[0].name=='HeroSkeleton'
    rig=rigs[0]
    family=json.loads((ROOT/'docs/art/rig_families.json').read_text())['families'][0]
    for name,parent in {**family['base_hierarchy'],**family['sockets']}.items():
        assert name in rig.data.bones,name
        b=rig.data.bones[name];assert (b.parent.name if b.parent else None)==parent,name
    meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==1
    for o in [rig,*meshes]:
        assert o.location.length<1e-7 and o.rotation_euler.to_matrix().is_identity and all(abs(s-1)<1e-7 for s in o.scale),o.name
    mesh=meshes[0]
    assert min(v.co.z for v in mesh.data.vertices)>=-.005
    assert max(v.co.z for v in mesh.data.vertices)>1.95
    assert all(re.fullmatch('mat_[a-z0-9_]+',m.name) for m in mesh.data.materials)
    for m in mesh.data.materials:
        assert m.use_nodes
        for node in m.node_tree.nodes:
            if node.type=='TEX_IMAGE':assert node.image and (node.image.packed_file or Path(bpy.path.abspath(node.image.filepath)).is_file())
    for vertex in mesh.data.vertices:
        assert vertex.groups and abs(sum(w.weight for w in vertex.groups)-1)<1e-5
        assert len(vertex.groups)<=4
    expected={c['name'] for c in json.loads((ROOT/'docs/art/animation_contract.json').read_text())['clips']}
    assert {a.name for a in bpy.data.actions}==expected
    assert {k.name for k in mesh.data.shape_keys.key_blocks}=={'Basis',*('expr_'+n for n in ['focused','aggressive','casting','pain_light','pain_heavy','stunned','victory','defeat','ko'])}
    basis=mesh.data.shape_keys.key_blocks[0]
    for key in mesh.data.shape_keys.key_blocks[1:]:
        assert key.value==0 and key.relative_key==basis,'Non-neutral or cumulative expression source'
        assert .001<max((a.co-b.co).length for a,b in zip(key.data,basis.data))<.05,'Excessive/empty face morph'
    original_action=rig.animation_data.action
    for action in bpy.data.actions:
        rig.animation_data.action=action
        assert int(action.frame_start)==0 and action.frame_end>0
        for frame in range(int(action.frame_end)+1):
            scene.frame_set(frame)
            root=rig.pose.bones['root']
            assert root.location.length<1e-6 and root.rotation_quaternion.angle<1e-5,action.name
    rig.animation_data.action=original_action
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    scene.frame_set(0)
    return rig,mesh


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    bpy.ops.wm.open_mainfile(filepath=str(a.source.resolve()))
    rig,mesh=validate_scene()
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True)
    bpy.context.view_layer.objects.active=rig
    a.output.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(a.output.resolve()),export_format='GLB',use_selection=True,
        export_yup=True,export_apply=False,export_skins=True,export_morph=True,
        export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,
        export_frame_step=1,export_optimize_animation_size=True,export_cameras=False,export_lights=False,
        export_extras=True,export_anim_single_armature=True)
    print('SOLKAEL_EXPORT_PASS '+str(a.output))


if __name__=='__main__':main()
