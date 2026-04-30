# Hero Smash — Project Brief Aggiornato per Collaboratori

**Versione documento:** 1.12  
**Stato progetto:** Prototype avanzato / Custom Engine web mobile landscape  
**Build di riferimento:** `HeroSmash_CustomEngine_v1_12_MarketUIReskin`  
**Ultima milestone integrata:** `v1.12 — Market UI Reskin`  
**Prossima milestone consigliata:** `v1.13 — Shop Odds + Economy Feedback Pass`

---

## 1. Elevator pitch

**Hero Smash** è un auto-battler mobile in landscape dove il giocatore sceglie un hero, costruisce una build tramite carte e rami sinergici, affronta una league da 8 partecipanti e sopravvive round dopo round.

La parte strategica avviene nel **market**: il giocatore compra carte, costruisce sinergie, gestisce economia, interessi, streak, soglie ramo e shop RNG.

La parte spettacolare avviene nel **combat automatico**: i fight vengono presentati come duelli arcade/fighting game, con HUD sovrapposta alla scena, arena 2.5D, banner dinamici, status leggibili, effetti e recap.

La frase secca:

> **Hero Smash è un auto-battler con cervello da strategico e faccia da arcade fighter.**

---

## 2. Stato aggiornato della build

La build corrente è:

```text
HeroSmash_CustomEngine_v1_12_MarketUIReskin
```

Questa build mantiene tutto ciò che era già stato integrato:

- Custom Engine
- layout landscape
- PWA manifest base
- Hero Draft iniziale con 3 hero random compatibili
- Branch draft generato prima della scelta hero
- Market completo
- Bot League 8 player
- Combat automatico
- Combat readability
- Final Art Integration
- Fighter UI System
- Overlay UI con drawer carte
- Arena01 Beast Crucible 2.5D Runtime
- Asset pipeline
- local save

E aggiunge le correzioni runtime:

```text
v1.8 — Arena Flow + Hero Draft
```

La base tecnica introdotta in v1.7 resta fondamentale:  **i JSON in `data/` sono la fonte autorevole caricata al runtime**. `src/game/GameData.js` non contiene più una copia enorme dei dati: carica `cards.json`, `heroes.json`, `branches.json`, `enemies.json`, `economy.json` e i manifest asset JSON al boot.

La v1.8 cambia invece il flow di gameplay:

- i rami attivi/bannati vengono generati **prima** della scelta hero;
- ogni hero può avere massimo **2 rami favoriti** tramite `favoredBranches`;
- all'inizio della run vengono mostrati solo **3 hero random compatibili** con i rami attivi;
- il player ha **2 reroll totali** per sostituire hero nei singoli slot;
- la battle parte con il drawer carte chiuso;
- il drawer/market durante battle è apribile manualmente ma resta view-only;
- dopo il combat non si passa più dalla schermata Standings: si torna direttamente al market nell'arena;
- se lo shop non era lockato, vengono generate nuove carte; se era lockato, le carte rimangono.
- dopo la battle appare un **round recap overlay** compatto e non bloccante dentro il market;
- il recap mostra risultato, avversario, HP persi/inflitti, gold ottenuto, rank e danni principali dell'ultimo fight;
- la classifica resta consultabile nei pannelli laterali, senza forzare una schermata Standings intermedia.


## v1.12 — Market UI Reskin

La v1.12 rifà la schermata **Market / Preparation** seguendo la reference fornita come blueprint di layout: classifica a sinistra, timer round centrale in alto, tre carte shop dominanti al centro, pannelli rami/statistiche/hero a destra e action bar in basso.

Nota importante: la patch replica **struttura, proporzioni, gerarchia e feeling visivo**, ma usa elementi originali Hero Smash e non clona asset o dettagli proprietari della reference.

### Cambiamenti principali

- timer round centrale trasformato in badge arcade/fantasy più dominante;
- leaderboard spostata e proporzionata come colonna laterale sinistra;
- tre carte shop più grandi e più centrali;
- pannelli laterali destri riorganizzati per branch, ultimo round e hero;
- action bar inferiore ridisegnata:
  - Reroll a sinistra;
  - Gold al centro;
  - Lock a destra;
  - Ready/Fight come CTA principale;
  - Random, Carte e Undo come utility pill secondarie;
- shop toggle riposizionato sopra le carte per non interferire con la barra inferiore;
- stile più marcato: vetro scuro, bordi bevel/slanted, glow blu/oro/viola e cornici carte più pesanti.

### Regola confermata

Le carte acquistate **non sono vendibili**. La collection resta solo consultazione build.

---

## 3. Avvio del progetto

Dalla cartella del progetto:

```bash
python3 tools/serve.py
```

Poi aprire:

```text
http://127.0.0.1:8000
```

Il server locale serve perché il progetto usa moduli JavaScript ES. Aprire direttamente `index.html` può non funzionare correttamente.

---

## 4. Filosofia attuale

Il progetto non usa Godot, Unity o Unreal.  
La build attuale è un **mini-engine custom web/mobile** basato su:

- JavaScript ES Modules
- Canvas 2D
- rendering landscape 1366×768
- dati JSON
- asset SVG/PNG
- arena runtime 2.5D a layer
- PWA manifest base
- salvataggio locale via `localStorage`

Questa scelta permette iterazione rapida su:

- UI mobile;
- market;
- card system;
- combat automatico;
- bot league;
- asset pipeline;
- presentazione 2.5D;
- future sprite sheet animation.

---

## 5. Struttura principale delle cartelle

