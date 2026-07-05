"""Esporta una griglia ASCII in un PNG usando Illwinter's Floorplan Generator, headless.

Ricetta scoperta: l'eseguibile accetta i flag CLI
  illfloor.exe --nosteam --importascii=<grid.txt> --export=<out.png>
ed esce da solo (nessuna finestra), MA la working directory deve essere la root
di Illfloor (dove sta la cartella `data/`), altrimenti si blocca sull'errore
"font ... guifont.ttf not found".

Uso:
  python _scripts/floorplan_export.py <grid.txt> <out.png> [--exe <illfloor.exe>]

Genera SOLO l'architettura (muri/pavimenti/porte/alberi/cespugli via ASCII).
I mobili NON sono importabili via ASCII: si piazzano a mano nell'editor.

Exit code 0 = PNG creato; 1 = errore. Solo libreria standard di Python.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_EXE = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Illfloor\win64\illfloor.exe"
)


def export(grid: Path, out: Path, exe: Path, timeout: int = 60) -> int:
    if not exe.is_file():
        print(f"ERRORE: eseguibile non trovato: {exe}", file=sys.stderr)
        return 1
    if not grid.is_file():
        print(f"ERRORE: griglia non trovata: {grid}", file=sys.stderr)
        return 1
    workdir = exe.parent.parent  # root di Illfloor, dove sta data/
    grid_abs = grid.resolve()
    out_abs = out.resolve()
    out_abs.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(exe),
        "--nosteam",
        f"--importascii={grid_abs}",
        f"--export={out_abs}",
    ]
    try:
        proc = subprocess.run(cmd, cwd=str(workdir), timeout=timeout)
    except subprocess.TimeoutExpired:
        print(
            f"ERRORE: Floorplan non e' uscito entro {timeout}s (possibile dialogo "
            f"bloccante). Working dir usata: {workdir}",
            file=sys.stderr,
        )
        return 1
    if out_abs.is_file() and out_abs.stat().st_size > 0:
        print(f"OK: {out_abs} ({out_abs.stat().st_size} byte)")
        return 0
    print(
        f"ERRORE: nessun PNG prodotto (exit {proc.returncode}). "
        f"Controlla la working dir ({workdir}) e i percorsi.",
        file=sys.stderr,
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Esporta una griglia ASCII in PNG via Floorplan.")
    parser.add_argument("grid", type=Path, help="file .txt della griglia ASCII")
    parser.add_argument("out", type=Path, help="percorso del PNG di output")
    parser.add_argument("--exe", type=Path, default=DEFAULT_EXE, help="percorso di illfloor.exe (default: %(default)s)")
    parser.add_argument("--timeout", type=int, default=60, help="timeout in secondi (default: 60)")
    args = parser.parse_args(argv)
    return export(args.grid, args.out, args.exe, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
