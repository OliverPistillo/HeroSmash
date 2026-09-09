# Foundation Blender → GLB → Godot spike

Existing Blender 5.2.1 LTS is used; expected series is 5.2 LTS. No Blender installation is performed by tooling.

```powershell
python -X utf8 tools/asset_pipeline/build_sample.py --blender 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe'
```

The build invokes `create_foundation_sample.py` with `--background --factory-startup --python-exit-code 1`. It creates an original 1-meter cube skinned to one bone, an `idle` pose animation, one opaque material and no textures. Blender Z-up exports to GLB Y-up; origin is at the floor. Source: `art/blender/shared/foundation_sample.blend`; export: `art/exports/props/foundation_sample.glb`.

`tools/validation/glb_check.py` validates container/buffer bounds, weights, joint index, 1m dimensions/origin, naming, actual animated rotation, material/texture counts. Only then is the runtime copy placed at `game/assets_runtime/props/foundation_sample.glb`; the provenance receipt records its SHA-256. Both GLBs must match exactly. This deliberate generated copy is necessary because Godot's resource root is `game/`.

Then run `foundation.py --godot <verified-executable>` to reimport and test the scene/skeleton/animation. Full commands are in `docs/qa/FOUNDATION_VALIDATION.md`.

This is a disposable pipeline fixture, not a final character, a final shared skeleton, or a final material/performance budget. Blender `.blend` bytes may contain save metadata and are not a deterministic binary fixture; GLB structure and provenance are validated. Blender 5.2 emits a forward-looking deprecation warning for `Material.use_nodes` (removal expected in 6.0); this does not invalidate the pinned 5.2 build.
