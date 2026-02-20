from pathlib import Path

from sheer_audit.governance.axisfolds import AxisFoldsLock


def test_axisfolds_generates_folds_file(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "demo"
dependencies = ["networkx>=3.2.1", "jinja2==3.1.3"]
"""
    )

    out = tmp_path / "requirements.folds"
    lock = AxisFoldsLock()
    generated = lock.write_folds_file(output_path=str(out), pyproject_path=str(pyproject))

    assert generated.endswith("requirements.folds")
    content = out.read_text()
    assert "networkx==3.2.1" in content
    assert "jinja2==3.1.3" in content
