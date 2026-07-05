---
tipo: reference
argomento: legenda ASCII per import in Floorplan
---

# Legenda ASCII → Floorplan (convenzione skill `/mappa`)

Floorplan usa una **legenda ASCII fissa e hardcoded**: l'import
(`File → Import ASCII Dungeon`) NON apre un dialogo di assegnazione, genera
direttamente il dungeon interpretando ogni carattere secondo il proprio schema.

**Fonte autorevole:** `floorplan-ascii-ufficiale.txt` = output di
`illfloor.exe --listascii`. La legenda **non è estendibile**: terreni/icone custom
aggiunti in `%AppData%\Roaming\illfloor\terrain\` o `\icons\` NON ricevono un
carattere ASCII (verificato empiricamente) — sono solo da dipingere/piazzare a mano.

`legend-chars.txt` è la sorgente autorevole dei caratteri legali usata dal
validatore; questa tabella deve restare coerente con quel file.

## Cosa si importa via ASCII

**Terreni** (muri, pavimenti, liquidi, biomi) + **solo 3 icone**: `D` porta,
`B` cespuglio, `T` albero. Tutto il resto del catalogo (mobili) NON è importabile.

### Sottoinsieme utile per interni/dungeon
| Char | Diventa in Floorplan |
|------|----------------------|
| (spazio) | muro di caverna / esterno |
| `W` | muro di pietra |
| `O` | muro di legno |
| `.` | pavimento di caverna |
| `:` | pavimento di pietra |
| `x` | pavimento di legno |
| `M` | pavimento di marmo |
| `L` | ciottoli |
| `G` | pavimento di granito |
| `C` | pavimento a scacchi |
| `9` | pavimento di metallo |
| `~` | mare / acqua |
| `r` | acqua |
| `l` | lava |
| `4` | fuoco |
| `S` | fogna |
| `D` | porta *(icona)* |
| `T` | albero *(icona)* |
| `B` | cespuglio *(icona)* |

> Per l'elenco completo (biomi esterni, varianti d'acqua, ecc.) vedi
> `floorplan-ascii-ufficiale.txt`. Alcune voci lì hanno char `?` = nessun carattere
> stampabile assegnato → paint-only, non importabili via ASCII.

## Arredo / mobili — via compositing (non via ASCII di Floorplan)

Tavoli, sedie, casse, letti, barili, librerie, focolari, altari NON si importano
con l'ASCII di Floorplan. La skill li gestisce con un **secondo livello**: una
griglia arredo (caratteri in `furniture-legend.txt`) che `_scripts/floorplan_furnish.py`
**sovrappone** al PNG dell'architettura con Pillow (icone TGA 64/128/32 px centrate
sulla cella). Vedi il flusso in `SKILL.md` (step 2, 3c).

In alternativa (rifinitura a mano) i mobili si possono aggiungere nell'editor:
`i` = seleziona icona, `ctrl+i` = cerca per nome, `<` / `>` = sotto/sopra i muri,
`Del` = elimina. Icone-mobile del catalogo: `table_1`, `table_2`,
`table_chairs_1/2`, `chair_1`, `bench_1`, `chest_1`, `wooden_crate_1`, `bed_1`,
`bed_double_1`, `barrel_top_1/2`, `bookshelf_1/2/3`, `bardesk`, `desk1`, `edgedesk1`,
`walltable_1`, `fireplace_1/2`, `altar_1/2`, `bottle`, `candle`, `pot_small`,
`rug_1/2/3`, `curtain_1/2/3`, `charred_wood`.

## Regole di disegno della griglia
- Racchiudi ogni stanza con caratteri-muro (`W`/`O`); il perimetro esterno è muro o spazio.
- Riempi l'interno con un carattere-pavimento coerente col tema.
- Inserisci `D` nel muro dove c'è una porta; `T`/`B` per alberi/cespugli.
- La griglia deve essere **rettangolare** (tutte le righe della stessa lunghezza).
- NON inserire caratteri per i mobili: l'arredo va nel manifest della nota.