```text
HeroSmash/
  index.html
  manifest.webmanifest

  src/
    engine/
      AssetManager.js
      Renderer.js
      Input.js
      SceneManager.js
      Audio.js
      SaveSystem.js
      Particles.js

    game/
      GameData.js
      GameState.js
      EconomySystem.js
      BranchSystem.js
      CardSystem.js
      CombatSystem.js
      BotSystem.js
      LeagueSystem.js
      RunSystem.js

    arena/
      ArenaLoader.js
      ParallaxArena.js

    scenes/
      BootScene.js
      HomeScene.js
      HeroSelectScene.js
      BranchDraftScene.js
      MarketScene.js
      CombatScene.js
      StandingsScene.js
      SummaryScene.js

    ui/
      Button.js
      CardView.js
      HeroView.js
      ProgressBar.js
      ArtScene.js

      fighter/
        FighterTheme.js
        FighterHealthBar.js
        RoundTimer.js
        StatusIconBar.js
        CombatBanner.js
        LeaguePanel.js
        EvolutionPanel.js
        BranchProgressPanel.js
        MarketCardFrame.js
        FighterButton.js
        OverlayUI.js

  data/
    heroes.json
    cards.json
    branches.json
    enemies.json
    economy.json
    asset_manifest.json
    asset_index.json
    final_art.json
    legacy_deck_source.json
    legacy_deck_import_report.json
    branch_logos_legacy.json

    arenas/
      arena_manifest.json
      arena01_beast_crucible.json

  assets/
    cards/
      legacy_001.svg
      ...
      legacy_150.svg

    heroes/
    fx/
    ui/

    final/
      backgrounds/
      ui/
      style/

    arenas/
      arena01_beast_crucible/
        arena01_bg_sky.png
        arena01_bg_mountains.png
        arena01_mg_back_architecture.png
        arena01_mg_crystal_core.png
        arena01_fg_combat_floor.png

  tools/
    serve.py
    asset_pipeline.py
    combat_readability_check.py
    validate_arena_assets.py
    import_legacy_deck.py

  docs/
    COMBAT_READABILITY_v1_1.md
    ASSET_PIPELINE_v1_1.md
    FINAL_ART_INTEGRATION_v1_2.md
    FIGHTER_UI_ARENA01_INTEGRATION_v1_3.md
    OVERLAY_UI_CARD_DRAWER_v1_4.md
    LEGACY_DECK_EXACT_IMPORT_v1_5.md
    ARENA01_IMPLEMENTATION_NOTES.md
```

---

## 6. Core game loop

Il loop attuale è:

1. **Home**
   - schermata iniziale;
   - profilo locale;
   - avvio nuova run.

2. **Hero Select**
   - scelta tra 16 hero;
   - ogni hero ha stats, skill e ramo favorito.

3. **Branch Draft**
   - il sistema seleziona 8 rami attivi su 12;
   - i 4 rami esclusi non producono carte nella run.

4. **Market / Preparation**
   - acquisto carte;
   - reroll;
   - random card;
   - lock shop;
   - consultazione collection;
   - undo ultimo acquisto;
   - preview soglie ramo;
   - gestione economia;
   - card drawer aperto automaticamente.

5. **Combat**
   - fight automatico;
   - player contro bot;
   - combat system frame-by-frame;
   - HUD overlay;
   - Arena01 2.5D runtime;
   - status, danni, skill, shield, crit, DoT.

6. **Standings**
   - risultati round;
   - classifica league;
   - HP rimanenti;
   - eliminazioni.

7. **Repeat**
   - nuovo market;
   - nuovo fight;
   - fino a fine run o eliminazione.

8. **Summary**
   - riepilogo finale;
   - rank;
   - build;
   - danni;
   - carte;
   - coins.

---

## 7. Player HP / Run HP

Ogni run parte con:

```text
HP Run = 100
```

Quando il giocatore perde un fight, perde HP run.

La quantità persa dipende da:

- livello/potenza dell’avversario;
- round;
- streak di vittorie precedente;
- scaling interno della run.

Se gli HP run arrivano a 0, il player è eliminato.

---

## 8. League a 8 giocatori

Il gioco implementa una **Bot League**:

- 1 player umano;
- 7 bot;
- ogni partecipante ha hero, HP, gold, build, card levels, win/loss streak e stats;
- i bot vengono accoppiati round-by-round.

### Match player vs bot

Usano il combat system completo.

### Match bot vs bot

Sono simulati tramite power score per mantenere performance e semplicità.

### Da migliorare

I bot oggi funzionano, ma devono diventare più intelligenti:

- archetipi bot;
- strategia economy;
- strategia reroll;
- forcing rami;
- gestione lock shop;
- lock shop;
- adattamento se stanno perdendo;
- counter-build.

---

## 9. Hero system

Attualmente sono previsti 16 hero.

Ogni hero ha:

- `id`
- `name`
- `title`
- `icon`
- `color`
- `favoredBranch`
- `stats`
- `skill`
- `image`

Esempio stats:

```json
{
  "hp": 930,
  "atk": 26,
  "arm": 7,
  "focus": 30,
  "spd": 0.94,
  "crit": 0.11,
  "critD": 1.5,
  "regen": 10,
  "dodge": 0.09
}
```

| Stat | Descrizione |
|---|---|
| `hp` | Vita massima in fight |
| `atk` | Danno fisico base |
| `arm` | Riduzione danno fisico |
| `focus` | Potenza skill/magia |
| `spd` | Velocità attacchi |
| `crit` | Probabilità critico |
| `critD` | Moltiplicatore critico |
| `regen` | Recupero energia |
| `dodge` | Probabilità schivata |

---

## 10. Skill system

Ogni hero ha una skill automatica.

Esempio:

```json
{
  "name": "Flame Duelist Art",
  "cd": 6,
  "energy": 45,
  "pow": 1.05,
  "type": "magic",
  "status": "burn",
  "dur": 3,
  "dot": 14
}
```

| Campo | Significato |
|---|---|
| `name` | Nome skill |
| `cd` | Cooldown |
| `energy` | Energia richiesta |
| `pow` | Moltiplicatore danno |
| `type` | `phys` o `magic` |
| `status` | Status applicato |
| `dur` | Durata status |
| `dot` | Danno nel tempo |

