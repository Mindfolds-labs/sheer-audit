from sheer_audit.governance.axisfolds import AxisFoldsLock


class _Completed:
    def __init__(self, stdout: str):
        self.stdout = stdout


def test_axisfolds_generate_lock(monkeypatch) -> None:
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: _Completed("b==2\na==1\n"),
    )

    lock = AxisFoldsLock().generate_folds_lock()

    assert lock["components"] == {"a": "1", "b": "2"}
    assert len(lock["sha256"]) == 64
