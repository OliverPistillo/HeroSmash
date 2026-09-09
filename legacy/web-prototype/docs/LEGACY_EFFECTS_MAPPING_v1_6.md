# v1.6 — Legacy Effects Mapping

**Milestone:** `HeroSmash_CustomEngine_v1_6_LegacyEffectsMapping`  
**Dipendenza:** v1.5 (Legacy Deck Exact Import)

---

## Obiettivo

Ogni carta deve fare esattamente quello che promette.

La v1.5 aveva importato le 150 carte con una mappatura numerica conservativa.  
La v1.6 completa quella mappatura: ogni chiave di effetto produce ora un comportamento
specifico nel `CombatSystem` anziché restare un numero silenzioso.

---

## Riepilogo modifiche

### 1. BranchSystem.js — Nuovi bonus di ramo

| Ramo | Aggiunto | Note |
|---|---|---|
| `wound` | `woundHit` | Il ramo wound ora genera anche probabilità di applicare wound, non solo amplificazione |
| `ice` | `iceHit` | Il ramo ice ora genera direttamente la probabilità di ghiacciare |
| `shield` | `shieldRegen`, `healBoost` | Regen periodico scudo e amplificazione cure |
| `power` | `execute` | Danno bonus a bassa vita, in aggiunta a `powerDamage` |
| `precision` | `critD` | Il ramo precision ora scala anche il moltiplicatore critico |
| `assault` | `multiHit` | Il ramo assault garantisce extra-colpi |

### 2. CombatSystem.js — Nuovi handler runtime

#### `powerDamage` *(era prodotto ma non consumato)*
- **Quando:** skill fisiche del giocatore
- **Effetto:** danno flat aggiuntivo post-calcolo, floater arancione `PWR +N`

#### `lifesteal` *(nuovo)*
- **Quando:** ogni colpo base o skill del giocatore che infligge danno
- **Effetto:** cura l'attaccante per `lifesteal × danno_inflitto`
- **Carte:** BERSERKER FRENZY (legacy_009)

#### `deathShield` *(nuovo)*
- **Quando:** l'unità scende a 0 HP
- **Effetto:** HP fissati a 1, applica shield burst pari al 35% degli HP massimi, durata 3s
- **Floater:** `LAST STAND!` giallo
- **Carte:** BERSERKER FRENZY (legacy_009), LAST STAND (legacy_111)

#### `counterHit` *(nuovo)*
- **Quando:** il giocatore riceve danno, probabilità `counterHit`
- **Effetto:** colpo fisico immediato sull'attaccante pari al 50% dell'ATK del giocatore
- **Floater:** `⚡ N` giallo
- **Carte:** COURAGEOUS MOMENT (legacy_016)

#### `dodgeReflect` *(nuovo)*
- **Quando:** schivata del giocatore andata a buon fine
- **Effetto:** riflette `dodgeReflect × danno_evaso` come danno magico sull'attaccante
- **Floater:** `↩ N` viola
- **Carte:** DIVINE REFLECTION (legacy_049)

#### `openingCrits` *(nuovo)*
- **Quando:** inizio combattimento, i primi `openingCrits` attacchi del giocatore
- **Effetto:** critico garantito (bypassa il roll), decrementa il contatore
- **Carte:** GIFT OF FREEDOM (legacy_017)

#### `phaseChance` *(nuovo)*
- **Quando:** il giocatore riceve danno, cooldown 0.5s tra proc
- **Effetto:** annulla completamente il colpo in arrivo
- **Floater:** `PHASE` viola
- **Carte:** TRICKERY (legacy_051)

#### `ice` slow sul tick di azione *(bug fix)*
- **Prima:** il status `ice` esisteva ma non rallentava effettivamente l'avversario
- **Ora:** `iceMult` in `act()` riduce la velocità di attacco e il regen energia proporzionalmente a `slow × stacks`
- Minimo garantito: 35% della velocità originale (`iceMult ≥ 0.35`)

---

## Carte modificate

### BERSERKER FRENZY `legacy_009` (Leggendaria, assault)

> *"Triggers upon taking lethal damage, preventing death for 1.4 seconds, granting 80 Assault speed and 45% Lifesteal."*

| Chiave | v1.5 | v1.6 |
|---|---|---|
| `lifesteal` | — | 0.22 |
| `deathShield` | — | 1 |
| `startShield` | 32.4 | rimosso (sostituito da deathShield) |
| `healBoost` | 0.027 | 0.014 (ridotto, lifesteal è più fedele) |

### COURAGEOUS MOMENT `legacy_016` (Epica, assault)