---

## 11. Branch system

Il gioco ha 12 rami totali.  
A ogni run ne vengono scelti casualmente 8 attivi e 4 bannati.

| Ramo | Tema |
|---|---|
| Wound | Amplifica i danni subiti dal nemico |
| Essence | Mana, skill power, magia |
| Rage | Attack speed, tempo, furia |
| Ice | Slow, freeze, stun |
| Toxin | DoT, poison stack |
| Shield | Barriere e riduzione danno |
| Healing | Cure e rigenerazione |
| Power | Burst e danno puro |
| Precision | Crit, execute, accuracy |
| Guardian | HP, armor, difesa |
| Assault | Danno fisico e pressione |
| Dodge | Schivata e counter |

### Soglie ramo

Ogni carta dà punti ramo.  
Le soglie attuali sono:

```text
4 / 10 / 20 / 40
```

Più punti ramo = tier più alto = bonus più forti.

---

## 12. Legacy Deck Exact Import

La milestone v1.5 ha importato il vecchio `deck.json` come **fonte autorevole esatta** delle carte.

Questo significa:

- nessuna carta inventata;
- nessuna carta rimossa;
- mantenuto l’esatto numero di carte;
- mantenute le tipologie originali;
- mantenuti gli ID legacy;
- mantenuto l’effetto testuale originale.

### Risultato import

| Voce | Valore |
|---|---:|
| Carte importate | 150 |
| ID legacy | 1–150 |
| Normali | 90 |
| Epiche | 36 |
| Leggendarie | 24 |
| Carte monoramo | 84 |
| Carte bi-ramo | 66 |

### Distribuzione rami

Ogni ramo appare **18 volte** nel deck importato.

| Ramo | Occorrenze |
|---|---:|
| Assault | 18 |
| Dodge | 18 |
| Essence | 18 |
| Guardian | 18 |
| Healing | 18 |
| Ice | 18 |
| Power | 18 |
| Precision | 18 |
| Rage | 18 |
| Shield | 18 |
| Toxin | 18 |
| Wound | 18 |

### Costi importati

| Costo | Carte |
|---:|---:|
| 100 | 90 |
| 200 | 35 |
| 300 | 25 |

### Max level importati

| Max level | Carte |
|---:|---:|
| 5 | 90 |
| 3 | 36 |
| 1 | 24 |

---

## 13. Dati preservati dal deck legacy

Per ogni carta sono stati preservati:

- `legacyId`
- `name`
- `rarity`
- `branch`
- `cost`
- `effect` originale
- `levels`
- `legacyImageCard`
- `legacyImageBackground`

L’effetto originale è salvato in:

```text
desc
legacyEffect
```

I vecchi path Godot sono mantenuti per riferimento, ma il browser usa placeholder SVG runtime-safe fino alla sostituzione con asset finali.

---

## 14. Normalizzazioni applicate al deck

Sono state applicate solo normalizzazioni tecniche necessarie:

| Legacy | Engine |
|---|---|
| `Normal` | `Normale` |
| `Epic` | `Epica` |
| `Legendary` | `Leggendaria` |
| `Wound` | `wound` |
| `Essence, Rage` | `["essence", "rage"]` |
| `Guadian` | `guardian` |

Correzioni importanti:

- branch scritti in una singola stringa sono stati convertiti in array pulito;
- typo legacy `Guadian` è stato corretto in `guardian`;
- nessuna anomalia bloccante rilevata;
- nessuna carta è stata scartata.

---

## 15. Runtime assets delle carte

I path Godot originali non sono direttamente utilizzabili dal browser.  
Perciò la build genera placeholder SVG runtime-safe:

```text
assets/cards/legacy_001.svg
...
assets/cards/legacy_150.svg
```

Questi placeholder sono temporanei.

Quando saranno disponibili le immagini finali delle carte, basterà:

1. sostituire i file SVG;
2. oppure aggiornare il campo `image` dentro `data/cards.json`;
3. rigenerare il manifest asset.

---

## 16. Effetti gameplay delle carte legacy

Gli effetti testuali originali sono preservati.

In più, è stata generata una prima mappatura numerica conservativa per il combat system attuale, usando:

- branch della carta;
- rarità;
- parole chiave nell’effetto legacy.

Questo permette alle 150 carte di essere giocabili subito.

### Nota importante

Gli effetti più complessi del vecchio deck non sono ancora implementati uno a uno.  
La mappatura attuale è una **prima passata di compatibilità**.

Esempi di effetti che richiedono implementazione specifica:

- “quando casti Essence, applica Ice”;
- “per ogni 400 HP persi...”;
- trigger condizionali;
- interazioni cross-branch;
- effetti delayed;
- conversioni tra stack;
- effetti su soglie specifiche;
- manipolazione dello shop o dell’economia.

Questa è una priorità della prossima milestone.

---

## 17. Card system attuale

Le carte nel runtime hanno campi modernizzati per il motore:

- `id`
- `legacyId`
- `name`
- `rarity`
- `branches`
- `points`
- `max`
- `cost`
- `weight`
- `unlock`
- `desc`
- `legacyEffect`
- `effects`
- `image`
- `legacyImageCard`
- `legacyImageBackground`

### Rarità e livelli

| Rarità | Max level | Costo tipico |
|---|---:|---:|
| Normale | 5 | 100 |
| Epica | 3 | 200 |
| Leggendaria | 1 | 300 |

### Regola importante

Da ora in poi il **deck non va espanso inventando carte nuove** senza aggiornare la fonte autorevole.  
Se una carta deve esistere, deve essere coerente con `deck.json` o con una sua futura versione approvata.

---

## 18. Market system

Il market è uno dei sistemi più completi già implementati.

### Funzioni disponibili

