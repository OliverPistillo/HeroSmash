# Patch Notes — v1.12.4 Latest Market UI Fixes

## Correzioni principali
- Allinea il progetto reale caricato alla UI market più recente.
- Usa le nuove card frame:
  - comune single-branch
  - comune double-branch
  - epica
  - leggendaria
- Aggiunge nel manifest `ui_assets.json` le chiavi mancanti per le nuove card frame.
- Sposta il gold dal bottom bar al badge timer in alto.
- Rimuove il bottom gold panel e il relativo click handler.
- Usa il pannello blank per i rami bannati.
- Usa il recap pill asset per il recap compatto.
- Rimuove la seconda riga di icone branch dentro la text area della carta: le branch icon ora vivono nello slot alto della frame.

## File modificati
- `src/scenes/MarketScene.js`
- `data/ui_assets.json`
- `data/runtime.json`

## Asset inclusi
- tutti gli asset `assets/ui/market/*.png` necessari alla UI market attuale.
