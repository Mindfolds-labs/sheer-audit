import json
from pathlib import Path

from typer.testing import CliRunner

from sheer_audit.cli import app
from sheer_audit.db.triggers import generate_audit_artifacts, run_forward_fix_audit


def test_generate_audit_artifacts_is_deterministic(tmp_path: Path) -> None:
    findings = {
        "target_path": "docs/",
        "critical_errors": True,
        "affected_files": ["docs/bad.py"],
        "error_details": [{"file": "docs/bad.py", "line": 1, "type": "SyntaxError", "impact": "CRITICAL"}],
    }

    artifacts = generate_audit_artifacts(findings, reports_path=str(tmp_path), run_id="fixed-run")

    assert Path(artifacts["issue"]).exists()
    assert Path(artifacts["adr"]).exists()
    assert artifacts["run_id"] == "fixed-run"


def test_run_forward_fix_audit_clean_scope(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "ok.txt").write_text("conteudo\n", encoding="utf-8")

    result = run_forward_fix_audit(
        target_path="docs/",
        reports_path=str(tmp_path / "reports"),
        repo_path=str(tmp_path),
        run_id="run-clean",
    )

    assert result["status"] == "clean"
    assert result["artifacts"] == {}


def test_cli_scan_generates_snapshot_and_db_record(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "guide.md").write_text("# guia\n", encoding="utf-8")

    output_json = tmp_path / "docs" / "sheeraudit" / "2.0.0" / "repo_model.json"
    vault = tmp_path / "docs" / "sheeraudit" / "2.0.0" / "logs" / "audit.sheerdb"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "scan",
            str(docs_dir),
            "--output",
            str(output_json),
            "--db-user",
            "USER_IA_SERVICE",
            "--audit-version",
            "2.0.0",
            "--vault-path",
            str(vault),
        ],
    )

    assert result.exit_code == 0
    assert output_json.exists()
    assert vault.exists()

    snapshot = json.loads(output_json.read_text(encoding="utf-8"))
    assert snapshot["audit_version"] == "2.0.0"
    assert snapshot["db_user"] == "USER_IA_SERVICE"