- shop con carte random;
- reroll;
- random card;
- lock shop;
- undo ultimo acquisto;
- collection carte in sola consultazione;
- modalità collezione;
- preview punti ramo;
- probabilità stimata della carta;
- evidenza soglia ramo;
- timer preparation;
- auto-ready a timer finito;
- card drawer apribile/chiudibile.

### Costi attuali

| Azione | Costo |
|---|---:|
| Reroll | 20 |
| Random Card | 100 |
| Carta Normale | 100 |
| Carta Epica | 200 |
| Carta Leggendaria | 300 |

### Collection

Le carte acquistate restano nella build della run. Non esiste vendita carte: la collection serve per consultare livelli, rarità e rami posseduti.

### Undo

L’undo annulla l’ultimo acquisto e restituisce il costo pagato.

---

## 19. Overlay UI e card drawer

La milestone v1.4 ha cambiato la direzione UI.

### Direzione corretta

La UI deve essere **sovrapposta alla fight scene**, non laterale o costruita attorno alla scena.

Elementi principali:

- top HUD compatto player/enemy;
- timer centrale;
- classifica HP in banner overlay a sinistra;
- branch report in banner overlay a destra;
- market card drawer in basso;
- bottone **Hide Cards / Cards**;
- il drawer si riapre automaticamente nella nuova fase di preparation.

### Regola UX

Durante il fight la scena deve restare pulita.  
Durante la preparation il drawer si apre automaticamente perché il giocatore deve interagire con le carte.

---

## 20. Economy system

La run parte con:

```text
300 coins
```

A fine round il player riceve income.

| Voce | Valore |
|---|---:|
| Base income | 300 |
| Interesse | +10 ogni 100 coins pre-match |
| Cap interesse | +100 |
| Vittoria | +50 |
| Win streak | +20 per streak |
| Cap win streak | +100 |
| Loss compensation | +15 per HP perso |
| Lose streak | +15 per streak |
| Cap lose streak | +60 |

Esempio:

```text
Pre-gold = 815
Interesse = +80
```

---

## 21. Combat system

Il combat è automatico e simulato frame-by-frame.

### Elementi implementati

- HP;
- energy;
- basic attack;
- skill cast;
- cooldown;
- crit;
- dodge;
- armor;
- shield;
- healing;
- DoT;
- wound amp;
- execute;
- slow/stun;
- multi-hit;
- status stack;
- combat recap;
- floating numbers;
- event log.

### Danni colorati

| Colore | Tipo |
|---|---|
| Bianco | Danno fisico |
| Viola | Magico / skill |
| Verde | DoT / Toxin |
| Azzurro | Shield |
| Giallo | Crit / skill pronta |
| Rosso | Danno subito / sconfitta |

### Recap finale

A fine fight vengono mostrati:

- danno fisico;
- danno magico;
- danno DoT;
- crit;
- cure;
- shield assorbito;
- schivate;
- danni subiti.

---

## 22. Combat readability

Sono già presenti:

- status icons sopra i combattenti;
- stack status;
- micro barra durata status;
- skill-ready indicator;
- pulse viola per skill cast;
- trail diversi per basic e skill;
- combat log live;
- pulsante Info con legenda;
- speed x1 / x2 / x3;
- slow motion finale.

### Fighter-style presentation

Sono stati introdotti:

- health bar top sinistra/destra;
- portrait hero;
- energy bar;
- timer centrale;
- banner Round Start;
- banner Fight;
- banner Victory / Defeat;
- league/classifica HP overlay;
- branch report overlay;
- drawer carte sovrapposto alla fight.

---

## 23. Fighter UI System

Il sistema Fighter UI è integrato nella build principale.

### Componenti

```text
src/ui/fighter/FighterTheme.js
src/ui/fighter/FighterHealthBar.js
src/ui/fighter/RoundTimer.js
src/ui/fighter/StatusIconBar.js
src/ui/fighter/CombatBanner.js
src/ui/fighter/LeaguePanel.js
src/ui/fighter/EvolutionPanel.js
src/ui/fighter/BranchProgressPanel.js
src/ui/fighter/MarketCardFrame.js
src/ui/fighter/FighterButton.js
src/ui/fighter/OverlayUI.js
```

### Funzione dei componenti

| Componente | Funzione |
|---|---|
| `FighterTheme` | palette, pannelli bevel, barre slanted, utility UI |
| `FighterHealthBar` | barra HP/energy stile arcade fighter |
| `RoundTimer` | timer centrale round |
| `StatusIconBar` | status icons con stack/durata |
| `CombatBanner` | Round Start / Fight / Victory / Defeat |
| `LeaguePanel` | classifica league laterale/overlay |
| `EvolutionPanel` | progresso build/evoluzione |
| `BranchProgressPanel` | progresso rami |
| `MarketCardFrame` | frame carte stile fighter |
| `FighterButton` | bottoni bevel/slanted |
| `OverlayUI` | nuova UI sovrapposta alla fight scene |

---

## 24. Arena01 Beast Crucible 2.5D Runtime

È stata integrata la prima arena runtime-ready:

```text
Arena01 — Beast Crucible
```

### File principali

```text
assets/arenas/arena01_beast_crucible/
  arena01_bg_sky.png
  arena01_bg_mountains.png
  arena01_mg_back_architecture.png
  arena01_mg_crystal_core.png
  arena01_fg_combat_floor.png

data/arenas/
  arena_manifest.json
  arena01_beast_crucible.json

src/arena/
  ArenaLoader.js
  ParallaxArena.js
```

### Funzioni integrate

- layer separati;
- parallax;
- camera drift;
- camera shake;
- crystal glow;
- crystal floating;
- dust FX ambientale;
- coordinate fighter/baseline;
- fallback se l’arena non carica.

### Limite attuale

Manca ancora un layer foreground props davanti ai fighter:

```text
arena01_fg_props.png
```

Questo migliorerebbe l’effetto 2.5D con occlusione frontale, cristalli, bracieri o vegetazione.

---

## 25. Final Art Integration

