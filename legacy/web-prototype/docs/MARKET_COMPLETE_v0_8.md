# Market Complete v0.8

## Feature implementate

### Lock shop
Il bottone Lock conserva lo shop anche dopo il combattimento successivo. Se il lock è attivo, `CardSystem.rollShop` non sostituisce la lista corrente.

### Timer preparation
Ogni fase market parte con 35 secondi. Se il timer arriva a zero, il gioco passa automaticamente al combat.

### Card detail
Toccando una carta si apre un popup con:
- artwork
- rarità
- livello attuale
- descrizione
- preview ramo
- probabilità nello shop
- lista effetti
- acquisto o vendita

### Preview ramo
Prima dell'acquisto mostra:
- punti attuali
- punti dopo acquisto
- soglia superata

### Collezione e vendita
La modalità Collezione mostra le carte possedute. Una carta può essere venduta per il 50% del costo.

### Undo
Annulla l'ultimo acquisto e restituisce il costo pagato.

## Prossimo step

Dopo questo market completo, il prossimo blocco naturale è Bot League:
- 7 bot
- classifica 8 player
- pairing round-by-round
- eliminazioni
