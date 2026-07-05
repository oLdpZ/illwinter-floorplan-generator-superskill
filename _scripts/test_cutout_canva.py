"""Test TDD per cutout_canva.py — scontorno generico di un'immagine Canva.

Proprieta' chiave: lo sfondo va reso trasparente partendo dai BORDI, ma un'area
dello STESSO colore dello sfondo che sia RACCHIUSA dalla figura deve restare opaca
(caso reale: le vesti del palo erano identiche all'oliva dello sfondo)."""
from pathlib import Path

import numpy as np
from PIL import Image

import cutout_canva as cc


def _synthetic() -> Image.Image:
    """40x40: sfondo (50,60,30). Cornice-figura rossa (200,50,50) da 10..29,
    spessore 3px. Interno racchiuso (16..23) ridipinto col colore dello sfondo."""
    bg = (50, 60, 30)
    fig = (200, 50, 50)
    arr = np.zeros((40, 40, 3), dtype=np.uint8)
    arr[:, :] = bg
    arr[10:30, 10:30] = fig            # blocco figura
    arr[16:24, 16:24] = bg             # buco interno = colore sfondo (racchiuso)
    return Image.fromarray(arr, "RGB")


def test_exterior_background_becomes_transparent():
    out = cc.cutout(_synthetic(), tol=20)
    # dopo il crop il contenuto parte da (0,0); controlliamo via maschera piena
    full = cc.cutout(_synthetic(), tol=20, crop=False)
    a = np.asarray(full)[:, :, 3]
    assert a[0, 0] == 0            # angolo = sfondo esterno -> trasparente
    assert a[5, 5] == 0


def test_figure_is_opaque():
    full = cc.cutout(_synthetic(), tol=20, crop=False)
    a = np.asarray(full)[:, :, 3]
    assert a[11, 11] == 255        # pixel della cornice rossa


def test_enclosed_background_is_preserved():
    """Il buco interno, pur avendo il colore dello sfondo, e' racchiuso -> opaco."""
    full = cc.cutout(_synthetic(), tol=20, crop=False)
    a = np.asarray(full)[:, :, 3]
    assert a[20, 20] == 255        # centro del buco interno


def test_crop_to_bounding_box():
    out = cc.cutout(_synthetic(), tol=20)      # crop=True default
    # bbox della figura 10..29 inclusi -> 20x20
    assert out.size == (20, 20)


def test_resize_to_height_keeps_aspect():
    im = Image.new("RGBA", (40, 80), (255, 0, 0, 255))
    r = cc.resize_to_height(im, 40)
    assert r.size == (20, 40)


def test_main_writes_rgba_tga_at_target_height(tmp_path):
    src = tmp_path / "src.png"
    _synthetic().save(src)
    out = tmp_path / "obj.tga"
    rc = cc.main([str(src), str(out), "--height", "60", "--tol", "20"])
    assert rc == 0
    assert out.is_file()
    im = Image.open(out)
    assert im.mode == "RGBA"
    assert im.height == 60


def test_main_also_copies_second_location(tmp_path):
    src = tmp_path / "src.png"
    _synthetic().save(src)
    out = tmp_path / "vault" / "obj.tga"
    also = tmp_path / "furniture" / "obj.tga"
    rc = cc.main([str(src), str(out), "--height", "60", "--tol", "20", "--also", str(also)])
    assert rc == 0
    assert out.is_file() and also.is_file()
    assert Image.open(also).height == 60
