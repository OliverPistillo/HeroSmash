# Patch Notes — v1.8 Arena Flow + Hero Draft

## Aggiunto

- Hero draft iniziale con 3 hero random compatibili con i rami attivi.
- 2 reroll totali per sostituire singoli hero slot.
- Supporto `favoredBranches` massimo 2 per hero.
- Runtime label aggiornato a v1.8.

## Cambiato

- I rami attivi/bannati vengono generati prima della scelta hero.
- Dopo il combat si torna direttamente al market nell'arena.
- Durante la battle il drawer carte parte chiuso.
- Il drawer in battle è apribile manualmente ma non permette acquisti.
- BotSystem considera entrambi i rami favoriti dell'hero.

## Conservato

- `favoredBranch` resta nei dati come fallback legacy.
- `StandingsScene` resta nel codice, ma non è più nel percorso principale.
- Lock shop continua a preservare lo shop tra battle e market.
