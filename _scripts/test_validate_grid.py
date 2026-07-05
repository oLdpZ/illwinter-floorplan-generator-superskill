from pathlib import Path

import validate_grid as vg


def test_rectangular_valid():
    lines = ["WWW", "W.W", "WWW"]
    legal = set("W. ")
    assert vg.validate(lines, legal) == []


def test_non_rectangular_flagged():
    lines = ["WWW", "W.", "WWW"]
    legal = set("W. ")
    errors = vg.validate(lines, legal)
    assert any("rectangular" in e for e in errors)


def test_illegal_char_flagged():
    lines = ["WWZ"]
    legal = set("W ")
    errors = vg.validate(lines, legal)
    assert any("illegal character" in e and "Z" in e for e in errors)


def test_empty_grid_flagged():
    assert vg.validate([], set("W ")) == ["grid is empty (no rows)"]


def test_load_legal_chars_parses_first_char_and_skips_comments(tmp_path):
    p = tmp_path / "legend-chars.txt"
    p.write_text("# commento\nW muro di pietra\n. pavimento caverna\n", encoding="utf-8")
    legal = vg.load_legal_chars(p)
    assert {"W", ".", " "} <= legal
    assert "#" not in legal


def test_read_grid_handles_crlf(tmp_path):
    p = tmp_path / "grid.txt"
    p.write_bytes(b"WWW\r\nW.W\r\nWWW\r\n")
    assert vg.read_grid(p) == ["WWW", "W.W", "WWW"]


def test_main_returns_zero_on_valid(tmp_path):
    legend = tmp_path / "legend-chars.txt"
    legend.write_text("W muro\n. pavimento\n", encoding="utf-8")
    grid = tmp_path / "g.txt"
    grid.write_text("WWW\nW.W\nWWW\n", encoding="utf-8")
    assert vg.main([str(grid), "--legend", str(legend)]) == 0


def test_main_returns_one_on_invalid(tmp_path):
    legend = tmp_path / "legend-chars.txt"
    legend.write_text("W muro\n. pavimento\n", encoding="utf-8")
    grid = tmp_path / "g.txt"
    grid.write_text("WWZ\nW.W\n", encoding="utf-8")
    assert vg.main([str(grid), "--legend", str(legend)]) == 1
