from pathlib import Path

from sheer_audit.config import ScanConfig
from sheer_audit.scan.repo import collect_python_files


def test_collect_python_files_respects_include_exclude_and_test_filters(tmp_path: Path) -> None:
    src = tmp_path / "src"
    tests = tmp_path / "tests"
    build = tmp_path / "build"

    src.mkdir()
    tests.mkdir()
    build.mkdir()

    (src / "main.py").write_text("print('ok')\n")
    (tests / "test_main.py").write_text("def test_x():\n    assert True\n")
    (build / "generated.py").write_text("pass\n")

    cfg = ScanConfig(include_dirs=["src", "tests", "build"], exclude_dirs=["build"], include_tests=False)

    files = collect_python_files(str(tmp_path), cfg)

    assert files == ["src/main.py"]


def test_collect_python_files_ignores_include_dir_outside_root(tmp_path: Path) -> None:
    (tmp_path / "safe.py").write_text("pass\n")

    cfg = ScanConfig(include_dirs=[".", "../"], exclude_dirs=[], include_tests=True)
    files = collect_python_files(str(tmp_path), cfg)

    assert files == ["safe.py"]
