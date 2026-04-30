# v1.4 — Overlay UI + Collapsible Card Drawer

## Obiettivo

Rifare la UI in modo più vicino al mockup approvato:

- UI sovrapposta direttamente sulla fight scene
- classifica HP in un banner overlay a sinistra
- branch report in un banner overlay a destra
- market card drawer in basso, apribile/chiudibile
- drawer che si riapre automaticamente a ogni nuova fase di preparazione
- niente grandi pannelli laterali rigidi fuori dalla fight

## Nuovo comportamento drawer

- In `MarketScene` il drawer si apre sempre automaticamente all'ingresso della fase preparation.
- Con il bottone `Hide Cards` il giocatore può chiuderlo.
- Quando parte il fight il drawer viene chiuso per lasciare pulito il combat.
- In `CombatScene` resta disponibile un piccolo tab `Cards ▲` per riaprirlo manualmente.
- Al prossimo market/preparation viene riaperto automaticamente.

## Arena

Le immagini arena usate sono quelle fornite:

- `arena01_bg_sky.png`
- `arena01_bg_mountains.png`
- `arena01_mg_back_architecture.png`
- `arena01_mg_crystal_core.png`
- `arena01_fg_combat_floor.png`

Sono state copiate dentro:

```text
assets/arenas/arena01_beast_crucible/
```

## File principali modificati

```text
src/game/GameState.js
src/scenes/MarketScene.js
src/scenes/CombatScene.js
src/ui/fighter/OverlayUI.js
src/ui/fighter/MarketCardFrame.js
data/arenas/arena01_beast_crucible.json
```
