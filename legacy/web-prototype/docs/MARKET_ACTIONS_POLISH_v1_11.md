# Hero Smash v1.11 — Market Actions Polish + Card Collection UX

Questa milestone migliora la leggibilità delle azioni economiche del market senza cambiare bilanciamento, combat o dati carte.

## Obiettivi

- Rendere immediato cosa costa ogni azione.
- Evitare click/tap ambigui tra acquisto e consultazione.
- Portare `Random Card`, `Undo`, `Lock` e `Collection` dentro una bottom bar coerente.
- Rendere la collection una vista di sola consultazione, senza vendita carte.

## Novità implementate

### Bottom action bar

La barra inferiore ora espone:

- `REROLL` con costo e stato disabled se mancano coins;
- `RANDOM` con costo e controllo pool disponibile;
- `CARTE` per aprire la collection posseduta;
- `UNDO` se esiste un acquisto annullabile;
- `LOCK` con stato leggibile;
- `FIGHT!` come CTA principale.

### Collection panel

Il pannello collection mostra fino a 12 carte per pagina con:

- nome carta;
- rarità;
- livello posseduto;
- rami;
- livello, rarità e rami;
- nessun pulsante di vendita.

Regola di gameplay: le carte acquistate non possono essere vendute. La collection serve solo a consultare la build.

### Feedback economico

Le toast ora indicano meglio:

- costo speso per reroll/random;
- carta ottenuta da random;
- refund ottenuto da undo;
- coins mancanti se non puoi pagare.

## File principali

```text
src/scenes/MarketScene.js
src/game/GameState.js
src/game/GameData.js
data/runtime.json
manifest.webmanifest
README.md
```

## Nota UX

La vendita è disabilitata. Su mobile il rischio peggiore non è un click in più: è distruggere una run con un tap sbagliato. Quindi: niente vendita, punto.
