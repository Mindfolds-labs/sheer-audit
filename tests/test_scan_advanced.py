from pathlib import Path

from sheer_audit.scan.advanced import SheerAdvancedEngine


def test_generate_cartesian_and_errors(tmp_path: Path) -> None:
    source = tmp_path / "mod.py"
    source.write_text(
        """
class A:
    def run(self):
        if True:
            return 1
        pass
""".strip()
        + "\n"
    )

    engine = SheerAdvancedEngine(str(tmp_path))

    mapping = engine.generate_cartesian_map()
    errors = engine.detect_structural_errors()

    assert mapping["components"]
    assert any(item["kind"] == "class" for item in mapping["components"])
    assert any(err["type"] == "DeadBranch" for err in errors)
