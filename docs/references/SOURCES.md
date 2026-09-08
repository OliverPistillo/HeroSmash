# Hero Smash — Source Registry

This file lists authoritative external sources and project-origin sources that Codex may consult.

## Official technical sources

### Godot

- Godot official release archive  
  https://godotengine.org/download/archive/  
  Purpose: pin stable engine versions.

- Godot release policy  
  https://docs.godotengine.org/en/stable/about/release_policy.html  
  Purpose: support window / upgrade decisions.

- Godot command-line tutorial  
  https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html  
  Purpose: headless test/export automation.

- Godot 3D formats / glTF import docs  
  https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html  
  Purpose: Blender/GLB pipeline.

### Blender

- Blender releases  
  https://www.blender.org/download/releases/  
  Purpose: production version pin.

- Blender 5.2 LTS  
  https://www.blender.org/releases/5-2/  
  Purpose: 3D production baseline.

### OpenAI / Codex

- Codex with ChatGPT plans / project instructions  
  https://help.openai.com/en/articles/11369540  
  Purpose: current Codex product workflow and `AGENTS.md`.

- Harness engineering: leveraging Codex in an agent-first world  
  https://openai.com/index/harness-engineering/  
  Purpose: repo knowledge-base design; short AGENTS + structured docs.

- Unrolling the Codex agent loop  
  https://openai.com/index/unrolling-the-codex-agent-loop/  
  Purpose: instruction hierarchy/context behavior.

## Product inspiration

### Dota Auto Gladiators

Steam Workshop page supplied by the project owner:
https://steamcommunity.com/sharedfiles/filedetails/?id=3147450491

Usage:
- mechanics/pacing/reference analysis only.

Do not:
- copy proprietary Dota 2 assets;
- copy names/characters;
- copy UI art;
- ship Valve/third-party copyrighted content.

## Hero Smash project sources

### GitHub

https://github.com/OliverPistillo/HeroSmash

Current baseline at foundation preparation:
`66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`

Role:
- current v1.14.3 behavior prototype;
- migration source;
- legacy project history.

### User legacy archive / old local project

Original local location reported by owner:
`C:\Users\olive\OneDrive\Desktop\Progetti\HeroSmash`

Role:
- old data;
- old card artwork;
- arena layers;
- branch artwork;
- hero/reference imagery;
- anthropomorphic hero roster;
- style/UI references.

## Source admission rule

The current v1.18 audit and source snapshot are under
`docs/references/visual/v1.18/`; the original v1.15 manifest remains historical.

When adding a new source, record:
- URL/path;
- owner/author;
- why it is needed;
- whether it is authoritative or reference-only;
- rights/license status if it contains reusable assets;
- date checked.

Do not treat search-engine summaries or random tutorial code as authoritative project sources.

## v1.18 verified sources (2026-09-08)

- `.work/legacy-source/hero.json.txt`: exact 20-candidate text source, supplied in
  project legacy material; author/owner and image-use rights unresolved. The byte
  snapshot and SHA are recorded in `visual/v1.18/source_provenance.json`.
- Named 20-candidate roster boards and `sheet sprite/Solkael.png`: local visual
  inspection only; stable IDs and limitations are in `visual/v1.18/review_decisions.json`.
  Useful direction does not establish a production license. Original external
  OneDrive archive was not accessed.
- [Godot model export considerations](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.html):
  Godot Engine documentation; technical source for model axes and export/rest
  conventions, not a project art source.
- [Godot skeleton retargeting](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html):
  Godot Engine documentation; technical source for BoneMap/rest compatibility.
- Existing local Godot `4.7.2.stable.official.ed1daf0bf` and Steam Blender
  `5.2.1 LTS` were detected again and exercised by foundation gates. Blender web
  manual fetch was unavailable; no unsupported claim about a new exporter release
  or installation is made. Shared pipeline values are explicit project contracts.

## v1.15 verified sources (2026-09-08)

- Production legacy copy: `.work/legacy-source/`, supplied by the project owner; read-only inventory source. External original path above was not accessed. `docs/migration/archive_inventory.csv` records all 1,152 physical files and SHA-256 hashes; visual rights are unknown and items remain reference-only.
- Godot official pinned release: https://godotengine.org/download/archive/4.7.2-stable/ and https://api.github.com/repos/godotengine/godot-builds/releases/tags/4.7.2-stable . Owner: Godot Engine project. Used only for official portable engine download and digest verification; engine license MIT. Version 4.7.2 verified locally; archive digest recorded in `docs/migration/ENVIRONMENT.md`.
- Godot command-line and glTF documentation listed above were checked for import/headless/renderer and GLB workflow; authoritative technical references, not project art sources.
- Blender installed executable: `C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe`, Blender Foundation distribution via Steam; `--version` reports 5.2.1 LTS. Existing tool used for procedural sample creation; no proprietary reference asset is consumed. Public Blender 5.2/docs web fetches were unavailable during this task; local executable/exporter output is the evidence of actual version and successful export.
