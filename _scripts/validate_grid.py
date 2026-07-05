"""Valida una griglia ASCII per l'import in Illwinter Floorplan.

Controlli:
  1. Griglia non vuota (almeno una riga).
  2. Rettangolare: tutte le righe della stessa lunghezza.
  3. Caratteri legali: ogni carattere appartiene al set della legenda.

Uso:
  python _scripts/validate_grid.py <grid.txt> [--legend <legend-chars.txt>]

Exit code 0 = valida; 1 = errori (stampati su stderr).
Solo libreria standard di Python.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_LEGEND = Path(".claude/skills/mappa/reference/legend-chars.txt")


def load_legal_chars(legend_path: Path) -> set[str]:
    """Set dei caratteri legali dal file di legenda.

    Ogni riga non vuota il cui primo carattere non e' '#' contribuisce il
    suo PRIMO carattere. Le righe che iniziano con '#' sono commenti.
    Lo spazio e' sempre legale (muro-caverna/vuoto di Floorplan).
    """
    legal: set[str] = {" "}
    for raw in legend_path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.lstrip().startswith("#"):
            continue
        legal.add(raw[0])
    return legal


def read_grid(grid_path: Path) -> list[str]:
    """Legge la griglia in righe, gestendo CRLF/LF e senza riga fantasma finale."""
    return grid_path.read_text(encoding="utf-8").splitlines()


def validate(lines: list[str], legal: set[str]) -> list[str]:
    """Ritorna la lista degli errori. Lista vuota = griglia valida."""
    errors: list[str] = []
    if not lines:
        errors.append("grid is empty (no rows)")
        return errors
    width = len(lines[0])
    for i, line in enumerate(lines, start=1):
        if len(line) != width:
            errors.append(
                f"row {i} has length {len(line)}, expected {width} "
                f"(grid must be rectangular)"
            )
        for j, ch in enumerate(line, start=1):
            if ch not in legal:
                errors.append(f"row {i} col {j}: illegal character {ch!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida una griglia ASCII per Floorplan.")
    parser.add_argument("grid", type=Path, help="percorso del file .txt della griglia")
    parser.add_argument(
        "--legend",
        type=Path,
        default=DEFAULT_LEGEND,
        help="percorso di legend-chars.txt (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    legal = load_legal_chars(args.legend)
    lines = read_grid(args.grid)
    errors = validate(lines, legal)
    if errors:
        print(f"INVALID: {args.grid} ({len(errors)} error(s))", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: {args.grid} ({len(lines)} rows x {len(lines[0])} cols)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
