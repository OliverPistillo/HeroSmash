# v0.9 — Bot League + Combat Polish

## Bot League

La run ora contiene 8 player:
- `you`
- 7 bot

Ogni bot è uno state-like object con:
- hero
- life
- gold
- activeBranches
- cardLevels
- streak
- stats

Il sistema genera pairing a ogni round. Il player umano combatte il suo opponent su canvas; gli altri match vengono simulati da `LeagueSystem.resolveBotMatch` usando `BotSystem.powerScore`.

## Bot AI

I bot preferiscono:
1. carte vicine a una soglia ramo,
2. carte del ramo favorito dell'hero,
3. carte random dal pool disponibile.

## Combat Polish

Il combat canvas ora mostra:
- icone status,
- trail d'attacco,
- pulse di cast,
- floating text colorato,
- recap danni.

## Limiti ancora presenti

- I bot non hanno ancora una strategia profonda per archetipi complessi.
- La simulazione bot-vs-bot usa power score, non combat frame-by-frame completo.
- Mancano ancora audio/VFX definitivi e bilanciamento numerico serio.