La milestone v1.2 è stata mantenuta.

### Asset final art inclusi

- home key art;
- market/preparation backdrop;
- combat backdrop;
- grand arena backdrop;
- hero select roster backdrop;
- branch icon sheet;
- UI asset sheet;
- style guide moodboard;
- fighter UI sheet;
- art bible.

### Cartelle

```text
assets/final/backgrounds/
assets/final/ui/
assets/final/style/
```

### Limiti attuali

Non sono ancora finali/atomici:

- portrait individuali per tutti gli hero;
- card illustration singole per tutte le carte;
- branch icon singole estratte dallo sheet;
- UI elements slicati;
- sprite sheet animati.

---

## 26. Asset pipeline

La pipeline asset attuale include:

- manifest asset;
- index asset;
- validazione;
- placeholder generation;
- fallback runtime;
- final art manifest;
- arena validation;
- legacy deck import.

### File principali

```text
data/asset_manifest.json
data/asset_index.json
data/final_art.json
data/legacy_deck_source.json
data/legacy_deck_import_report.json
data/branch_logos_legacy.json

data/runtime.json
data/ui_assets.json

# Nota v1.7: i vecchi manifest JS generati non sono più usati dal runtime.
```

### Tool

```bash
python3 tools/asset_pipeline.py report
python3 tools/asset_pipeline.py validate
python3 tools/asset_pipeline.py manifest
python3 tools/asset_pipeline.py placeholders
python3 tools/combat_readability_check.py
python3 tools/validate_arena_assets.py
python3 tools/import_legacy_deck.py data/legacy_deck_source.json
```

### Validazioni v1.5

La build v1.5 ha superato:

- sintassi JavaScript;
- asset pipeline validate;
- arena assets validate;
- asset manifest con 166 immagini e 0 mancanti.

---

## 27. Mobile UX

Implementato:

- layout landscape;
- rotate hint se in portrait;
- PWA manifest landscape;
- touch target grandi;
- input pointer con dx/dy;
- haptic feedback leggero;
- HUD pensato per 16:9;
- fighter UI pensata per mobile landscape;
- drawer carte collassabile.

Da migliorare:

- safe area notch avanzata;
- service worker;
- offline cache;
- install prompt;
- performance mobile reale;
- modalità low graphics;
- test su Android/iOS.

---

## 28. PWA / Mobile packaging

Attualmente il progetto è una web app/PWA base.

### Implementato

- `manifest.webmanifest`;
- landscape orientation;
- display fullscreen/standalone;
- theme/background color.

### Mancante

- service worker;
- caching assets;
- offline mode;
- app icons;
- splash screen;
- install prompt;
- cache busting;
- wrapper Android;
- APK test;
- iOS Safari test.

---

## 29. Salvataggio

Il sistema attuale usa:

```text
localStorage
```

Viene salvato:

- numero run;
- best round;
- best wins;
- total coins.

### Da migliorare

- save versioning;
- migrazione save;
- export/import save;
- impostazioni audio/haptic;
- tutorial completato;
- collezione;
- meta progression.

---

## 30. Audio

Attualmente esiste audio sintetico base tramite `AudioBus`.

### Implementato

- beep UI;
- feedback semplice su bottoni/eventi.

### Mancante

- musica menu;
- musica market;
- musica combat;
- SFX acquisto;
- SFX reroll;
- SFX lock;
- SFX crit;
- SFX shield;
- SFX toxin tick;
- SFX freeze/stun;
- SFX victory/defeat;
- settings audio.

---

## 31. Sprite sheet / 2.5D animation direction

Il progetto ora ha:

- arena 2.5D runtime;
- HUD fighter-style;
- overlay UI;
- combat system leggibile;
- banner dinamici;
- card drawer.

Manca ancora la parte animata vera degli hero.

### Prossima pipeline consigliata

Ogni hero dovrebbe avere sprite sheet per:

```text
idle
intro
attack_light
attack_heavy
skill_cast
hit_react
dodge
crit
ko
victory
loop_breathing
```

### Metadata esempio

```json
{
  "id": "fireheart_idle",
  "src": "assets/sprites/heroes/fireheart/idle.png",
  "frameWidth": 256,
  "frameHeight": 256,
  "frames": 12,
  "fps": 12,
  "loop": true
}
```

### Perché sprite sheet

Gli sprite sheet sono preferibili ai video per il combat perché:

- pesano meno;
- sono più controllabili;
- si possono interrompere o loopare;
- permettono timing con hit/skill;
- funzionano meglio su mobile;
- si integrano con Canvas e FX.

### Dove usare video

Solo per eventuali momenti premium:

- intro speciale;
- ultimate highlight;
- victory cinematic;
- trailer/marketing.

Non per tutto il fight loop.

---

## 32. Bilanciamento

Il bilanciamento è ancora preliminare.

Serve un tool di simulazione massiva.

### Obiettivo

```bash
python3 tools/simulate_runs.py --runs 5000
```

Output desiderato:

```text
Hero winrate:
Fireheart 52.1%
Frostfang 48.7%
Nightshade 57.8%

Branch winrate:
Toxin 61.2%
Shield 44.3%
Precision 55.0%

Warnings:
Toxin + Healing too strong
Guardian weak early
Legendary unlock too late
```

### Metriche da misurare

- winrate hero;
- winrate branch;
- winrate combinazioni;
- average round reached;
- average gold;
- shop odds;
- card pick rate;
- HP loss;
- damage type distribution;
- bot performance;
- legacy card pick/win rate;
- effetti legacy non ancora mappati.

---

## 33. Bot AI

I bot attuali:

- hanno hero;
- hanno gold;
- hanno build;
- comprano carte;
- partecipano alla league;
- vengono simulati nei match bot-vs-bot.

### Da espandere

Archetipi:

- aggressive bot;
- economy bot;
- reroll bot;
- scaling bot;
- anti-meta bot;
- branch forcing bot;
- defensive bot;
- risky bot.

