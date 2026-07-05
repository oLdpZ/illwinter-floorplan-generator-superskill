---
name: mappa
description: Genera l'ambiente arredato di una nuova area DCC come file ASCII per Illwinter Floorplan e ne salva la nota nel vault. Usa quando l'utente vuole creare/generare una mappa, un'area o un ambiente di gioco per la campagna solo DCC.
---

# Skill `/mappa` — genera un'area arredata per la campagna solo DCC

Genera l'**ambiente di gioco** (architettura + arredo) di una nuova area come
griglia ASCII importabile in Illwinter's Floorplan Generator, e salva la nota
Giudice in Obsidian seguendo le convenzioni del vault. **Non generare mostri**:
lasciane un placeholder (l'utente li aggiunge su Roll20).

## Riferimenti (leggili prima di generare)
- Caratteri architettura (Floorplan): `.claude/skills/mappa/reference/floorplan-legend.md`
- Set autorevole caratteri legali: `.claude/skills/mappa/reference/legend-chars.txt`
- Caratteri arredo (nostri): `.claude/skills/mappa/reference/furniture-legend.txt`
- Esito test import + ricetta CLI: `.claude/skills/mappa/reference/FASE0-esito.md`
- Icone custom generate (versionate): `Mappe/icons_custom/` (+ copia in
  `<Illfloor>\data\icons\Furniture\` per usarle anche a mano nell'app)

## Come funziona (due livelli)
La mappa si costruisce su DUE griglie ASCII della **stessa dimensione**:
1. **Architettura** — caratteri di Floorplan (`legend-chars.txt`): muri, pavimenti,
   porte, alberi/cespugli, acqua/lava. Diventa il PNG base, esportato in automatico
   via CLI (`floorplan_export.py`). NON mettere mobili qui.
2. **Arredo** — caratteri nostri (`furniture-legend.txt`): `t`=tavolo, `h`=sedia,
   `c`=cassa, `e`=letto, `f`=focolare… Vengono **sovrapposti** al PNG base con
   Pillow (`floorplan_furnish.py`), centrati sulla cella. Floorplan NON importa i
   mobili via ASCII: li compone la nostra pipeline.

Le due griglie sono allineate cella-per-cella (ogni cella = 64px nel PNG).

**Oggetto mancante?** Se l'arredo che serve non esiste tra le icone (stock Illfloor
o `Mappe/icons_custom/`), lo si **genera con Canva** e lo si adatta a icona TGA con
`_scripts/cutout_canva.py` (vedi step 2b). Cosi' la mappa non e' limitata alle icone
di serie.

## Flusso

### 1. Raccogli gli input (una domanda alla volta, con default)
- Lettera area (`A`, `B`, …) e **nome** (es. "Cucina della Torre").
- Funzione/tema (es. cucina, cripta, sala del trono, cava allagata).
- Dimensione griglia (default 12×12).
- Tono/atmosfera (una frase).

### 2. Disegna le due griglie (stessa dimensione!)
**Architettura** — solo caratteri di `legend-chars.txt`:
- racchiudi le stanze con muri (`W`/`O`), riempi con un pavimento coerente col
  tema (`.` caverna, `:` pietra, `x` legno, `M` marmo, `L` ciottoli, `G` granito,
  `C` scacchi), metti `D` alle porte, `~`/`r`/`l` per acqua/fiume/lava, `T`/`B` per verde.

**Arredo** — solo caratteri di `furniture-legend.txt`; `.` = cella vuota:
- stessa larghezza e altezza della griglia architettura (allineamento cella-per-cella);
- posiziona i mobili sulle celle di pavimento (non dentro i muri).

### 2b. Oggetto mancante → genera con Canva e adattalo a icona TGA
Fallo **solo** se un oggetto dell'arredo non esiste gia' (né tra le icone stock di
Illfloor in `<Illfloor>\data\icons\**`, né in `Mappe/icons_custom/`). Altrimenti usa
il carattere esistente e salta questo step.

1. **Genera l'art in Canva** (MCP `canva`): `generate-design` con un prompt che chieda
   un **soggetto singolo isolato** su **sfondo piatto e uniforme**, *niente testo,
   niente cornice, niente scena*. Poi `create-design-from-candidate` sul candidato
   scelto dall'utente e `export-design` in **PNG** (NON serve trasparente).
   > ⚠️ Canva piano Free **non** esporta PNG con sfondo trasparente: la trasparenza
   > la ricava lo step successivo. Non perdere tempo con `transparent_background`.
2. **Adatta a icona TGA** con lo script (scontorno robusto region-growing dai bordi:
   rende trasparente solo lo sfondo connesso al bordo, preserva le aree dello stesso
   colore ma racchiuse dalla figura):
   ```
   python _scripts/cutout_canva.py "<canva_export.png>" "Mappe/icons_custom/<nome>.tga" \
       --height 168 --tol 40 \
       --also "C:/Program Files (x86)/Steam/steamapps/common/Illfloor/data/icons/Furniture/<nome>.tga"
   ```
   `--height` = altezza in px (cella=64px; ~168 ≈ 2.6 celle). `--tol` = tolleranza
   colore sfondo (alza se resta alone, abbassa se "mangia" la figura). `--also` copia
   il TGA anche nella cartella di Floorplan (usabile a mano nell'app).
   Verifica il risultato compositandolo su una scacchiera prima di proseguire.
3. **Registra il carattere** in `furniture-legend.txt`: riga `X <nome> <etichetta>`
   (senza `.tga`), con `X` un carattere libero. Poi usalo nella griglia arredo.

### 3. Scrivi e valida i file ASCII
- Scrivi `Mappe/Area <L> - <Nome>.txt` (architettura) e
  `Mappe/Area <L> - <Nome>.arredo.txt` (arredo, `.` per le celle vuote).
- Valida l'architettura:
  `python _scripts/validate_grid.py "Mappe/Area <L> - <Nome>.txt" --legend ".claude/skills/mappa/reference/legend-chars.txt"`
- Se l'output NON è `OK`, correggi e ripeti. (Il livello arredo lo valida lo step 3c.)

### 3b. Genera il PNG dell'architettura (automatico, headless)
```
python _scripts/floorplan_export.py "Mappe/Area <L> - <Nome>.txt" "Mappe/Area <L> - <Nome>.png"
```
Lo script lancia `illfloor.exe --nosteam --importascii=... --export=...` con la
working directory corretta (root di Illfloor). Se esce `OK`, il PNG base è pronto.
Se serve un percorso `illfloor.exe` diverso, passa `--exe "<path>"`.

### 3c. Sovrapponi l'arredo (automatico)
```
python _scripts/floorplan_furnish.py "Mappe/Area <L> - <Nome>.arredo.txt" "Mappe/Area <L> - <Nome>.png" "Mappe/Area <L> - <Nome>.png"
```
Compone i mobili sul PNG base e sovrascrive il PNG finale. Valida da sé il livello
arredo (dimensioni coerenti + caratteri noti); se `INVALID`, correggi la griglia
arredo e ripeti. Se non c'è arredo, salta questo step (il PNG resta l'architettura).

### 4. Scrivi la nota Giudice
Crea `Avventura/Area <L> - <Nome>.md` con questo schema (rispetta le convenzioni
del vault):

```markdown
---
tipo: avventura-giudice
spoiler: true
area: <L>
stato: in-corso
---

# Area <L> — <Nome> ⚠️

> Note Giudice (SPOILER). · [[00 Indice]]

<1-2 frasi di contesto/atmosfera dal tono richiesto>

![[Area <L> - <Nome>.png]]

## Read-aloud (tradotto)
<descrizione immersiva da leggere al giocatore>

## Stanze e arredo
| # | Funzione | Materiali (muri/pavimento) | Arredo / oggetti | Note GM |
|---|----------|----------------------------|------------------|---------|
| 1 | <es. cucina> | pietra / ciottoli | tavolo, 2 casse, focolare | <gancio> |

<!-- L'arredo è già composto sul PNG (step 3c). Questa colonna riepiloga i mobili
     per il Giudice. -->

## Mostri
> **Da aggiungere su Roll20.** (Questa skill non genera statblock.)

## Segreti / tesori (opzionale)
- <eventuali passaggi nascosti, bottino ambientale>

## Esito (partita)
- <vuoto: si compila giocando>
```

### 5. Mostra il risultato all'utente
Il PNG finale (architettura + arredo) è già generato in automatico dagli step 3b/3c:
mostra all'utente il percorso `Mappe/Area <L> - <Nome>.png`.

Rifiniture opzionali a mano (solo se l'utente vuole): aprire il `.txt` in Floorplan
(`File → Import ASCII Dungeon`), aggiungere/spostare icone (`i` / `ctrl+i`) e
ri-esportare. Non necessario per il flusso standard.

### 6. Aggiorna l'indice (append idempotente)
In `00 Indice.md`, sotto una sezione `## 🗺️ Aree generate` (creala se manca),
aggiungi `- [[Area <L> - <Nome>]]` solo se non è già presente.
