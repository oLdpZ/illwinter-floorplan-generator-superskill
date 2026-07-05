"""Rende trasparente lo sfondo di un'immagine generata da Canva e la adatta come
icona TGA per Illwinter Floorplan (pipeline arredo della skill /mappa).

Perche' serve: Canva sul piano Free NON esporta PNG con sfondo trasparente, quindi
la trasparenza va ricavata dopo. Un color-key ingenuo pero' "buca" la figura quando
questa condivide colori con lo sfondo (caso reale: le vesti del cadavere erano
identiche all'oliva dello sfondo). La soluzione robusta e' un REGION-GROWING dai
bordi: si rimuove solo lo sfondo *connesso al bordo*; ogni area dello stesso colore
ma RACCHIUSA dalla figura non e' raggiungibile e resta opaca.

Uso:
  python _scripts/cutout_canva.py <src.png> <out.tga> \\
      [--height 168] [--tol 40] [--also <secondo_path.tga>]

- <src.png>   PNG esportato da Canva (sfondo piatto/uniforme).
- <out.tga>   TGA RGBA risultante (es. Mappe/icons_custom/<nome>.tga).
- --height    altezza in px del TGA (una cella = 64px; ~168 = 2.6 celle).
- --tol       tolleranza colore (distanza L1) per considerare un pixel "sfondo".
- --also      copia opzionale del TGA in una seconda cartella
              (es. <Illfloor>\\data\\icons\\Furniture per usarlo anche nell'app).

Exit code 0 = ok; 1 = errore. Richiede Pillow e numpy.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


def background_palette(
    arr: np.ndarray, bucket: int = 16, max_colors: int = 48, min_frac: float = 0.02
) -> np.ndarray:
    """Colori rappresentativi dello sfondo, campionati dall'anello di bordo.

    I pixel di bordo sono raggruppati in bucket (per de-duplicare gradiente/rumore);
    per ogni bucket si usa il colore MEDIO reale (non il floor del bucket, che
    falserebbe la distanza). Si scartano i bucket rari (< min_frac dei pixel di
    bordo): sono tipicamente intrusioni della figura che tocca il bordo (es. il
    palo in cima). Si tengono i piu' frequenti, fino a max_colors.
    """
    h, w, _ = arr.shape
    border = np.concatenate([
        arr[0, :, :], arr[h - 1, :, :], arr[:, 0, :], arr[:, w - 1, :]
    ]).astype(np.int16)
    total = border.shape[0]
    keys, inv, counts = np.unique(border // bucket, axis=0, return_inverse=True, return_counts=True)
    means = np.stack([border[inv == i].mean(axis=0) for i in range(len(keys))])
    keep = counts >= max(1, int(min_frac * total))
    if not keep.any():
        keep[counts.argmax()] = True
    means, counts = means[keep], counts[keep]
    order = np.argsort(counts)[::-1][:max_colors]
    return means[order].round().astype(np.int16)


def background_mask(arr: np.ndarray, palette: np.ndarray, tol: float) -> np.ndarray:
    """True dove c'e' sfondo connesso al bordo (region-growing dai bordi).

    Gate: un pixel e' 'sfondo-simile' se la distanza L1 dal colore di palette piu'
    vicino e' <= tol. Il BFS parte dal bordo e si propaga solo tra pixel gated,
    quindi lo sfondo racchiuso dalla figura NON viene raggiunto.
    """
    h, w, _ = arr.shape
    a = arr.astype(np.int16)
    mind = np.full((h, w), np.inf)
    for p in palette:
        d = np.abs(a - p).sum(axis=2)
        mind = np.minimum(mind, d)
    gate = mind <= tol

    bg = np.zeros((h, w), dtype=bool)
    dq: deque[tuple[int, int]] = deque()

    def seed(y: int, x: int) -> None:
        if gate[y, x] and not bg[y, x]:
            bg[y, x] = True
            dq.append((y, x))

    for x in range(w):
        seed(0, x)
        seed(h - 1, x)
    for y in range(h):
        seed(y, 0)
        seed(y, w - 1)

    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and gate[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True
                dq.append((ny, nx))
    return bg


def cutout(im: Image.Image, tol: float = 40.0, crop: bool = True) -> Image.Image:
    """Ritorna l'immagine RGBA con lo sfondo (connesso al bordo) reso trasparente."""
    arr = np.asarray(im.convert("RGB"))
    palette = background_palette(arr)
    bg = background_mask(arr, palette, tol)
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    rgba = np.dstack([arr.astype(np.uint8), alpha])
    out = Image.fromarray(rgba, "RGBA")
    if crop:
        ys, xs = np.where(alpha > 0)
        if len(xs):
            out = out.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    return out


def resize_to_height(im: Image.Image, height: int) -> Image.Image:
    """Ridimensiona mantenendo l'aspect ratio all'altezza data (in px)."""
    w = max(1, round(im.width * height / im.height))
    return im.resize((w, height), Image.LANCZOS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scontorna un PNG Canva e lo salva come TGA per Floorplan.")
    parser.add_argument("src", type=Path, help="PNG sorgente esportato da Canva")
    parser.add_argument("out", type=Path, help="TGA di output (RGBA)")
    parser.add_argument("--height", type=int, default=168, help="altezza in px (cella=64px). Default %(default)s")
    parser.add_argument("--tol", type=float, default=40.0, help="tolleranza colore L1 per lo sfondo. Default %(default)s")
    parser.add_argument("--also", type=Path, default=None, help="copia opzionale del TGA in una seconda cartella")
    args = parser.parse_args(argv)

    if not args.src.is_file():
        print(f"ERRORE: sorgente non trovata: {args.src}", file=sys.stderr)
        return 1
    im = Image.open(args.src)
    cut = cutout(im, tol=args.tol)
    cut = resize_to_height(cut, args.height)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cut.save(args.out)
    msg = f"OK: {args.out} ({cut.size[0]}x{cut.size[1]} RGBA)"
    if args.also is not None:
        args.also.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.out, args.also)
        msg += f" + copia {args.also}"
    print(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
