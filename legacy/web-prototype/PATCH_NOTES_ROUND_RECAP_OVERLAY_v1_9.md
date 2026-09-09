# Patch Notes — Hero Smash v1.9 Round Recap Overlay

## Sintesi

Questa patch aggiunge un recap round compatto e non bloccante dopo ogni battle, mantenendo il ritorno diretto al market introdotto in v1.8.

## File modificati

- `src/scenes/CombatScene.js`
- `src/scenes/MarketScene.js`
- `src/game/GameState.js`
- `src/game/GameData.js`
- `data/runtime.json`
- `manifest.webmanifest`
- `README.md`

## File aggiunti

- `docs/ROUND_RECAP_OVERLAY_v1_9.md`
- `PATCH_NOTES_ROUND_RECAP_OVERLAY_v1_9.md`

## Comportamento atteso

1. Il combat finisce.
2. La league viene risolta.
3. `CombatScene` salva il riepilogo del round in `state.lastRoundRecap`.
4. Il gioco passa direttamente al market.
5. `MarketScene` mostra il recap per pochi secondi.
6. Il player può chiuderlo o riaprirlo senza interrompere il market.
