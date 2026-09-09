# v1.7 — Sprite Sheet Pipeline

**Milestone:** `HeroSmash_CustomEngine_v1_7_SpritePipeline`
**Dipendenza:** v1.6 (Legacy Effects Mapping)

---

## Obiettivo

Trasformare il combat da "due cerchi colorati" a un duello arcade con:
- Sprite animati per tutti e 16 gli hero
- Sequenze cinematiche intro / KO / victory
- Pipeline ufficiale per importare art reale in futuro

---

## Formato Sprite Sheet (canonico)

### Layout PNG

```
1024 × 1344 px  (8 col × 7 righe, frame 128×192 px)

Row 0 — idle    (4 frame @ 7fps,  loop)
Row 1 — attack  (4 frame @ 14fps, once)
Row 2 — skill   (6 frame @ 10fps, once)
Row 3 — hit     (2 frame @ 12fps, once)
Row 4 — death   (6 frame @ 8fps,  once)
Row 5 — victory (4 frame @ 8fps,  loop)
Row 6 — intro   (4 frame @ 10fps, once)
```

Ogni frame: colonne sx→dx per indice frame, nessun padding.

### Manifest JSON

```json
{
  "meta": {
    "hero":   "ironfist",
    "image":  "assets/sprites/ironfist.png",
    "frameW": 128,
    "frameH": 192,
    "sheetW": 1024,
    "sheetH": 1344,
    "source": "generated" | "imported" | "final"
  },
  "animations": {
    "idle":    { "row": 0, "frames": 4, "fps": 7,  "loop": true  },
    "attack":  { "row": 1, "frames": 4, "fps": 14, "loop": false },
    "skill":   { "row": 2, "frames": 6, "fps": 10, "loop": false },
    "hit":     { "row": 3, "frames": 2, "fps": 12, "loop": false },
    "death":   { "row": 4, "frames": 6, "fps": 8,  "loop": false },
    "victory": { "row": 5, "frames": 4, "fps": 8,  "loop": true  },
    "intro":   { "row": 6, "frames": 4, "fps": 10, "loop": false }
  }
}
```

Il formato è compatibile con Aseprite via `tools/import_spritesheet.py`.

---

## Flusso per aggiungere sprite reali

### Con Aseprite

1. Crea le animazioni con i tag: `idle`, `attack`, `skill`, `hit`, `death`, `victory`, `intro`
2. Esporta in **JSON hash** + PNG (File → Export Sprite Sheet → JSON Hash)
3. Esegui il converter:
   ```bash
   python3 tools/import_spritesheet.py ironfist export/ironfist.json assets/sprites
   ```
4. Copia il PNG in `assets/sprites/ironfist.png`
5. Aggiorna `data/sprites_manifest.json`: cambia `"source": "final"` per quell'hero

### Con TexturePacker o altro tool

Stessa procedura — il converter rileva il formato automaticamente.

### Sostituzione diretta (frame identici)

Se la tua sheet usa già il nostro layout (128×192, 8 col × 7 righe):
1. Copia il PNG in `assets/sprites/{hero_id}.png`
2. Il JSON placeholder esistente funziona già — nessuna modifica necessaria

---

## Componenti JS aggiunti

### `AnimationSystem` (`src/engine/AnimationSystem.js`)

State machine per-unit. Vive su `app.anim` (globale).

```javascript
app.anim.register(heroId, image, manifest); // al boot
app.anim.setState(heroId, 'attack');         // cambia stato
app.anim.update(heroId, dt);                 // avanza timer
const f = app.anim.getFrame(heroId);         // { image, sx, sy, sw, sh, done }
```

### `CinematicSystem` (`src/engine/CinematicSystem.js`)

Macchina a stati cinematica in `CombatScene`.

Fasi:
```
INTRO (1.8s) → FIGHT → KO (1.5s) → VICTORY (2.0s) → DONE
```

API chiave:
```javascript
cin.update(dt);
cin.triggerKO();              // chiamato quando combat.result si setta
cin.isCombatPaused();         // true durante INTRO
cin.getAnimState(u, result, isPlayer); // → 'idle'|'attack'|'skill'|...
cin.introX(isPlayer, targetX);         // X durante entrata da bordo
cin.koFlashAlpha;                      // 0→1→0 flash bianco al KO
```

### `Renderer.drawSprite()` (`src/engine/Renderer.js`)

```javascript
r.drawSprite(image, sx, sy, sw, sh, dx, dy, dw, dh, flipX, alpha);
r.drawSpriteColored(image, sx, sy, sw, sh, dx, dy, dw, dh, flipX, tintColor, tintAlpha);
```

---

## Sequenze cinematiche

### INTRO (1.8s)

- Player entra da destra (startX = 1506), enemy da sinistra (startX = -140)
- Ease-out cubic sul movimento
- A metà intro compaiono i name tag centrali
- Combat in pausa

### KO (1.5s)

- `triggerKO()` chiamato al primo frame con `combat.result`
- Flash bianco `sin(t*π)` in dissolvenza
- Banner "KO" che scala da 0 a 100% al centro
- Loser in animazione `death`, winner in `idle`

### VICTORY (2.0s)

- Winner in animazione `victory` (loop)
- Banner "[Name] WINS" con dissolvenza in entrata
- Dopo DONE il recap standard è accessibile

---

## Generazione placeholder

Tutti i 16 hero hanno placeholder generativi:

```bash
python3 tools/generate_placeholder_sprites.py data/heroes.json assets/sprites
```

I placeholder sono silhouette geometriche colorate, differenziate per animazione.
Sono funzionali e sostituibili con art finale senza toccare il codice.

---

## `data/sprites_manifest.json`

Registro di tutti gli sprite sheets. Il BootScene lo carica all'avvio:

```json
{
  "heroes": {
    "fireheart": {
      "manifest": "assets/sprites/fireheart.json",
      "image":    "assets/sprites/fireheart.png",
      "source":   "generated"
    }
  }
}
```

Cambiare `"source": "final"` è opzionale (solo informativo).

---

## Fallback garantito

Se uno spritesheet non carica → `app.anim.hasSprite(heroId)` = false → `CombatScene` usa il cerchio colorato originale. Nessuna regressione.

---

## Stato placeholder vs art finale

| Hero | Stato |
|------|-------|
| tutti i 16 | `generated` (placeholder geometrico) |
| i tuoi 1–4 hero con art | pronto per `import_spritesheet.py` |

---

## Prossima milestone

```
v1.8 — Bot AI upgrade + balancing simulator
```

Ora che il combat ha presentazione arcade, il passo successivo è rendere i bot avversari più intelligenti.