Azioni future:

- consultare e valutare la propria build;
- lock shop;
- cambiare strategia;
- puntare a soglie;
- adattarsi a sconfitte;
- scegliere counter-build.

---

---

## v1.8 Arena Flow + Hero Draft

Questa milestone porta il gioco verso un flusso più mobile e meno frammentato.

### Nuovo flow principale

```text
Home
→ genera 8 rami attivi / 4 bannati
→ Hero Draft con 3 hero compatibili
→ Market direttamente nell'arena
→ Battle con carte chiuse di default
→ ritorno diretto al Market nell'arena
→ repeat
```

La vecchia schermata `StandingsScene` resta nel codice, ma non è più obbligatoria nel percorso principale.

### Hero con rami favoriti multipli

Ogni hero ora supporta:

```json
"favoredBranches": ["rage", "power"]
```

Regole:

- massimo 2 rami favoriti;
- fallback compatibile con il vecchio `favoredBranch`;
- un hero è eleggibile se almeno uno dei suoi rami favoriti è attivo;
- gli hero con entrambi i rami bannati non compaiono nel draft iniziale.

### Hero Draft iniziale

Il player vede 3 hero random compatibili con i rami attivi.

```text
[Hero A] [Hero B] [Hero C]
Reroll disponibili: 2
```

Il reroll sostituisce il singolo slot e non genera duplicati visibili.

### Arena market / battle

Durante la preparation:

- arena visibile;
- market aperto automaticamente;
- nuove carte generate se lo shop non è lockato.

Durante la battle:

- carte nascoste di default;
- pulsante Cards disponibile;
- drawer apribile solo per consultazione;
- acquisto carte non disponibile durante il fight.

Dopo la battle:

- niente schermata intermedia;
- recap breve;
- ritorno automatico al market;
- round incrementato e preparation riaperta.

## v1.9 Round Recap Overlay

La v1.9 rifinisce il flow introdotto in v1.8: dopo ogni battle non compare più una schermata obbligatoria, ma un recap compatto direttamente sopra il market in arena.

### Cosa mostra il recap

- Victory/Defeat;
- nome e hero dell'avversario;
- HP persi dal player o inflitti all'avversario nella league;
- gold guadagnato nel round;
- rank attuale e partecipanti ancora vivi;
- danni fisici, magici, DoT e danni subiti dell'ultimo fight.

### Comportamento UX

- Il recap si apre automaticamente al ritorno nel market;
- si chiude da solo dopo pochi secondi;
- può essere riaperto tramite pill `Round Recap`;
- non blocca il market e non richiede un click per continuare;
- il pannello `ULTIMO ROUND` ora usa le statistiche dell'ultimo combat, non più i cumulativi della run.

Nota: `StandingsScene` resta nel codice come fallback/debug, ma non è più parte del percorso principale della run.

## v1.10 Market Readability + Card Inspect

La v1.10 migliora la leggibilità del market senza cambiare il bilanciamento. Il market resta dentro l’arena, ma ora le carte sono più facili da valutare prima dell’acquisto.

### Novità UI

- ogni carta shop ha un pulsante `i` per aprire un pannello dettaglio;
- il pannello dettaglio mostra nome, rarità, costo, livello, rami, testo effetto e meccaniche runtime;
- il pannello permette di comprare direttamente la carta quando è possibile;
- le carte non acquistabili evidenziano quanti coins mancano;
- le carte selezionate hanno un highlight visivo;
- il drawer durante la battle comunica meglio che il market è chiuso e le carte sono solo in consultazione.

### Obiettivo

Ridurre gli acquisti “alla cieca” su mobile. Il giocatore deve poter leggere cosa fa una carta senza dover decifrare testo microscopico mentre il timer gli respira sul collo come un mutuo.

## v1.11 Market Actions Polish + Card Collection UX

La v1.11 rende più chiare le azioni economiche del market. Non cambia il bilanciamento di carte, combat o income: cambia il modo in cui il giocatore capisce cosa può fare, quanto costa e cosa possiede.

### Novità UI

- bottom action bar ridisegnata con azioni più esplicite;
- `REROLL` mostra costo e stato disabled se mancano coins;
- `RANDOM` è ora accessibile dal market e mostra costo/stato pool;
- `UNDO` mostra chiaramente quando è disponibile;
- `LOCK` comunica se il prossimo market manterrà o rigenererà lo shop;
- pannello `CARTE` per consultare la collection posseduta;
- collection posseduta in sola consultazione, senza vendita/refund;
- paginazione collection da 12 carte per pagina;
- toast economici più espliciti: costo speso, carta ottenuta, undo disponibile.

### Regola UX

La collection non permette vendita: serve solo a leggere la build posseduta. Meno rischio, meno contabilità strana, più chiarezza: quello che compri resta parte della run.


## 34. Roadmap consigliata

### v1.6 — Legacy Effects Mapping

Obiettivo: trasformare gli effetti testuali del deck legacy in meccaniche reali.

Da implementare:

- tabella `legacy_effect_map.json`;
- parsing keyword più preciso;
- trigger condizionali;
- effetti cross-branch;
- effetti su HP persi;
- effetti su cast skill;
- effetti su stack;
- effetti economy/shop;
- test automatici per carte speciali;
- report “effetto legacy implementato / non implementato”.

---

### v1.7 — Sprite Sheet Pipeline + Intro / KO / Victory Animations

Obiettivo: rendere i fight più vivi.

Da implementare:

- `SpriteAnimator.js`;
- `AnimationStateMachine.js`;
- `data/animations.json`;
- atlas/sheet manifest;
- placeholder animazioni;
- idle;
- intro;
- attack;
- skill;
- hit reaction;
- KO;
- victory pose;
- sincronizzazione hit timing;
- camera zoom/pan su momenti chiave.

---

### v1.8 — Card Art / Asset Slicing

