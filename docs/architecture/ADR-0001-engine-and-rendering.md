# ADR-0001 — Production Engine and Rendering

**Status:** Accepted  
**Date:** 2026-09-08

## Decision

Use:
- Godot 4.7.2 stable;
- typed GDScript;
- Godot Mobile renderer by default;
- Blender 5.2 LTS for 3D authoring;
- real-time 3D fighters;
- 2.5D hybrid 3D arenas.

## Context

The current repository is a capable JS/Canvas prototype, but the production requirement is now explicitly **real-time 3D characters**.

Keeping the Canvas runtime would require introducing a separate 3D web renderer and mobile packaging/performance complexity while preserving a custom engine surface that we would also need to maintain.

Godot is a better production fit for:
- mobile 3D;
- skeletal animation;
- scene authoring;
- camera/VFX integration;
- Android/iOS export;
- CLI/headless automation;
- direct glTF/Blender-friendly workflows.

## Consequences

Positive:
- natural real-time 3D pipeline;
- easier Blender integration;
- strong mobile/export tooling;
- agent-friendly text scripts/scenes and CLI;
- simpler route to native mobile builds.

Cost:
- current JS runtime logic must be migrated rather than reused directly;
- parity tests are required to avoid behavioral drift.

## Migration strategy

The JS prototype acts as a behavior oracle.

Port in this order:
1. canonical data;
2. deterministic simulation;
3. economy/market;
4. bot league;
5. presentation;
6. save/progression;
7. mobile packaging.

Do not port UI line-by-line.
Recreate behavior and visual intent in native Godot structures.
