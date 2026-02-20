from pathlib import Path

from sheer_audit.model.db_engine import SheerDBEngine


def test_db_commit_fetch_verify_and_export(tmp_path: Path) -> None:
    db_path = tmp_path / "audit.sheerdb"
    db = SheerDBEngine(str(db_path))

    db.commit_record("errors", {"file": "a.py", "line": 1})
    db.commit_record("cartesian", {"x": "a.py", "y": 2})

    errors = db.fetch_all("errors")
    stats = db.verify_integrity()
    csv_path = db.export_csv(str(tmp_path / "audit.csv"))

    assert errors == [{"file": "a.py", "line": 1}]
    assert stats["invalid"] == 0
    assert csv_path.exists()


def test_db_purge(tmp_path: Path) -> None:
    db = SheerDBEngine(str(tmp_path / "audit.sheerdb"))
    db.commit_record("errors", {"code": "X"})
    db.purge()

    assert db.verify_integrity()["total"] == 0
