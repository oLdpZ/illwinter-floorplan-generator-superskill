---
tipo: nota-tecnica
argomento: import-icone Floorplan
data: 2026-07-05
---

# Fase 0 — Esito micro-test icone

**ESITO: B**

- **A** = nel dialogo *Import ASCII Dungeon* un carattere può essere assegnato a un'icona-mobile → l'arredo si genera via ASCII. La legenda include righe "icone-mobili".
- **B** = l'import assegna solo terreni/architettura → l'arredo è fornito come manifest testuale per stanza nella nota; l'ASCII copre solo l'architettura.

## Nota dall'utente

Test eseguito importando `Mappe/_test-import.txt` (stanza 5×5 con `W`, `.`, `D`, e `t` al centro).

**Scoperta 1 — nessun dialogo di assegnazione.** L'import NON apre un dialogo dove
si assegnano i caratteri ai tile: apre direttamente il dungeon già generato.
Floorplan usa quindi una **legenda ASCII fissa e predefinita**. I caratteri NON
sono una convenzione arbitraria nostra: `legend-chars.txt` deve contenere i
caratteri *reali* riconosciuti da Floorplan (quelli del manuale), non inventati.

**Scoperta 2 — i mobili non si importano via ASCII.** Risultato osservato:
- `W` → muri di pietra ✅
- `.` → pavimento ✅
- `D` → porta ✅
- `t` → NON è diventato un tavolo: Floorplan ha "indovinato un terreno" (una chiazza
  di pavimento chiaro), coerente col manuale: *"If an icon is selected instead of a
  terrain, then IFG will guess what terrain would be suitable in that square."*

**Conseguenza operativa:** l'ASCII copre solo l'architettura. L'arredo/icone si
piazzano a mano nell'editor di Floorplan (comandi `i` = select icon, `ctrl+i` =
search, `<`/`>` = place under/over walls). Nel flusso della skill l'arredo va
fornito come **manifest testuale per stanza** nella nota Giudice.

## Approfondimento (2026-07-05) — legenda ASCII autorevole

Ispezione dell'installazione (`C:\Program Files (x86)\Steam\steamapps\common\Illfloor`)
e dei flag CLI dell'eseguibile:

- `illfloor.exe --listascii` stampa la **legenda ASCII completa e autorevole**
  (salvata in `floorplan-ascii-ufficiale.txt`). È **hardcoded** nel binario.
- La legenda importabile = terreni (muri/pavimenti/liquidi/biomi) + **solo 3 icone**:
  `D = Door`, `B = Bush`, `T = Tree`. Sezione `Icons:` in fondo alla lista.
- **Nessun carattere per i mobili** (tavolo/sedia/cassa/letto...): non importabili via ASCII.
- `t = Sandstone Wall` → spiega perché nel test `t` diede una chiazza di terreno.
- **Esperimento:** aggiunto un terrain custom in `%AppData%\Roaming\illfloor\terrain\Indoor\`
  e rilanciato `--listascii`: il custom NON riceve un carattere (conteggio invariato).
  → la legenda NON è estendibile. Terreni/icone custom sono solo paint/place-by-hand.
- Altri flag CLI presenti: `--importascii=X`, `--export=X`. Un test headless di
  import+export non ha prodotto il PNG (probabilmente serve il contesto grafico/GUI):
  l'export automatico resta un possibile approfondimento futuro, non affidabile ora.

**Conclusione:** ESITO B confermato in modo definitivo. Correzioni applicate a
`legend-chars.txt`/`floorplan-legend.md` con i caratteri reali (aggiunto `x` =
pavimento di legno; `D`/`T`/`B` confermati importabili).
