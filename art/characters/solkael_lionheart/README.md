# Solkael first fighter source

Approved identity and production source: `docs/art/SOLKAEL_ART_LOCK.md` and the
eight hashed PNGs under `references/visual/characters/solkael_lionheart/production/`.
No old unknown-rights image is a source, mesh trace or texture.

`source/chr_solkael_lionheart_v001.blend` is editable Blender 5.2 LTS source in the
SOLKAEL_EXPORT collection: one HeroSkeleton, one skinned mesh, nine scalar PBR
materials, nine independent relative expression keys plus neutral, ten named
30-fps actions and action pose markers. The source opens in neutral T-pose; morph
values are explicitly zero. Rest matrices and all bones/sockets are in
`solkael_asset.json`. Five finger chains articulate the glove geometry; the shared
medium biped hierarchy is retained with mane, ears and four tail segments.

This initial original model uses solid geometric fur clumps and separate armored
forms. It is an editable first pipeline fighter, not a claim of final sculpt/texture
fidelity to the painted references. Scalar materials carry the approved palette;
there are no external textures, fur alpha cards or reference pixels in the GLB.
Per-face planar UVs support tangent generation; a future painted atlas needs its
own UV/art pass. No final mobile budget or final art sign-off is inferred.

Rebuild the initial authored geometry/rig/actions (overwrites this initial source):

```powershell
python tools/asset_pipeline/build_fighter.py --blender 'C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe'
```

Export a manually edited saved source without regenerating it:

```powershell
python tools/asset_pipeline/build_fighter.py --blender 'C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe' --export-existing
```

For isolated reconstruction add `--out-root .work/fighter-rebuild`. Source generation
never writes the reference images. Saved-source validation precedes export; the
independent GLB validator precedes runtime copy. The `.blend` container includes
Blender save/path metadata, so reconstruction compares the exact exported GLB and
source/rig/clip manifest rather than requiring identical `.blend` container bytes.
The saved committed `.blend` must independently export the same GLB.

Staging `exports/` is ignored. Only the runtime GLB under
`game/assets/characters/solkael_lionheart/` is tracked, via Git LFS. No `.blend` is
inside the Godot project. LOD generation is intentionally disabled for this first
measured mesh; first-fighter costs are not assumed to represent a complete arena.

Technical choices: 1.95 m skull-height proposal, 2.099 m crown/mane bounds, supporting
floor at zero, rest arms T-shaped, integrated towers, no sword/cape/separate shield.
KO floor alignment uses evaluated skinned bounds, with local pelvis movement and
immutable root. No action or pose marker applies damage.
