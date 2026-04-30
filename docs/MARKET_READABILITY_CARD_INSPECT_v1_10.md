# v1.10 — Market Readability + Card Inspect

## Obiettivo

Migliorare la leggibilità delle carte nel market senza cambiare bilanciamento, economia o combat.

La v1.10 parte da un problema pratico: nel market mobile il testo sulle carte è compatto, quindi il giocatore rischia di comprare senza capire bene effetto, costo, rami e meccaniche runtime.

## Modifiche principali

### Card inspect

Ogni carta shop ora mostra un piccolo pulsante `i`.

Toccandolo si apre un pannello dettaglio con:

- nome carta;
- rarità;
- costo;
- livello attuale / livello massimo;
- rami associati;
- testo effetto leggibile;
- testo legacy, se diverso;
- meccaniche runtime derivate da `effects`;
- pulsante acquisto diretto, quando possibile.

### Stati di acquisto

Le carte ora comunicano meglio il loro stato:

- carta comprabile;
- carta già acquistata nel round;
- carta a livello massimo;
- carta non acquistabile per gold insufficiente.

Se il player non ha abbastanza gold, la carta mostra quanti coins mancano.

### Drawer battle

Durante la battle il drawer resta consultabile, ma comunica chiaramente che il market è chiuso.

Il titolo passa a:

```text
CARTE · CONSULTAZIONE
```

con nota:

```text
Market chiuso durante la battle
```

## File modificati

```text
src/scenes/MarketScene.js
src/ui/fighter/OverlayUI.js
data/runtime.json
manifest.webmanifest
README.md
```

## Compatibilità

Questa patch è pensata per essere applicata sopra:

```text
v1.7 Runtime JSON + League Fix
v1.8 Arena Flow + Hero Draft
v1.9 Round Recap Overlay
```

Non modifica:

- `data/cards.json`;
- `data/heroes.json`;
- economia;
- league;
- combat;
- odds dello shop.

## Nota UX

Il click/tap sull'intera carta continua ad acquistare la carta.
Il tap sul pulsante `i` apre invece il dettaglio senza comprare.
