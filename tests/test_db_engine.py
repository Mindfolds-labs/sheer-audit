from pathlib import Path

from sheer_audit.model.db_engine import SheerDBEngine


def test_db_engine_commit_fetch_verify_and_export(tmp_path: Path) -> None:
    db_file = tmp_path / "audit.sheerdb"
    csv_file = tmp_path / "audit.csv"

    db = SheerDBEngine(vault_path=str(db_file))
    db.commit_record("errors", {"file": "a.py", "line": 10})

    stats = db.verify_integrity()
    assert stats == {"total": 1, "valid": 1, "invalid": 0}

    rows = db.fetch_all("errors")
    assert rows == [{"file": "a.py", "line": 10}]

    count = db.export_csv(str(csv_file))
    assert count == 1
    assert csv_file.exists()


def test_snapshot_diff_and_evolution_report(tmp_path: Path) -> None:
    db_file = tmp_path / "audit.sheerdb"
    report_file = tmp_path / "evolution.md"

    db = SheerDBEngine(vault_path=str(db_file))
    db.record_snapshot(
        {
            "snapshot_id": "s1",
            "components": [{"id": "a.py:alpha", "hash": "h1"}],
            "findings": [{"code": "SyntaxError", "severity": "CRITICAL", "file": "a.py", "line": 1, "message": "x"}],
            "metrics": {"findings_total": 1},
        }
    )
    db.record_snapshot(
        {
            "snapshot_id": "s2",
            "components": [
                {"id": "a.py:alpha", "hash": "h1b"},
                {"id": "b.py:beta", "hash": "h2"},
            ],
            "findings": [],
            "metrics": {"findings_total": 0},
        }
    )

    diff = db.diff_snapshots("s1", "s2")
    assert diff["components"]["added"] == ["b.py:beta"]
    assert diff["components"]["changed"] == ["a.py:alpha"]
    assert diff["findings"]["resolved"] == 1
    assert diff["classification"]["stability"] == "ESTAVEL"

    persisted = db.list_snapshots()
    assert [item["snapshot_id"] for item in persisted] == ["s1", "s2"]

    generated = db.export_evolution_markdown("s1", "s2", str(report_file))
    assert generated["old_snapshot_id"] == "s1"
    assert report_file.exists()


def test_db_purge(tmp_path: Path) -> None:
    db_file = tmp_path / "audit.sheerdb"
    db = SheerDBEngine(vault_path=str(db_file))
    db.commit_record("errors", {"x": 1})
    db.purge()
    assert not db_file.exists()
