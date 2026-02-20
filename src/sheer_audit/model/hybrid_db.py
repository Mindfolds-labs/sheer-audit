from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Dict, List


class HybridAuditDB:
    """Persistência híbrida: SQL (linhagem) + blob semântico em arquivo JSON."""

    def __init__(
        self,
        sql_path: str = "docs/sheer_audit/vault/lineage.db",
        blob_root: str = "docs/sheer_audit/2.0.0/data",
    ) -> None:
        self.sql_path = Path(sql_path)
        self.blob_root = Path(blob_root)

    def init(self) -> None:
        self.sql_path.parent.mkdir(parents=True, exist_ok=True)
        self.blob_root.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.sql_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_lineage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component_name TEXT NOT NULL,
                    version_tag TEXT NOT NULL,
                    nosql_blob_path TEXT NOT NULL,
                    complexity_index REAL NOT NULL,
                    integrity_hash TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def persist_component_audit(self, component_data: Dict[str, object], version_tag: str) -> Dict[str, object]:
        self.init()
        component_name = str(component_data.get("component", "unknown"))
        full_ast = component_data.get("ast", {})
        complexity_index = float(len(component_data.get("components", [])))

        digest = hashlib.sha256(
            json.dumps(full_ast, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()

        blob_path = self.blob_root / f"{component_name.replace('/', '_').replace(':', '_')}.json"
        blob_path.write_text(
            json.dumps(
                {
                    "component": component_name,
                    "version_tag": version_tag,
                    "ast": full_ast,
                    "execution": component_data.get("execution", {}),
                },
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            ),
            encoding="utf-8",
        )

        with sqlite3.connect(self.sql_path) as conn:
            conn.execute(
                """
                INSERT INTO audit_lineage (
                    component_name,
                    version_tag,
                    nosql_blob_path,
                    complexity_index,
                    integrity_hash,
                    status
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    component_name,
                    version_tag,
                    blob_path.as_posix(),
                    complexity_index,
                    digest,
                    "STABLE" if component_data.get("found") else "FAIL",
                ),
            )
            conn.commit()

        return {
            "component_name": component_name,
            "version_tag": version_tag,
            "nosql_blob_path": blob_path.as_posix(),
            "complexity_index": complexity_index,
            "integrity_hash": digest,
        }

    def list_lineage(self) -> List[Dict[str, object]]:
        self.init()
        with sqlite3.connect(self.sql_path) as conn:
            rows = conn.execute(
                """
                SELECT component_name, version_tag, nosql_blob_path,
                       complexity_index, integrity_hash, status
                FROM audit_lineage
                ORDER BY component_name, version_tag
                """
            ).fetchall()

        return [
            {
                "component_name": row[0],
                "version_tag": row[1],
                "nosql_blob_path": row[2],
                "complexity_index": row[3],
                "integrity_hash": row[4],
                "status": row[5],
            }
            for row in rows
        ]