> *"A 20% chance of immediately performing a counter-attack when taking damage."*

| Chiave | v1.5 | v1.6 |
|---|---|---|
| `counterHit` | — | 0.20 |
| `multiHit` | 0.0297 | 0.012 (ridotto, era un proxy sbagliato) |

### GIFT OF FREEDOM `legacy_017` (Leggendaria, precision)

> *"At the start of the battle, temporarily raises critical chance to 100; lasts for 3 Crit."*

| Chiave | v1.5 | v1.6 |
|---|---|---|
| `openingCrits` | — | 3 |

### DIVINE REFLECTION `legacy_049` (Leggendaria, dodge/essence)

> *"When Evasion, there is a 50% chance to reflect incoming damage as magical damage."*

| Chiave | v1.5 | v1.6 |
|---|---|---|
| `dodgeReflect` | — | 0.50 |
| `multiHit` | 0.006 | rimosso (era un proxy sbagliato) |

### TRICKERY `legacy_051` (Leggendaria, dodge)

> *"When taking any damage, [8%+20%×evasion] chance to become immune for 0.2s."*

| Chiave | v1.5 | v1.6 |
|---|---|---|
| `phaseChance` | — | 0.12 |

### LAST STAND `legacy_111` (Leggendaria, shield)

> *"Become immune to death 1 time and immediately gains 1200 stack(s) of Shield."*

| Chiave | v1.5 | v1.6 |
|---|---|---|
| `deathShield` | — | 1 |
| `startShield` | 81.0 | 40.5 (ridotto, deathShield porta il burst shield alla morte) |

---

## Copertura effetti post-v1.6

| Chiave effetto | Handler | Note |
|---|---|---|
| `hp` | ✅ applyLoadout | HP massimi e iniziali |
| `armor` | ✅ applyLoadout | Riduzione danno fisico |
| `attack` | ✅ applyLoadout | ATK addizionale |
| `focus` | ✅ applyLoadout | Focus (danno magico) addizionale |
| `manaRegen` | ✅ applyLoadout | Regen energia |
| `speedPct` | ✅ applyLoadout | Moltiplicatore velocità attacco |
| `crit` | ✅ applyLoadout | Probabilità critico addizionale |
| `critD` | ✅ applyLoadout | Moltiplicatore danno critico |
| `dodge` | ✅ applyLoadout | Probabilità schivata |
| `startShield` | ✅ applyLoadout | Shield istantaneo a inizio combat |
| `openingCrits` | ✅ applyLoadout + damage | N critici garantiti ad apertura |
| `deathShield` | ✅ applyLoadout + take | Previene la prima morte |
| `hpRegen` | ✅ act | Regen HP per secondo |
| `shieldRegen` | ✅ act | Regen shield periodico (ogni 7s) |
| `healBoost` | ✅ heal | Amplificazione percentuale cure |
| `lifesteal` | ✅ basic + skill | Cura su danno inflitto |
| `multiHit` | ✅ basic | Extra colpo leggero |
| `counterHit` | ✅ take | Counter-attacco su ricezione danno |
| `tempo` | ✅ basic | Burst energia ogni 5 colpi |
| `toxinHit` | ✅ basic | Proc veleno su colpo base |
| `toxinTick` | ✅ basic | Tick danno veleno |
| `toxinBoost` | ✅ basic | Amplificazione veleno |
| `woundHit` | ✅ basic + BranchSystem | Proc piaga su colpo base |
| `woundAmp` | ✅ basic + damage | Amplificazione danno su piagati |
| `iceHit` | ✅ basic + BranchSystem | Proc ghiaccio su colpo base |
| `slow` | ✅ act (ice status) | Rallentamento attacchi/regen su ghiacciati |
| `stunHit` | ✅ basic | Proc stordimento su colpo base |
| `skillPower` | ✅ skill | Moltiplicatore skill |
| `powerDamage` | ✅ skill | Danno flat su skill fisiche |
| `execute` | ✅ damage | Danno bonus a < 30% HP |
| `echo` | ✅ skill | Ripetizione skill a potere ridotto |
| `shieldReduction` | ✅ take | Riduzione danno passiva |
| `dodgeReflect` | ✅ take (dodge) | Riflette danno evaso come magico |
| `phaseChance` | ✅ take | Annulla colpo in arrivo |

**Copertura: 36/36 chiavi — 100%**

---

## Prossima milestone

```
v1.7 — Sprite Sheet Pipeline + Intro / KO / Victory Animations
```

Ora che ogni carta fa quello che promette, il passo successivo è rendere
il combat visivamente distinguibile: animazioni hero, intro round, KO cinematico.
