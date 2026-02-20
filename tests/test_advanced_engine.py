from pathlib import Path

from sheer_audit.scan.advanced import SheerAdvancedEngine


def test_generate_cartesian_map_and_detect_errors(tmp_path: Path) -> None:
    src = tmp_path / "pkg"
    src.mkdir()
    (src / "a.py").write_text("def alpha():\n    return 1\n")
    (src / "b.py").write_text("from pkg import a\n")

    engine = SheerAdvancedEngine(str(tmp_path))

    mapping = engine.generate_cartesian_map()
    errors = engine.detect_structural_errors()

    assert mapping["max_depth"] >= 0
    assert any(item["x"].endswith(":alpha") for item in mapping["coordinates"])
    assert errors == []


def test_detect_structural_syntax_error(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text("def oops(:\n    pass\n")

    engine = SheerAdvancedEngine(str(tmp_path))
    errors = engine.detect_structural_errors()

    assert len(errors) == 1
    assert errors[0]["type"] == "SyntaxError"
