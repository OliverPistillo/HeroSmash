# Hero Smash — v1.9 Round Recap Overlay

## Obiettivo

Rendere il ritorno `battle → market` più informativo senza reintrodurre una schermata intermedia obbligatoria.

## Modifiche principali

- `CombatScene` salva `state.lastRoundRecap` dopo la risoluzione della league.
- `MarketScene` mostra automaticamente un recap compatto al rientro in preparation.
- Il recap si chiude automaticamente dopo pochi secondi oppure manualmente con `×`.
- Quando chiuso, resta disponibile un piccolo pulsante `Round Recap`.
- Il pannello laterale `ULTIMO ROUND` legge le statistiche dell'ultimo fight da `state.lastRoundRecap.recap`.

## Dati salvati nel recap

```js
state.lastRoundRecap = {
  round,
  result,
  victory,
  opponentName,
  opponentHero,
  hpLost,
  playerHp,
  gold,
  goldDelta,
  rank,
  aliveCount,
  recap,
  results,
  standings,
  seen
}
```

## Nota tecnica

`StandingsScene` non viene rimossa. Resta utile come fallback o schermata debug, ma il main loop resta diretto:

```text
Combat → Market in arena + Round Recap Overlay
```
