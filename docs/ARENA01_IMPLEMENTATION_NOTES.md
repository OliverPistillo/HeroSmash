# Arena01 Implementation Notes

## Render order

1. sky
2. mountains
3. back architecture
4. crystal core
5. combat floor
6. fighter shadows
7. fighters
8. combat FX
9. HUD

## Why only 5 layers?

The user-provided final set contains 5 usable layers. This is enough for a working 2.5D scene. The missing foreground props layer is optional but strongly recommended for occlusion depth.

## Coordinates

The source layer space is 2048×1152. The game canvas is 1366×768. The renderer scales design-space coordinates to runtime-space automatically.

Important anchors:

```json
{
  "baselineY": 846,
  "player": { "x": 770, "y": 846 },
  "enemy": { "x": 1278, "y": 846 }
}
```

Runtime canvas equivalent is approximately:

```json
{
  "baselineY": 564,
  "player": { "x": 513, "y": 564 },
  "enemy": { "x": 852, "y": 564 }
}
```

## Integration in Hero Smash custom engine

1. Copy `assets/arenas/arena01_beast_crucible/` into the game project.
2. Copy `data/arenas/` config files.
3. Copy `src/arena/ParallaxArena.js` and `src/arena/ArenaLoader.js`.
4. Load the arena in boot/preload.
5. In `CombatScene.draw`, call `arena.draw(...)` before drawing fighters/HUD.
6. Replace current circular arena background with `ParallaxArena`.

## Next ideal asset

Add:

```text
assets/arenas/arena01_beast_crucible/arena01_fg_props.png
```

This layer should contain side crystals, front braziers, vegetation and close stone edge details. It must be transparent PNG with real alpha.
