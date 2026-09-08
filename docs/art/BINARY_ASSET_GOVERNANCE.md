# Production binary governance v1

New admitted Solkael reference PNGs, editable Blender source and runtime GLB use
Git LFS. Git LFS 3.7.1 was already installed; only repository-local hooks/config
are initialized. Existing legacy/sample blobs and published history are untouched.
CI checkout explicitly hydrates LFS. A pointer file is not a usable asset: admission
validates hydrated bytes against SHA-256 and rejects missing objects/pointers.

The supplied eight-image Art Lock is immutable. Its manifest remains byte-identical;
new metadata lives in the central manifest's `production_items` collection. The
historical `items` and v1.18 review retain their unknown-rights status. Approval is
the owner's 2026-09-09 instruction, not filename inference. No unrelated art is admitted.

Source authority: `art/characters/solkael_lionheart/source/`. The authored build recipe
and editable `.blend` are versioned; the recipe records how to rebuild the initial
asset, while the exporter also accepts the saved source without regenerating it.
Runtime authority: `game/assets/characters/solkael_lionheart/`. Staging GLBs under
`art/characters/solkael_lionheart/exports/` are ignored and compared byte-for-byte
before publication to runtime. Godot never depends on a `.blend` file.

Keep backup `.blend1/.blend2`, caches, scratch renders, intermediate exports and
local raw video out of Git. Curated small screenshots/JSON remain ordinary Git.
Do not rewrite LFS history or remove a referenced binary to reduce repository size.
Before each asset commit run the binary manifest/hash checks; after push verify
`git lfs fsck` and a fresh clone/hydration. Record export metrics and content hashes.

No unmeasured mobile budget is asserted. Triangle, material, bone, morph, texture,
GLB and runtime costs are measured for this fighter and labeled by environment.
