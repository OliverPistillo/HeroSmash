# ADR-0002 — Blender → GLB → Godot Asset Pipeline

**Status:** Accepted  
**Date:** 2026-09-08

## Decision

Blender source files are authoring sources.
Validated GLB files are the primary interchange/runtime-import artifacts.

## Why GLB

- glTF 2.0 is the recommended Godot 3D exchange format.
- It supports skeletons, animation, materials and scene structure.
- It avoids depending on direct `.blend` import in every CI/runtime environment.
- It is straightforward to validate and regenerate.

## Source policy

Suggested source layout:

```text
art/blender/characters/<hero>/
art/blender/arenas/<arena>/
art/blender/shared/
```

Exports:

```text
art/exports/characters/<hero>.glb
art/exports/arenas/<arena>.glb
```

Godot runtime wrappers live under `game/`.

## Automation goals

A single command should eventually:
1. open/run Blender headlessly;
2. validate scale/origin/armature/naming;
3. export GLB;
4. validate expected animations/material limits;
5. trigger Godot import/check;
6. produce a machine-readable report.

## Character conventions to lock before bulk production

- units/scale;
- world forward axis;
- floor origin;
- skeleton naming;
- animation naming;
- animation event metadata;
- texture sizes;
- material count;
- weapon attachment sockets;
- VFX attachment sockets.

No bulk character generation before these conventions have a validated test fighter.
