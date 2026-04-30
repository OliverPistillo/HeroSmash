# Hero Smash v1.8 — Arena Flow + Hero Draft

## Obiettivo

Ridurre le schermate intermedie e trasformare la run in un ciclo continuo dentro l'arena.

## Modifiche principali

- Branch draft generato prima della scelta hero.
- Hero Select trasformata in Hero Draft:
  - 3 hero random;
  - filtrati in base ai rami attivi;
  - 2 reroll totali;
  - reroll per singolo slot.
- Hero data aggiornata con `favoredBranches` massimo 2.
- Bot AI aggiornata per preferire entrambi i rami favoriti.
- Combat parte con card drawer chiuso.
- Drawer durante combat apribile manualmente e view-only.
- Fine combat: ritorno diretto al MarketScene, senza StandingsScene obbligatoria.
- MarketScene riapre il drawer e rigenera shop se non lockato.

## File principali

```text
data/heroes.json
data/runtime.json
src/game/GameState.js
src/game/BotSystem.js
src/scenes/HomeScene.js
src/scenes/HeroSelectScene.js
src/scenes/CombatScene.js
src/ui/HeroView.js
src/ui/fighter/OverlayUI.js
manifest.webmanifest
README.md
```

## Nota su StandingsScene

`StandingsScene` resta disponibile nel codice come scena consultiva/futura, ma non viene più usata nel flow principale post-combat.
