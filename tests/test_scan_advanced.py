from pathlib import Path

from sheer_audit.scan.advanced import SheerAdvancedEngine


def test_generate_cartesian_map_builds_complexity_vector(tmp_path: Path) -> None:
    source = tmp_path / "mod.py"
    source.write_text(
        """
class A:
    @staticmethod
    def run():
        for _ in range(1):
            if True:
                return 1
        return 0
""".strip()
        + "\n"
    )

    engine = SheerAdvancedEngine(str(tmp_path))
    mapping = engine.generate_cartesian_map()

    assert mapping["coordinates"]
    assert any(item["kind"] == "ClassDef" for item in mapping["coordinates"])
    assert mapping["complexity_total"] > 0

    run_component = next(item for item in mapping["complexity_vector"] if item["x"].endswith(":run"))
    assert run_component["stage_impact"] > 0
    assert run_component["partial_derivative"] >= run_component["stage_impact"]


def test_detect_prohibited_reachability_from_core_to_io(tmp_path: Path) -> None:
    core_dir = tmp_path / "core"
    core_dir.mkdir()
    (core_dir / "__init__.py").write_text("\n")
    (core_dir / "domain.py").write_text("from db import adapter\n")

    db_dir = tmp_path / "db"
    db_dir.mkdir()
    (db_dir / "__init__.py").write_text("\n")
    (db_dir / "adapter.py").write_text("def save():\n    return 'ok'\n")

    engine = SheerAdvancedEngine(str(tmp_path))
    errors = engine.detect_structural_errors()

    assert any(err["type"] == "ForbiddenReachability" for err in errors)
