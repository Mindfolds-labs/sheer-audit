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
        ],
    )
    assert result_preflight_fail.exit_code == 1
