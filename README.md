# Illwinter's Floorplan Generator superskill

A [Claude Code](https://claude.com/claude-code) skill (`/mappa`) that generates a
**furnished game area** for a tabletop RPG campaign as an ASCII grid importable into
[Illwinter's Floorplan Generator](https://www.illwinter.com/floorplan/), auto-exports
the battlemap PNG, composites furniture on top, and — when an object doesn't exist as
a stock icon — **generates it with Canva** and adapts it into a transparent Floorplan
icon.

Built for a solo *Dungeon Crawl Classics* campaign kept in an Obsidian vault, but the
map-generation pipeline is generic.

## How it works — two aligned ASCII layers

1. **Architecture** — Floorplan characters (walls, floors, doors, water/lava, trees).
   Rendered to a base PNG by exporting through Illwinter's Floorplan (`floorplan_export.py`).
2. **Furniture** — our own characters, **composited** onto the base PNG with Pillow
   (`floorplan_furnish.py`), centered per cell. Floorplan does not import furniture via
   ASCII, so our pipeline overlays it.

Both grids share the same dimensions; each cell is 64×64 px in the exported PNG.

### Missing object? Generate it with Canva → TGA icon

When a needed piece of furniture exists neither among Illwinter's stock icons nor in
`Mappe/icons_custom/`, the skill:

1. generates the art in **Canva** (isolated subject on a flat background),
2. adapts it into a transparent TGA icon with **`cutout_canva.py`**,
3. registers a character in `furniture-legend.txt` and places it in the furniture grid.

> ⚠️ Canva's Free plan **cannot** export PNGs with a transparent background, so
> transparency is recovered afterwards by `cutout_canva.py`. It uses a **region-growing
> flood from the borders**: only background *connected to the edge* is removed, so areas
> that happen to share the background color but are **enclosed by the figure** stay
> opaque (a naïve chroma-key would punch holes through the subject).

## Repository layout

```
.claude/skills/mappa/
  SKILL.md                     # the /mappa skill (workflow instructions)
  reference/
    legend-chars.txt           # authoritative legal architecture characters
    floorplan-legend.md        # human doc: char → Floorplan tile
    floorplan-ascii-ufficiale.txt
    furniture-legend.txt       # our furniture characters → TGA icon names
    FASE0-esito.md             # import micro-test outcome / CLI recipe
_scripts/
  validate_grid.py             # validates an architecture ASCII grid (stdlib only)
  floorplan_export.py          # headless PNG export via illfloor.exe
  floorplan_furnish.py         # composites furniture TGAs onto the base PNG (Pillow)
  cutout_canva.py              # Canva PNG → transparent, resized TGA icon
  test_*.py                    # pytest suites
```

## Requirements

- Python 3.10+
- [Pillow](https://python-pillow.org/) and [NumPy](https://numpy.org/) (see `requirements.txt`)
- [Illwinter's Floorplan Generator](https://www.illwinter.com/floorplan/) for PNG export
  and (optionally) manual icon placement
- The `/mappa` skill runs inside a [Claude Code](https://claude.com/claude-code) project;
  the Canva step uses the Canva MCP server

```bash
pip install -r requirements.txt
```

## Using the scripts standalone

```bash
# validate an architecture grid
python _scripts/validate_grid.py area.txt --legend .claude/skills/mappa/reference/legend-chars.txt

# export the base PNG (headless) through Illwinter's Floorplan
python _scripts/floorplan_export.py area.txt area.png

# composite the furniture layer
python _scripts/floorplan_furnish.py area.arredo.txt area.png area.png

# turn a Canva export into a transparent TGA icon (~2.6 cells tall)
python _scripts/cutout_canva.py canva_export.png Mappe/icons_custom/object.tga \
    --height 168 --tol 40 --also "<Illfloor>/data/icons/Furniture/object.tga"
```

## Tests

```bash
python -m pytest _scripts/ -q
```

## Installing the skill into your vault

Copy `.claude/skills/mappa/` and `_scripts/` into the root of an Obsidian vault that is
a Claude Code project, then invoke `/mappa`. Paths in the scripts are relative to the
vault root; `floorplan_furnish.py` and `cutout_canva.py` default to a Windows Steam
install of Illwinter's Floorplan — override with `--icons` / `--also` as needed.

## Notes

The skill's instructions and reference docs are written in Italian (the campaign's
language); the code and this README are in English.

## License

[MIT](LICENSE) © 2026 Pedro José Zei (oLdpZ)
