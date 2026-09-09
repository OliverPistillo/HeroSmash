# v1.18 reference audit

`reference_inventory.json` is the current review/rights catalog. The original
`../reference_manifest.json` remains the frozen v1.15 census for preservation gates.
`reference_duplicates.json` records all grouped origins and explicitly excluded QA
screenshots. `review_decisions.json` is the authored visual-review overlay; rebuild
the two generated reports with `python tools/art/reference_lock.py`.

The census covers 832 origins in 534 canonical-content groups. 202 historical SVG
groups differ only between recorded Windows checkout bytes and Git/archive bytes;
their historical IDs and working hashes remain visible. The 286 consolidated
duplicate groups have 298 extra origins. This is not a claim that all historical
working files were byte-identical. No image was copied, moved, deleted or edited.

All 534 groups have `unknown-rights`. A filename mentioning ChatGPT/Gemini/DALL-E
suggests a tool but does not prove account ownership, prompt provenance or rights
in included source material. Zero images are admitted to production. Six reviewed
images are `direction-selected`: limited internal planning approval under the
current task, not clearance to trace, texture, ship or redistribute their pixels.
No image is asserted to be Valve-owned merely from visual resemblance; any proven
Dota/Valve or similar proprietary material must be `third-party-reference-only`
or `prohibited-for-production`, never production-usable without an explicit license.

38 significant boards were visually inspected (named full-roster boards and the
primary Solkael sheet additionally at source resolution). Remaining procedural
cards, UI slices and numbered legacy imagery are inventoried and conservatively
classified, not claimed to have passed detailed art review. The manifest exposes
that distinction. No unreviewed image receives direction selection.

`hero_candidates.source.json` is an exact byte snapshot of the local read-only
`hero.json.txt`, retained so roster validation works in a clean checkout without
the archive. Its hash, path and limits are in `source_provenance.json`. It is a
legacy concept source, not a runtime hero dataset. All 20 records are preserved.

Reference packets are incomplete for every hero. Named roster boards supply
partial neutral, palette and 3/4-front direction; they do not supply orthographic
turnarounds, isolated silhouettes, expression sheets or consistent weapon sockets.
The per-hero gap matrix is authoritative for production entry. An artist must first
establish rights/independent original design and complete that packet in v1.19.
