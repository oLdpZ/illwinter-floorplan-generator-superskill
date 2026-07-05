"""Sovrappone i mobili (livello arredo) al PNG dell'architettura di Floorplan.

Due livelli:
  1. griglia architettura -> PNG base (via floorplan_export.py, caratteri Floorplan);
  2. griglia arredo (stessa dimensione) -> mobili sovrapposti qui (caratteri nostri).

Ogni cella del PNG e' 64x64 px (l'export di Floorplan produce col*64 x righe*64).
Le icone-mobile (TGA in <Illfloor>\\data\\icons\\Furniture) vengono CENTRATE sulla
cella: 64x64 = 1 cella; 128x128 = 2x2 (sconfina sui vicini); 32x32 = piu' piccola.

Uso:
  python _scripts/floorplan_furnish.py <arredo.txt> <base.png> <out.png> \\
      [--legend <furniture-legend.txt>] [--icons <cartella Furniture>] [--cell 64]

Exit code 0 = PNG arredato creato; 1 = errore. Richiede Pillow.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_LEGEND = Path(".claude/skills/mappa/reference/furniture-legend.txt")
DEFAULT_ICONS = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Illfloor\data\icons\Furniture"
)
EMPTY = {".", " "}


def load_furniture_map(legend_path: Path) -> dict[str, str]:
    """char -> nome file TGA (con estensione .tga). Ignora commenti/righe vuote."""
    mapping: dict[str, str] = {}
    for raw in legend_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        parts = raw.split()
        if len(parts) < 2:
            continue
        ch, tga = parts[0], parts[1]
        if not tga.lower().endswith(".tga"):
            tga += ".tga"
        mapping[ch] = tga
    return mapping


def read_grid(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def paste_topleft(row: int, col: int, icon_w: int, icon_h: int, cell: int = 64) -> tuple[int, int]:
    """Angolo in alto-sinistra per CENTRARE un'icona sulla cella (row, col)."""
    center_x = col * cell + cell // 2
    center_y = row * cell + cell // 2
    return (center_x - icon_w // 2, center_y - icon_h // 2)


def validate_layer(grid: list[str], mapping: dict[str, str], base_size: tuple[int, int], cell: int = 64) -> list[str]:
    """Errori: dimensioni coerenti col PNG base e caratteri noti."""
    errors: list[str] = []
    if not grid:
        return errors  # nessun mobile: valido (PNG resta l'architettura)
    width = len(grid[0])
    for i, line in enumerate(grid, start=1):
        if len(line) != width:
            errors.append(f"riga {i}: lunghezza {len(line)}, attesa {width} (griglia non rettangolare)")
        for j, ch in enumerate(line, start=1):
            if ch not in EMPTY and ch not in mapping:
                errors.append(f"riga {i} col {j}: carattere mobile sconosciuto {ch!r}")
    exp_w, exp_h = width * cell, len(grid) * cell
    if base_size != (exp_w, exp_h):
        errors.append(
            f"il PNG base {base_size} non combacia con la griglia arredo "
            f"({exp_w}x{exp_h} attesi per {width}x{len(grid)} celle)"
        )
    return errors


def furnish(arredo: Path, base_png: Path, out_png: Path, legend: Path, icons_dir: Path, cell: int = 64) -> int:
    try:
        from PIL import Image
    except ImportError:
        print("ERRORE: serve Pillow (python -m pip install pillow)", file=sys.stderr)
        return 1
    mapping = load_furniture_map(legend)
    grid = read_grid(arredo)
    base = Image.open(base_png).convert("RGBA")
    errors = validate_layer(grid, mapping, base.size, cell)
    if errors:
        print(f"INVALID: livello arredo {arredo} ({len(errors)} error(i))", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    placed = 0
    for r, line in enumerate(grid):
        for c, ch in enumerate(line):
            if ch in EMPTY:
                continue
            icon_path = icons_dir / mapping[ch]
            if not icon_path.is_file():
                print(f"ERRORE: TGA non trovata: {icon_path}", file=sys.stderr)
                return 1
            icon = Image.open(icon_path).convert("RGBA")
            base.alpha_composite(icon, paste_topleft(r, c, icon.width, icon.height, cell))
            placed += 1
    out_png.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out_png)
    print(f"OK: {out_png} ({placed} mobili sovrapposti)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sovrappone i mobili al PNG dell'architettura.")
    parser.add_argument("arredo", type=Path, help="griglia arredo .txt (stessa dimensione dell'architettura)")
    parser.add_argument("base", type=Path, help="PNG dell'architettura (da floorplan_export.py)")
    parser.add_argument("out", type=Path, help="PNG di output arredato")
    parser.add_argument("--legend", type=Path, default=DEFAULT_LEGEND)
    parser.add_argument("--icons", type=Path, default=DEFAULT_ICONS)
    parser.add_argument("--cell", type=int, default=64)
    args = parser.parse_args(argv)
    return furnish(args.arredo, args.base, args.out, args.legend, args.icons, args.cell)


if __name__ == "__main__":
    raise SystemExit(main())
