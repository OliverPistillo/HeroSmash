# Asset Pipeline v1.1

## Obiettivo

Smettere di trattare gli asset come file sparsi e iniziare a gestirli come una pipeline.

## File generati

### data/asset_manifest.json
Manifest completo degli asset:
- cards
- heroes
- path
- hash
- exists/missing
- metadata utile

### data/asset_index.json
Indice semplificato per lookup rapido.

### Runtime v1.7
Il runtime non importa più manifest JS generati. `BootScene` carica direttamente `data/asset_manifest.json`, `data/final_art.json` e `data/ui_assets.json` tramite `src/game/GameData.js`.

## Tool

### Report

```bash
python3 tools/asset_pipeline.py report
```

### Validazione

```bash
python3 tools/asset_pipeline.py validate
```

Controlla:
- immagini mancanti
- id duplicati
- campi card obbligatori
- campi hero obbligatori

### Rigenerazione manifest

```bash
python3 tools/asset_pipeline.py manifest
```

### Placeholder mancanti

```bash
python3 tools/asset_pipeline.py placeholders
```

Crea SVG placeholder per asset mancanti.

## Fallback runtime

AssetManager ora non lascia buchi se manca un'immagine:
- registra il fallimento
- genera un placeholder canvas
- mantiene il gioco funzionante

## Prossimi step

- compressione immagini
- atlas sprites
- build hash/cache busting
- editor JSON per carte
- anteprima web degli asset
