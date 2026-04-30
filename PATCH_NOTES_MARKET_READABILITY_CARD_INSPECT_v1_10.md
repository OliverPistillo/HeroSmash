# Patch Notes — v1.10 Market Readability + Card Inspect

## Aggiunto

- Pulsante `i` sulle carte del market.
- Pannello dettaglio carta leggibile.
- Acquisto diretto dal pannello dettaglio.
- Lista delle meccaniche runtime della carta.
- Indicatore di gold mancante sulle carte non acquistabili.
- Highlight visivo sulla carta selezionata.
- Drawer battle più chiaro: market chiuso, carte solo consultazione.

## Modificato

- `MarketScene.js` gestisce inspect card e stati di acquisto più leggibili.
- `OverlayUI.js` aggiorna il drawer carte durante la battle.
- `runtime.json`, `manifest.webmanifest` e `README.md` aggiornati a v1.10.

## File da sostituire

```text
HeroSmash-v1.7/README.md
HeroSmash-v1.7/manifest.webmanifest
HeroSmash-v1.7/data/runtime.json
HeroSmash-v1.7/src/scenes/MarketScene.js
HeroSmash-v1.7/src/ui/fighter/OverlayUI.js
```

## File da aggiungere

```text
HeroSmash-v1.7/docs/MARKET_READABILITY_CARD_INSPECT_v1_10.md
HeroSmash-v1.7/PATCH_NOTES_MARKET_READABILITY_CARD_INSPECT_v1_10.md
```

## Da testare manualmente

1. Avviare una nuova run.
2. Entrare nel market.
3. Toccare `i` su una carta.
4. Chiudere il pannello con `×`.
5. Comprare dal pannello dettaglio.
6. Verificare carta già acquistata.
7. Spendere gold e verificare indicatore `Mancano X`.
8. Andare in battle e aprire `Cards`.
9. Verificare che il drawer dica che il market è chiuso.
