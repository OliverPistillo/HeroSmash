# v1.7 — Runtime JSON + LeagueSystem Fix

## Obiettivo

Questa patch rimuove la copia statica dei dati gameplay dentro `src/game/GameData.js` e rende i file JSON in `data/` la fonte autorevole del runtime.

## Modifiche principali

- `src/game/GameData.js` ora è un loader leggero:
  - `data/runtime.json`
  - `data/branches.json`
  - `data/heroes.json`
  - `data/enemies.json`
  - `data/cards.json`
  - `data/economy.json`
  - `data/asset_manifest.json`
  - `data/asset_index.json`
  - `data/final_art.json`
  - `data/ui_assets.json`
- `BootScene` carica i dati prima di creare `GameState`.
- `GameState` rifiuta l’avvio se i dati non sono stati caricati.
- `LeagueSystem.resolveRound()` accredita correttamente il bot vincitore quando il player perde.
- In caso di vittoria del player, il bot sconfitto riceve correttamente loss, HP loss e income da sconfitta.
- `SaveSystem` usa la nuova key `hs_custom_v17` e migra automaticamente da `hs_custom_v07`.
- Versione UI/PWA normalizzata a `v1.7`.

## Nota operativa

Da ora in avanti, le modifiche a carte, hero, economy e branch vanno fatte nei JSON dentro `data/`. Non modificare `GameData.js` per cambiare il gameplay: quello è solo il rubinetto, non l’acqua.
