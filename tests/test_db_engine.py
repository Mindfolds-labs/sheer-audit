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


def test_db_purge(tmp_path: Path) -> None:
    db_file = tmp_path / "audit.sheerdb"
    db = SheerDBEngine(vault_path=str(db_file))
    db.commit_record("errors", {"x": 1})
    db.purge()
    assert not db_file.exists()
