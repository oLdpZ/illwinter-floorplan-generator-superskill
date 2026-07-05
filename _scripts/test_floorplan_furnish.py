from pathlib import Path

import floorplan_furnish as ff


def test_paste_centers_single_cell_icon():
    # icona 64x64 nella cella (0,0) -> angolo (0,0)
    assert ff.paste_topleft(0, 0, 64, 64) == (0, 0)
    # cella (1,2) -> centro (2*64+32, 1*64+32) meno 32 = (128, 64)
    assert ff.paste_topleft(1, 2, 64, 64) == (128, 64)


def test_paste_centers_small_and_large_icons():
    # icona 32x32 nella cella (0,0): centro cella (32,32) - 16 = (16,16)
    assert ff.paste_topleft(0, 0, 32, 32) == (16, 16)
    # icona 128x128 (letto 2x2) nella cella (0,0): centro (32,32) - 64 = (-32,-32)
    assert ff.paste_topleft(0, 0, 128, 128) == (-32, -32)


def test_load_furniture_map_appends_tga_and_skips_comments(tmp_path):
    p = tmp_path / "furniture-legend.txt"
    p.write_text("# commento\nt table_1 tavolo\nh chair_1 sedia\n", encoding="utf-8")
    m = ff.load_furniture_map(p)
    assert m["t"] == "table_1.tga"
    assert m["h"] == "chair_1.tga"
    assert "#" not in m


def test_validate_layer_flags_unknown_char():
    grid = ["t.", ".Z"]
    errors = ff.validate_layer(grid, {"t": "table_1.tga"}, (2 * 64, 2 * 64))
    assert any("sconosciuto" in e and "Z" in e for e in errors)


def test_validate_layer_flags_size_mismatch():
    grid = ["t.", ".."]
    errors = ff.validate_layer(grid, {"t": "table_1.tga"}, (999, 999))
    assert any("non combacia" in e for e in errors)


def test_validate_layer_ok_on_matching_dims():
    grid = ["t.", ".."]
    assert ff.validate_layer(grid, {"t": "table_1.tga"}, (2 * 64, 2 * 64)) == []


def test_empty_grid_is_valid():
    assert ff.validate_layer([], {"t": "table_1.tga"}, (128, 128)) == []