Obiettivo: sostituire i placeholder legacy.

Da implementare:

- card art finali per 150 carte;
- slicing branch icon;
- slicing UI elements;
- sostituzione placeholder SVG;
- aggiornamento asset manifest;
- report asset mancanti.

---

### v1.9 — Tutorial + Audio

Obiettivo: onboarding e feeling.

Da implementare:

- tutorial guidato;
- SFX reali;
- musica base;
- settings audio/haptic;
- prima run controllata.

---

### v2.0 — Balance Build

Obiettivo: numeri meno “a sentimento”.

Da implementare:

- simulatore run;
- report winrate;
- branch/card/hero analytics;
- bot benchmark;
- tuning economia;
- tuning HP loss;
- tuning shop odds.

---

### v2.1 — PWA Offline + Save Robust

Obiettivo: rendere la web app quasi installabile.

Da implementare:

- service worker;
- offline cache;
- save versioning;
- export/import save;
- install prompt;
- app icons;
- splash screen.

---

### v2.2 — Mobile Candidate

Obiettivo: primo pacchetto testabile come app.

Da implementare:

- wrapper Android;
- APK;
- performance pass;
- UI polish;
- asset slicing;
- test device;
- bug fixing.

---

## 35. Ruoli utili per collaboratori

### Game Designer

Si occupa di:

- carte;
- rami;
- soglie;
- economia;
- bilanciamento;
- bot archetypes;
- tutorial flow;
- mappatura degli effetti legacy.

### Frontend / Engine Developer

Si occupa di:

- Canvas renderer;
- scene system;
- input;
- sprite animation;
- performance;
- PWA;
- mobile packaging;
- pipeline runtime.

### UI/UX Designer

Si occupa di:

- overlay UI;
- HUD fighting-game inspired;
- market drawer;
- interaction flow;
- touch usability;
- hierarchy;
- mobile readability.

### Concept Artist

Si occupa di:

- hero portrait;
- card art;
- branch icons;
- arena backgrounds;
- UI ornaments;
- card illustrations per le 150 carte.

### Technical Artist

Si occupa di:

- sprite sheet;
- atlas;
- VFX;
- animation timing;
- asset slicing;
- pipeline optimization;
- 2.5D arena layer pass.

### Sound Designer

Si occupa di:

- UI SFX;
- combat SFX;
- win/lose cues;
- music loops;
- audio feedback.

### QA / Balancing

Si occupa di:

- test run;
- exploit;
- bug report;
- balancing data;
- mobile compatibility;
- performance profiling;
- validazione deck legacy.

---

## 36. Regole di identità / IP

Hero Smash deve restare originale.

Non usare:

- loghi esistenti;
- nomi protetti;
- personaggi riconoscibili;
- UI copiata 1:1;
- asset presi da altri giochi;
- riferimenti diretti a Dota, Auto Gladiators, Auto Chess, Street Fighter o altri IP.

Consentito:

- ispirarsi al genere;
- usare pattern di UX comuni;
- reinterpretare il linguaggio arcade/fighting;
- creare asset, nomi, lore e UI originali.

---

## 37. Terminologia progetto

| Termine | Significato |
|---|---|
| Run | Una partita completa |
| Round | Una fase market + combat |
| Hero | Personaggio principale del player |
| Bot | Avversario controllato dal sistema |
| League | Gruppo di 8 partecipanti |
| Branch | Ramo/sinergia |
| Card | Oggetto acquistabile nel market |
| Legacy Deck | Il vecchio `deck.json`, ora fonte autorevole delle carte |
| Legacy Effect | Effetto testuale originale di una carta |
| Tier | Livello del ramo in base ai punti |
| HP Run | Vita del player nella run |
| Market | Fase acquisto carte |
| Card Drawer | Pannello carte apribile/chiudibile |
| Combat | Fight automatico |
| Standings | Classifica league |
| Build | Insieme di carte e rami del player |
| DoT | Damage over time |
| Proc | Effetto che si attiva con probabilità |
| Sprite Sheet | Immagine con più frame animazione |
| Parallax Arena | Arena a layer con profondità simulata |
| Fighter UI | HUD ispirato ai picchiaduro arcade |
| Hit Stop | Micro pausa su impatto forte |
| KO | Knockout / fine fight spettacolare |

---

## 38. Stato sintetico: cosa c’è già

Implementato:

- custom engine;
- layout landscape;
- PWA base;
- hero select;
- branch draft;
- 12 rami;
- 8 rami attivi random;
- card system;
- import esatto delle 150 carte legacy;
- market completo;
- economia;
- shop lock;
- undo;
- collection carte;
- bot league;
- combat automatico;
- combat readability;
- asset pipeline;
- final art integration;
- Fighter UI System;
- overlay UI;
- collapsible card drawer;
- Arena01 2.5D runtime;
- local save;
- docs tecnici.

---

## 39. Stato sintetico: cosa manca

Mancano ancora:

- mappatura completa effetti legacy;
- sprite sheet pipeline;
- intro/victory/KO animate;
- hero portrait finali individuali;
- card art finali singole per 150 carte;
- branch icon slicing;
- UI asset slicing;
- foreground props layer arena;
- audio reale;
- tutorial;
- simulatore bilanciamento;
- bot AI avanzata;
- service worker/offline;
- wrapper Android/iOS;
- performance mobile pass.

---

## 40. Direzione immediata consigliata

Il prossimo step più sensato è:

```text
v1.6 — Legacy Effects Mapping
```

Perché ora il deck corretto è dentro al gioco.  
Il problema non è più “quali carte devono esserci”.  
Il problema ora è: **ogni carta deve fare esattamente quello che promette**.

Subito dopo:

```text
v1.7 — Sprite Sheet Pipeline + Intro / KO / Victory Animations
```

Così il combat passa da “funziona e si legge” a “sembra davvero un duello arcade”.

---

## 41. Filosofia di sviluppo

