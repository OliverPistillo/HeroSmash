# v1.3 — Fighter UI + Arena01 2.5D Integration

## Obiettivo

Integrare i due nuovi pacchetti ricevuti senza perdere le funzioni già implementate nelle milestone precedenti.

## Pacchetti integrati

### 1. HeroSmash_Arena01_2_5D_Runtime

Contenuto integrato:

- `assets/arenas/arena01_beast_crucible/`
- `data/arenas/arena01_beast_crucible.json`
- `data/arenas/arena_manifest.json`
- `src/arena/ArenaLoader.js`
- `src/arena/ParallaxArena.js`
- `tools/validate_arena_assets.py`
- `docs/ARENA01_IMPLEMENTATION_NOTES.md`

Usato in:

- `src/scenes/CombatScene.js`

### 2. HeroSmash_CustomEngine_FighterUISystem

Contenuto integrato:

- tutti i componenti `src/ui/fighter/`
- asset `fighter_ui_sheet`
- asset `art_bible`
- styling fighter UI in Combat e Market

Usato in:

- `HomeScene`
- `HeroSelectScene`
- `BranchDraftScene`
- `MarketScene`
- `CombatScene`

## CombatScene

La scena combat ora usa:

- `FighterHealthBar` per player/enemy
- `RoundTimer` centrale
- `CombatBanner` per Round Start / Fight / Victory / Defeat
- `LeaguePanel`
- `EvolutionPanel`
- `FighterButton`
- `StatusIconBar`
- `ParallaxArena`

La logica di combat non è stata sostituita da una demo: resta `CombatSystem.js`.

## MarketScene

La scena market ora usa:

- `FighterButton`
- `LeaguePanel`
- `BranchProgressPanel`
- `EvolutionPanel`
- `MarketCardFrame`
- `RoundTimer`

La logica market non è stata rimossa:

- acquisto
- vendita
- undo
- lock
- reroll
- random card
- preview card
- probability info
- branch threshold preview

## Limiti attuali

- gli hero non sono ancora sprite sheet animati
- le animazioni intro/victory/KO non sono ancora sequenze 2.5D
- il foreground props layer dell'arena manca ancora
- branch/UI sheet non sono ancora slicati in asset atomici

## Prossimo step

`v1.4 — Sprite Sheet Pipeline + Intro / KO / Victory Animations`
