# v1.5 — Legacy Deck Exact Import

## Obiettivo

`deck.json` è ora la fonte autorevole per le carte del gioco. La build usa **esattamente le 150 carte** del vecchio deck, senza inventare nuove tipologie e senza scartare carte.

## Risultato import

| Voce | Valore |
|---|---:|
| Carte importate | 150 |
| ID legacy | 1–150 |
| Normali | 90 |
| Epiche | 36 |
| Leggendarie | 24 |
| Carte monoramo | 84 |
| Carte bi-ramo | 66 |

## Dati preservati

Per ogni carta sono stati preservati:

- `legacyId`
- `name`
- `rarity`
- `branch`
- `cost`
- `effect` originale, salvato in `desc` e `legacyEffect`
- `levels`
- path Godot originali in `legacyImageCard` e `legacyImageBackground`

## Normalizzazioni applicate

- `Normal` → `Normale`
- `Epic` → `Epica`
- `Legendary` → `Leggendaria`
- branch TitleCase → id lowercase del motore
- branch scritti in una singola stringa, tipo `"Essence, Rage"`, convertiti in array pulito
- typo legacy `Guadian` corretto in `guardian`

## Runtime assets

I path Godot originali non sono direttamente utilizzabili dal browser. Perciò la build genera placeholder SVG runtime-safe:

```text
assets/cards/legacy_001.svg
...
assets/cards/legacy_150.svg
```

Quando avremo le immagini finali, basterà sostituire questi file o aggiornare `image` in `data/cards.json`.

## Effetti gameplay

L’effetto testuale originale è mantenuto. Inoltre è stata generata una prima mappatura numerica conservativa per il combat system attuale, usando:

- branch della carta
- rarità
- parole chiave nell’effetto legacy

Questo rende tutte le carte giocabili subito, ma la mappatura è una **prima passata**: gli effetti più complessi del vecchio deck andranno implementati uno per uno nel combat engine.

## File generati

```text
data/cards.json
data/legacy_deck_source.json
data/legacy_deck_import_report.json
data/branch_logos_legacy.json
tools/import_legacy_deck.py
```

## Comandi utili

```bash
python3 tools/import_legacy_deck.py data/legacy_deck_source.json
python3 tools/asset_pipeline.py validate
python3 tools/asset_pipeline.py report
```
