# Patch Notes — v1.14.2 Hero Draft Full Replacement

## Modifiche principali
- Sostituzione completa di `HeroSelectScene.js`.
- Click su una hero card = selezione, non avvio diretto.
- Aggiunto bottone grande `CONFERMA FIGHTER`.
- Stato selezionato molto più evidente.
- Timer visibile da 20 secondi.
- Alla scadenza:
  - se è stato selezionato un eroe, viene confermato quello;
  - se non è stato selezionato nessun eroe, viene assegnato automaticamente l'eroe a sinistra.
- Reroll reso mini e meno invasivo.
- Sfondo più scuro per nascondere la vecchia schermata sotto.
- Layout più compatto e mobile premium.
- Pannello dettagli a destra aggiornato.
- Bottom bar sostituita con stato selezione + conferma.

## File modificati
- `src/scenes/HeroSelectScene.js`
- `data/runtime.json`
