# Combat Readability v1.1

## Problema

Il combat precedente funzionava, ma il giocatore doveva intuire troppo:
- che tipo di danno stava vedendo
- quale status era attivo
- quando una skill era pronta
- cosa aveva inciso nel risultato

## Soluzione

### Codice colore
- Bianco: danno fisico
- Viola: skill/magico
- Verde: DoT/Toxin
- Azzurro: Shield assorbito
- Giallo: Crit e skill-ready
- Rosso: danno subito/sconfitta

### Status icons
Ogni unità mostra gli status sopra la testa:
- Toxin
- Burn
- Wound
- Ice
- Stun
- Shield

Gli status mostrano anche stack e una micro barra durata.

### Skill readability
- Cerchio tratteggiato giallo: skill pronta.
- Pulse viola: skill lanciata.
- Testo azione sopra il personaggio.

### Recap finale
A fine match il giocatore vede:
- danno fisico
- danno magico
- danno DoT
- crit
- cure
- shield assorbito
- schivate
- danno subito

## Risultato

Il combat non è ancora “AAA”, ma ora è leggibile. Si capisce cosa sta succedendo, non solo che due palline si stanno facendo del male.
