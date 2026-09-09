"""Blender 5.2 LTS: original one-bone cube pipeline fixture, never final hero art."""
from pathlib import Path
import json
import math
import bpy

ROOT = Path(__file__).resolve().parents[2]
assert bpy.app.version[:2] == (5, 2), f"Expected Blender 5.2 LTS; got {bpy.app.version_string}"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.data.orphans_purge(do_recursive=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.render.fps = 30
scene.frame_start, scene.frame_end = 1, 31
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
mesh = bpy.context.object
mesh.name = "foundation_cube"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
material = bpy.data.materials.new("foundation_teal")
material.diffuse_color = (0.06, 0.68, 0.62, 1)
material.use_nodes = True
bsdf = material.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = material.diffuse_color
bsdf.inputs["Metallic"].default_value = 0.15
bsdf.inputs["Roughness"].default_value = 0.55
mesh.data.materials.append(material)
bpy.ops.object.armature_add(location=(0, 0, 0))
rig = bpy.context.object
rig.name = "foundation_rig"
rig.data.bones[0].name = "root"
mesh.parent = rig
modifier = mesh.modifiers.new("foundation_skin", "ARMATURE")
modifier.object = rig
weights = mesh.vertex_groups.new(name="root")
weights.add(list(range(len(mesh.data.vertices))), 1.0, "REPLACE")
bone = rig.pose.bones["root"]
bone.rotation_mode = "XYZ"
for frame, angle in ((1, 0), (16, math.radians(12)), (31, 0)):
    bone.rotation_euler.y = angle
    bone.keyframe_insert(data_path="rotation_euler", frame=frame, group="root")
rig.animation_data.action.name = "idle"
scene.frame_set(1)
assert len(mesh.data.materials) == 1
assert len(rig.data.bones) == 1
assert tuple(mesh.location) == (0, 0, 0)
assert tuple(mesh.scale) == (1, 1, 1)
assert min(v.co.z for v in mesh.data.vertices) == 0
assert max(v.co.z for v in mesh.data.vertices) == 1
source = ROOT / "art/blender/shared/foundation_sample.blend"
export = ROOT / "art/exports/props/foundation_sample.glb"
source.parent.mkdir(parents=True, exist_ok=True)
export.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(export), export_format="GLB", export_animations=True,
                          export_skins=True, export_yup=True, export_apply=False)
report = dict(blender=bpy.app.version_string, source=source.relative_to(ROOT).as_posix(),
              export=export.relative_to(ROOT).as_posix(), units="meters", height=1,
              floor_origin=True, materials=1, bones=1, expected_animations=["idle"],
              textures=0, rights="original procedural project fixture", final_character=False)
out = ROOT / ".work/reports/blender_sample.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("FOUNDATION_BLENDER_PASS " + json.dumps(report))
