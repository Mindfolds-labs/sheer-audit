from pathlib import Path

from typer.testing import CliRunner

from sheer_audit.cli import app


runner = CliRunner()


def test_snapshot_evolution_and_preflight_commands(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text(
        "[project]\nname = 'demo'\ndependencies = ['typer==0.16.0']\n", encoding="utf-8"
    )

    vault = tmp_path / "audit.sheerdb"
    blobs = tmp_path / "blobs"
    blobs.mkdir()
    issue = tmp_path / "issues.md"
    adr = tmp_path / "adr.md"
    blueprint = tmp_path / "blueprint.md"
    evolution = tmp_path / "evolution.md"

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

    (repo / "a.py").write_text("def alpha():\n    return 2\n\ndef beta():\n    return alpha()\n", encoding="utf-8")

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

    result_evolution = runner.invoke(
        app,
        [
            "evolution",
            "diff",
            "--old",
            "s1",
            "--new",
            "s2",
            "--markdown-out",
            str(evolution),
            "--issue-out",
            str(issue),
            "--adr-out",
            str(adr),
            "--blueprint-out",
            str(blueprint),
            "--vault-path",
            str(vault),
        ],
    )
    assert result_evolution.exit_code == 0
    assert evolution.exists()
    assert issue.exists()
    assert adr.exists()
    assert blueprint.exists()

    result_preflight_ok = runner.invoke(
        app,
        [
            "preflight",
            "--role",
            "USER_IA_SERVICE",
            "--log-dir",
            str(tmp_path),
            "--snapshot-id",
            "s2",
            "--vault-path",
            str(vault),
            "--blob-dir",
            str(blobs),
        ],
    )
    assert result_preflight_ok.exit_code == 0

    result_preflight_fail = runner.invoke(
        app,
        [
            "preflight",
            "--role",
            "USER_DBA",
            "--log-dir",
            str(tmp_path),
            "--snapshot-id",
            "s2",
            "--vault-path",
            str(vault),
            "--blob-dir",
            str(blobs),
        ],
    )
    assert result_preflight_fail.exit_code == 1


def test_new_granular_commands_and_hybrid_persistence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "mod.py").write_text("def neuron():\n    return 42\n", encoding="utf-8")

    vault = tmp_path / "audit.sheerdb"
    lineage_sql = tmp_path / "lineage.db"
    blob_root = tmp_path / "data"

    init_db = runner.invoke(app, ["db", "--init", "--vault-path", str(vault)])
    assert init_db.exit_code == 0
    assert vault.exists()

    analyze_component = runner.invoke(
        app,
        [
            "analyze",
            "component",
            "mod.py:neuron",
            "--repo-path",
            str(repo),
            "--sql-path",
            str(lineage_sql),
            "--blob-root",
            str(blob_root),
            "--version-tag",
            "2.0.0",
        ],
    )
    assert analyze_component.exit_code == 0
    assert lineage_sql.exists()
    assert any(blob_root.glob("*.json"))

    blueprint_generate = runner.invoke(
        app,
        [
            "blueprint",
            "generate",
            "--repo-path",
            str(repo),
            "--output",
            str(tmp_path / "blueprint.md"),
        ],
    )
    assert blueprint_generate.exit_code == 0

    for snapshot_id in ["s1", "s2"]:
        result = runner.invoke(
            app,
            ["snapshot", "--id", snapshot_id, "--repo-path", str(repo), "--vault-path", str(vault)],
        )
        assert result.exit_code == 0

    blueprint_diff = runner.invoke(
        app,
        ["blueprint", "diff", "s1", "s2", "--vault-path", str(vault), "--output", str(tmp_path / "b.diff")],
    )
    assert blueprint_diff.exit_code == 0

    evolution_graph = runner.invoke(
        app,
        ["evolution", "graph", "--vault-path", str(vault), "--output", str(tmp_path / "graph.md")],
    )
    assert evolution_graph.exit_code == 0

    evolution_health = runner.invoke(app, ["evolution", "health", "--vault-path", str(vault)])
    assert evolution_health.exit_code == 0
