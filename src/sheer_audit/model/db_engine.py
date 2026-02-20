from __future__ import annotations

import csv
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Dict, List


class SheerDBEngine:
    """SGBD append-only com HMAC para integridade de registros de auditoria."""

    def __init__(self, vault_path: str = "docs/sheer_audit/vault/audit.sheerdb"):
        self.path = Path(vault_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.key = os.getenv("SHEER_DB_SECRET", "axis_folds_2026_secure").encode("utf-8")

    def _generate_hmac(self, payload: str) -> str:
        return hmac.new(self.key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def commit_record(self, table: str, data: Dict[str, object], timestamp: str = "static") -> None:
        """Salva registro assinado em formato SIGNATURE|JSON\\n."""

        entry = {"version": "2.0.3", "timestamp": timestamp, "table": table, "payload": data}
        raw_json = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        signature = self._generate_hmac(raw_json)

        with self.path.open("ab") as handle:
            handle.write(f"{signature}|{raw_json}\n".encode("utf-8"))

    def verify_integrity(self) -> Dict[str, int]:
        total = 0
        valid = 0
        invalid = 0

        if not self.path.exists():
            return {"total": 0, "valid": 0, "invalid": 0}

        with self.path.open("rb") as handle:
            for line in handle:
                row = line.decode("utf-8", errors="replace").strip()
                if not row:
                    continue
                total += 1
                try:
                    sig, content = row.split("|", 1)
                except ValueError:
                    invalid += 1
                    continue

                if hmac.compare_digest(sig, self._generate_hmac(content)):
                    valid += 1
                else:
                    invalid += 1

        return {"total": total, "valid": valid, "invalid": invalid}

    def fetch_all(self, table: str) -> List[Dict[str, object]]:
        valid_records: List[Dict[str, object]] = []
        if not self.path.exists():
            return valid_records

        with self.path.open("rb") as handle:
            for line in handle:
                row = line.decode("utf-8", errors="replace").strip()
                if not row:
                    continue
                try:
                    sig, content = row.split("|", 1)
                except ValueError:
                    continue

                if not hmac.compare_digest(sig, self._generate_hmac(content)):
                    continue

                obj = json.loads(content)
                if obj.get("table") == table:
                    valid_records.append(obj.get("payload", {}))

        return valid_records

    def export_csv(self, output_path: str) -> int:
        rows: List[Dict[str, object]] = []
        if self.path.exists():
            with self.path.open("rb") as handle:
                for line in handle:
                    row = line.decode("utf-8", errors="replace").strip()
                    if not row:
                        continue
                    try:
                        sig, content = row.split("|", 1)
                    except ValueError:
                        continue
                    if not hmac.compare_digest(sig, self._generate_hmac(content)):
                        continue
                    entry = json.loads(content)
                    rows.append(entry)

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["version", "timestamp", "table", "payload"])
            for item in rows:
                writer.writerow(
                    [
                        item.get("version", ""),
                        item.get("timestamp", ""),
                        item.get("table", ""),
                        json.dumps(item.get("payload", {}), ensure_ascii=False, sort_keys=True),
                    ]
                )

        return len(rows)

    def purge(self) -> None:
        if self.path.exists():
            self.path.unlink()
