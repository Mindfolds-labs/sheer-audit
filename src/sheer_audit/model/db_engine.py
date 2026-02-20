from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


class SheerDBEngine:
    """Append-only store com assinatura HMAC para evidências de auditoria."""

    def __init__(self, vault_path: str = "docs/sheer_audit/vault/audit.sheerdb"):
        self.path = Path(vault_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.key = os.getenv("SHEER_DB_SECRET", "axis_folds_2026_secure").encode("utf-8")

    def _generate_hmac(self, payload: str) -> str:
        return hmac.new(self.key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def commit_record(self, table: str, data: Dict) -> None:
        entry = {
            "version": "2.0.3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "table": table,
            "payload": data,
        }
        raw_json = json.dumps(entry, ensure_ascii=False, sort_keys=True)
        signature = self._generate_hmac(raw_json)

        with self.path.open("ab") as f:
            f.write(f"{signature}|{raw_json}\n".encode("utf-8"))

    def _iter_valid_records(self) -> List[Dict]:
        valid_records: List[Dict] = []
        if not self.path.exists():
            return valid_records

        for line in self.path.read_bytes().splitlines():
            line_str = line.decode("utf-8", errors="ignore").strip()
            if not line_str or "|" not in line_str:
                continue
            sig, content = line_str.split("|", 1)
            if not hmac.compare_digest(sig, self._generate_hmac(content)):
                continue
            try:
                valid_records.append(json.loads(content))
            except json.JSONDecodeError:
                continue
        return valid_records

    def fetch_all(self, table: str) -> List[Dict]:
        return [entry.get("payload", {}) for entry in self._iter_valid_records() if entry.get("table") == table]

    def verify_integrity(self) -> Dict[str, int]:
        if not self.path.exists():
            return {"total": 0, "valid": 0, "invalid": 0}

        total = 0
        valid = 0
        for line in self.path.read_bytes().splitlines():
            line_str = line.decode("utf-8", errors="ignore").strip()
            if not line_str or "|" not in line_str:
                continue
            total += 1
            sig, content = line_str.split("|", 1)
            if hmac.compare_digest(sig, self._generate_hmac(content)):
                valid += 1
        return {"total": total, "valid": valid, "invalid": total - valid}

    def export_csv(self, output_path: str) -> Path:
        records = self._iter_valid_records()
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        lines = ["timestamp,table,payload_json"]
        for rec in records:
            payload = json.dumps(rec.get("payload", {}), ensure_ascii=False).replace('"', '""')
            lines.append(f'"{rec.get("timestamp", "")}","{rec.get("table", "")}","{payload}"')
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return out

    def purge(self) -> None:
        self.path.write_text("", encoding="utf-8")
