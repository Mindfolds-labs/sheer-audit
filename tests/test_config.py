from pathlib import Path

from sheer_audit.config import load_config


def test_load_config_supports_uml_sequence_table(tmp_path: Path) -> None:
    cfg_file = tmp_path / "sheer.toml"
    cfg_file.write_text(
        """
[project]
name = "Demo"

[scan]
include_dirs = ["."]
exclude_dirs = []

[uml]
engine = "plantuml"
output_dir = "artifacts/uml"

[uml.sequence]
max_depth = 42
"""
    )

    cfg = load_config(str(cfg_file))

    assert cfg.sequence.max_depth == 42
