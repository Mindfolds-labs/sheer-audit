from pathlib import Path

from typer.testing import CliRunner

from sheer_audit.cli import app


runner = CliRunner()


def test_analyze_blueprint_and_evolution_helpers(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pkg.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")

    vault = tmp_path / "audit.sheerdb"
    analysis = tmp_path / "component_analysis.json"
    graph = tmp_path / "graph.md"
    health = tmp_path / "health.json"
    blueprint = tmp_path / "blueprint.md"
    blueprint_diff = tmp_path / "blueprint_diff.md"

    analyze_result = runner.invoke(
        app,
        [
            "analyze",
            "--repo-path",
            str(repo),
            "--component",
            "pkg.py:alpha",
            "--output",
            str(analysis),
        ],
    )
    assert analyze_result.exit_code == 0
    assert analysis.exists()

    result_s1 = runner.invoke(
        app,
        [
            "snapshot",
            "--id",
            "s1",
            "--repo-path",
            str(repo),
            "--vault-path",
            str(vault),
        ],
    )
    assert result_s1.exit_code == 0

    (repo / "pkg.py").write_text("def alpha():\n    return 2\n", encoding="utf-8")

    result_s2 = runner.invoke(
        app,
        [
            "snapshot",
            "--id",
            "s2",
            "--repo-path",
            str(repo),
            "--vault-path",
            str(vault),
        ],
    )
    assert result_s2.exit_code == 0

    graph_result = runner.invoke(
        app,
        ["evolution-graph", "--output", str(graph), "--vault-path", str(vault)],
    )
    assert graph_result.exit_code == 0
    assert graph.exists()

    health_result = runner.invoke(
        app,
        ["evolution-health", "--output", str(health), "--vault-path", str(vault)],
    )
    assert health_result.exit_code == 0
    assert health.exists()

    blueprint_result = runner.invoke(
        app,
        [
            "blueprint",
            "generate",
            "--snapshot-id",
            "s2",
            "--vault-path",
            str(vault),
            "--output",
            str(blueprint),
        ],
    )
    assert blueprint_result.exit_code == 0
    assert blueprint.exists()

    blueprint_diff_result = runner.invoke(
        app,
        [
            "blueprint",
            "diff",
            "--old",
            "s1",
            "--new",
            "s2",
            "--vault-path",
            str(vault),
            "--output",
            str(blueprint_diff),
        ],
    )
    assert blueprint_diff_result.exit_code == 0
    assert blueprint_diff.exists()

