from __future__ import annotations

import csv
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence


class SheerDBEngine:
    """Append-only store com assinatura HMAC para evidências de auditoria."""

    def __init__(self, vault_path: str = "docs/sheer_audit/vault/audit.sheerdb"):
        self.path = Path(vault_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.key = os.getenv("SHEER_DB_SECRET", "axis_folds_2026_secure").encode("utf-8")

    def _generate_hmac(self, payload: str) -> str:
        return hmac.new(self.key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def commit_record(self, table: str, data: Dict[str, object], timestamp: str = "static") -> None:
        """Salva registro assinado em formato SIGNATURE|JSON\\n."""

        entry = {"version": "2.1.0", "timestamp": timestamp, "table": table, "payload": data}
        raw_json = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        signature = self._generate_hmac(raw_json)

        with self.path.open("ab") as handle:
            handle.write(f"{signature}|{raw_json}\n".encode("utf-8"))

    def _iter_verified_entries(self) -> Sequence[Dict[str, object]]:
        rows: List[Dict[str, object]] = []
        if not self.path.exists():
            return rows

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

                rows.append(json.loads(content))

        return rows

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
        for entry in self._iter_verified_entries():
            if entry.get("table") == table:
                valid_records.append(entry.get("payload", {}))
        return valid_records

    def record_snapshot(self, snapshot: Dict[str, object], timestamp: str = "static") -> None:
        """Registra um snapshot versionado com metadados de evolução."""

        self.commit_record("snapshots", snapshot, timestamp=timestamp)

    def list_snapshots(self) -> List[Dict[str, object]]:
        snapshots = self.fetch_all("snapshots")
        return sorted(
            snapshots,
            key=lambda item: (
                str(item.get("timestamp", "")),
                str(item.get("snapshot_id", "")),
            ),
        )

    def get_snapshot(self, snapshot_id: str) -> Dict[str, object] | None:
        for item in self.list_snapshots():
            if item.get("snapshot_id") == snapshot_id:
                return item
        return None

    @staticmethod
    def _component_index(snapshot: Dict[str, object]) -> Dict[str, str]:
        index: Dict[str, str] = {}
        for component in snapshot.get("components", []):
            component_id = str(component.get("id", ""))
            digest = str(component.get("hash", ""))
            if component_id:
                index[component_id] = digest
        return index

    @staticmethod
    def _finding_keys(snapshot: Dict[str, object]) -> set[str]:
        keys: set[str] = set()
        for finding in snapshot.get("findings", []):
            keys.add(
                "|".join(
                    [
                        str(finding.get("code", "")),
                        str(finding.get("severity", "")),
                        str(finding.get("file", "")),
                        str(finding.get("line", "")),
                        str(finding.get("message", "")),
                    ]
                )
            )
        return keys

    @staticmethod
    def _stability_level(regressions: int, total_findings: int) -> str:
        if regressions > 0:
            return "INSTAVEL"
        if total_findings == 0:
            return "ESTAVEL"
        return "EM_EVOLUCAO"

    def diff_snapshots(self, old_id: str, new_id: str) -> Dict[str, object]:
        old_snapshot = self.get_snapshot(old_id)
        new_snapshot = self.get_snapshot(new_id)
        if old_snapshot is None or new_snapshot is None:
            raise ValueError("snapshot não encontrado")

        old_components = self._component_index(old_snapshot)
        new_components = self._component_index(new_snapshot)

        old_keys = set(old_components)
        new_keys = set(new_components)
        added_components = sorted(new_keys - old_keys)
        removed_components = sorted(old_keys - new_keys)
        changed_components = sorted(
            item for item in (old_keys & new_keys) if old_components[item] != new_components[item]
        )

        old_findings = self._finding_keys(old_snapshot)
        new_findings = self._finding_keys(new_snapshot)
        new_findings_count = len(new_findings - old_findings)
        resolved_findings_count = len(old_findings - new_findings)
        persistent_findings_count = len(old_findings & new_findings)

        stability = self._stability_level(
            regressions=new_findings_count,
            total_findings=int(new_snapshot.get("metrics", {}).get("findings_total", len(new_findings))),
        )

        return {
            "old_snapshot_id": old_id,
            "new_snapshot_id": new_id,
            "components": {
                "added": added_components,
                "removed": removed_components,
                "changed": changed_components,
            },
            "findings": {
                "new": new_findings_count,
                "resolved": resolved_findings_count,
                "persistent": persistent_findings_count,
            },
            "classification": {
                "stability": stability,
                "regressions": new_findings_count,
            },
        }

    def export_evolution_markdown(self, old_id: str, new_id: str, output_path: str) -> Dict[str, object]:
        diff = self.diff_snapshots(old_id, new_id)

        lines = [
            f"# Relatório de Evolução `{old_id}` → `{new_id}`",
            "",
            "## Classificação",
            f"- Estabilidade: **{diff['classification']['stability']}**",
            f"- Regressões detectadas: **{diff['classification']['regressions']}**",
            "",
            "## Componentes",
            f"- Adicionados: **{len(diff['components']['added'])}**",
            f"- Removidos: **{len(diff['components']['removed'])}**",
            f"- Alterados: **{len(diff['components']['changed'])}**",
            "",
            "## Findings",
            f"- Novos: **{diff['findings']['new']}**",
            f"- Resolvidos: **{diff['findings']['resolved']}**",
            f"- Persistentes: **{diff['findings']['persistent']}**",
        ]

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(lines), encoding="utf-8")
        return diff

    def export_csv(self, output_path: str) -> int:
        rows: List[Dict[str, object]] = list(self._iter_verified_entries())

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
