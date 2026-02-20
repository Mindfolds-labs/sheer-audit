from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from ..scan.advanced import SheerAdvancedEngine


def perform_semantic_scan(target_path: str, repo_path: str = ".") -> Dict[str, Any]:
    """Executa varredura semântica determinística no escopo indicado."""

    engine = SheerAdvancedEngine(repo_path=repo_path)
    structural_errors = [
        error
        for error in engine.detect_structural_errors()
        if error["file"].startswith(target_path.rstrip("/"))
    ]

    return {
        "target_path": target_path,
        "critical_errors": bool(structural_errors),
        "affected_files": sorted({error["file"] for error in structural_errors}),
        "error_details": structural_errors,
    }


def _deterministic_run_id(findings: Dict[str, Any], run_id: str | None = None) -> str:
    if run_id:
        return run_id

    raw = json.dumps(findings, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def generate_audit_artifacts(
    findings: Dict[str, Any],
    reports_path: str = "docs/sheeraudit/2.0.0/reports",
    run_id: str | None = None,
) -> Dict[str, str]:
    """Gera artefatos de Issue e ADR draft para o fluxo Forward-Fix."""

    report_dir = Path(reports_path)
    report_dir.mkdir(parents=True, exist_ok=True)

    audit_run_id = _deterministic_run_id(findings, run_id=run_id)
    issue_path = report_dir / f"ISSUE_AUDIT_{audit_run_id}.md"
    adr_path = report_dir / f"ADR_DRAFT_{audit_run_id}.md"

    issue_path.write_text(
        "\n".join(
            [
                "# 🔴 ISSUE: Falha de Integridade Detectada",
                "",
                f"**Run ID:** {audit_run_id}",
                f"**Escopo:** {findings['target_path']}",
                f"**Componentes Afetados:** {findings['affected_files']}",
                "",
                "## Detalhes da Falha",
                json.dumps(findings["error_details"], indent=2, ensure_ascii=False),
                "",
                "## Plano de Ação (Forward-Fix)",
                "1. Corrigir falha de integridade.",
                "2. Reexecutar snapshot com o mesmo escopo.",
                "3. Atualizar ADR para registrar decisão final.",
            ]
        ),
        encoding="utf-8",
    )

    adr_path.write_text(
        "\n".join(
            [
                "# ADR: Correção de Estabilidade de Versão",
                "",
                "Status: Proposto",
                f"Run ID: {audit_run_id}",
                "Contexto: Falha detectada pelo gatilho 2.0.0.",
                "Decisão: Aplicar Forward-Fix sem rollback.",
                "",
                "## Evidências",
                f"- Issue gerada: `{issue_path.name}`",
            ]
        ),
        encoding="utf-8",
    )

    return {"issue": str(issue_path), "adr": str(adr_path), "run_id": audit_run_id}


def run_forward_fix_audit(
    target_path: str = "docs/",
    reports_path: str = "docs/sheeraudit/2.0.0/reports",
    repo_path: str = ".",
    run_id: str | None = None,
) -> Dict[str, Any]:
    """Executa auditoria no modo de governança linear (Forward-Fix)."""

    findings = perform_semantic_scan(target_path=target_path, repo_path=repo_path)
    artifacts: Dict[str, str] = {}

    if findings["critical_errors"]:
        artifacts = generate_audit_artifacts(findings, reports_path=reports_path, run_id=run_id)

    return {
        "status": "failed" if findings["critical_errors"] else "clean",
        "findings": findings,
        "artifacts": artifacts,
    }