Hero Smash deve crescere così:

1. prima il sistema;
2. poi la leggibilità;
3. poi l’identità visiva;
4. poi il contenuto esatto;
5. poi la fedeltà degli effetti;
6. poi animazioni e asset atomici;
7. poi bilanciamento;
8. infine mobile packaging.

La priorità non è fare “tutto subito”.  
La priorità è non costruire un castello sopra codice fragile.

Ora il progetto ha una cosa fondamentale: **il deck vero**.  
Da qui in poi si smette di improvvisare contenuto. Finalmente.

---

## 42. One-liner finale

**Hero Smash è un auto-battler mobile in landscape dove costruisci il tuo gladiatore usando le 150 carte legacy ufficiali, sopravvivi a una league da 8 partecipanti e guardi i fight automatici trasformarsi in duelli arcade su arena 2.5D.**



Questa build integra **senza perdere i sistemi precedenti**:

- Final Art Integration
- Market completo
- Bot League 8 player
- Combat readability
- Asset pipeline
- Fighter UI System
- Arena01 Beast Crucible 2.5D Runtime

## Avvio

```bash
python3 tools/serve.py
```

Apri:

```text
http://127.0.0.1:8000
```

## Cosa è stato aggiunto in v1.3

### Fighter UI System

Sono stati integrati i componenti:

```text
src/ui/fighter/FighterTheme.js
src/ui/fighter/FighterHealthBar.js
src/ui/fighter/RoundTimer.js
src/ui/fighter/StatusIconBar.js
src/ui/fighter/CombatBanner.js
src/ui/fighter/LeaguePanel.js
src/ui/fighter/EvolutionPanel.js
src/ui/fighter/BranchProgressPanel.js
src/ui/fighter/MarketCardFrame.js
src/ui/fighter/FighterButton.js
```

Usi principali:

- HUD combat stile arcade fighter
- health/energy bars inclinate
- timer centrale
- banner Round Start / Fight / Victory / Defeat
- pannelli league e branch più coerenti
- market cards con frame fighter style
- bottoni bevel/slanted

### Arena01 2.5D Runtime

È stato integrato il pacchetto:

```text
assets/arenas/arena01_beast_crucible/
data/arenas/
src/arena/
```

Funzioni:

- layer separati
- parallax
- crystal floating/glow
- idle camera drift
- camera shake su impatti
- dust FX ambientale
- fallback statico se l'arena non carica

Il CombatScene usa ora Arena01 come stage runtime 2.5D, mantenendo tutto il combat system già esistente.

## Sistemi preservati

Non sono stati rimossi:

- 16 hero
- 12 rami
- 8 rami attivi / 4 bannati
- card system
- market completo
- lock shop
- reroll
- random card
- collection carte in sola consultazione
- undo acquisto
- preview soglie ramo
- probabilità shop
- economia con interessi/streak
- Bot League
- combat automatico frame-by-frame
- recap danni
- status icons
- asset pipeline
- final art pack

## Nota

Questa build non trasforma ancora gli hero in sprite sheet animati completi.  
Fa il passo precedente corretto: monta **HUD fighter-style** e **arena 2.5D runtime** dentro il gioco esistente.

Il prossimo step naturale è:

```text
v1.4 — Sprite Sheet Pipeline + Intro / KO / Victory Animations
```



## v1.6 Legacy Effects Mapping

Questa build porta ogni carta a fare esattamente quello che promette.

### Nuovi handler runtime in CombatSystem

- **`powerDamage`** — danno flat su skill fisiche (ramo power), era prodotto ma non consumato
- **`lifesteal`** — cura l'attaccante per una percentuale del danno inflitto (ogni colpo base e skill)
- **`deathShield`** — previene la prima morte: HP fissati a 1, burst shield al 35% degli HP max
- **`counterHit`** — 20% di chance di contrattaccare immediatamente quando si riceve danno
- **`dodgeReflect`** — sulla schivata, riflette il 50% del danno evaso come danno magico
- **`openingCrits`** — i primi N attacchi di ogni combat sono critici garantiti
- **`phaseChance`** — chance di annullare completamente un colpo in arrivo (cooldown 0.5s)
- **Ice slow fix** — il status `ice` ora rallenta effettivamente velocità d'attacco e regen energia del bersaglio

### Carte aggiornate

| Carta | Effetto faithfully implementato |
|---|---|
| BERSERKER FRENZY (legacy_009) | lifesteal + deathShield |
| COURAGEOUS MOMENT (legacy_016) | counterHit |
| GIFT OF FREEDOM (legacy_017) | openingCrits (3 crits garantiti) |
| DIVINE REFLECTION (legacy_049) | dodgeReflect |
| TRICKERY (legacy_051) | phaseChance |
| LAST STAND (legacy_111) | deathShield |

### BranchSystem aggiornato

Nuovi bonus di ramo: `woundHit`, `iceHit`, `shieldRegen`, `healBoost`, `critD`, `multiHit`, `execute` distribuiti sui rami che li implicavano semanticamente.

**Copertura effetti: 36/36 chiavi — 100%**

Documentazione completa: `docs/LEGACY_EFFECTS_MAPPING_v1_6.md`

## v1.4 UI Update

- UI sovrapposta direttamente alla fight scene.
- Classifica HP in banner a sinistra.
- Branch Report in banner a destra.
- Market card drawer apribile/chiudibile.
- Il drawer si riapre automaticamente a ogni nuova preparation phase.
- Arena aggiornata con le immagini fornite.


## v1.5 Legacy Deck Exact Import

Questa build usa `deck.json` come fonte autorevole per tutte le carte:

- 150 carte importate
- 90 Normali
- 36 Epiche
- 24 Leggendarie
- 84 monoramo
- 66 bi-ramo

Report completo: `data/legacy_deck_import_report.json` e `docs/LEGACY_DECK_EXACT_IMPORT_v1_5.md`.
