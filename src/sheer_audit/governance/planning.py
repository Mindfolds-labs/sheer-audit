from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from typing import Dict, List, Mapping, Sequence

from ..model.schema import Finding, RepoModel, Severity

SEVERITY_WEIGHT: Mapping[Severity, int] = {
    "INFO": 1,
    "WARN": 3,
    "ERROR": 8,
    "CRITICAL": 13,
}


@dataclass(frozen=True)
class GovernanceIssue:
    """Issue derivada deterministicamente de findings com o mesmo código."""

    code: str
    priority_score: int
    max_severity: Severity
    evidence_count: int
    files: List[str]


@dataclass(frozen=True)
class GovernanceBundle:
    """Pacote completo de governança derivado do relatório."""

    report_fingerprint: str
    issues_markdown: str
    blueprint_markdown: str
    adr_markdown: str


_SEVERITY_RANK: Mapping[Severity, int] = {
    "INFO": 0,
    "WARN": 1,
    "ERROR": 2,
    "CRITICAL": 3,
}


def _normalize_findings(findings: Sequence[Finding]) -> List[Finding]:
    return sorted(
        findings,
        key=lambda f: (
            f.code,
            -_SEVERITY_RANK[f.severity],
            f.file,
            f.line if f.line is not None else -1,
            f.column if f.column is not None else -1,
            f.message,
        ),
    )


def build_governance_issues(findings: Sequence[Finding]) -> List[GovernanceIssue]:
    """Agrupa findings por código e calcula prioridade com função linear estável.

    Modelo:
    - score = soma dos pesos por severidade
    - pesos fixos em ``SEVERITY_WEIGHT``

    O modelo é monotônico em relação à severidade e cardinalidade de evidências,
    mantendo interpretação simples e auditável.
    """

    grouped: Dict[str, List[Finding]] = defaultdict(list)
    for finding in _normalize_findings(findings):
        grouped[finding.code].append(finding)

    issues: List[GovernanceIssue] = []
    for code, entries in grouped.items():
        max_severity = max(entries, key=lambda item: _SEVERITY_RANK[item.severity]).severity
        files = sorted({item.file for item in entries})
        priority_score = sum(SEVERITY_WEIGHT[item.severity] for item in entries)
        issues.append(
            GovernanceIssue(
                code=code,
                priority_score=priority_score,
                max_severity=max_severity,
                evidence_count=len(entries),
                files=files,
            )
        )

    return sorted(
        issues,
        key=lambda issue: (-issue.priority_score, -_SEVERITY_RANK[issue.max_severity], issue.code),
    )


def _fingerprint_report(report: RepoModel) -> str:
    """Fingerprint determinístico do conteúdo relevante do relatório."""

    normalized = {
        "schema_version": report.schema_version,
        "repo": report.repo.model_dump(mode="json"),
        "findings": [item.model_dump(mode="json") for item in _normalize_findings(report.findings)],
        "metrics": dict(sorted(report.metrics.items())),
    }
    payload = repr(normalized).encode("utf-8")
    return sha256(payload).hexdigest()


def _render_issues_markdown(issues: Sequence[GovernanceIssue], fingerprint: str) -> str:
    lines = [
        "# Governance Issues (derivado de relatório)",
        "",
        f"Fingerprint do relatório fonte: `{fingerprint}`",
        "",
        "## Backlog priorizado",
    ]

    if not issues:
        lines.extend(["", "Nenhum finding para converter em issue."])
        return "\n".join(lines)

    for index, issue in enumerate(issues, start=1):
        files = ", ".join(f"`{path}`" for path in issue.files)
        lines.extend(
            [
                "",
                f"### {index:02d}. {issue.code}",
                f"- Prioridade (score): **{issue.priority_score}**",
                f"- Severidade máxima: **{issue.max_severity}**",
                f"- Evidências: **{issue.evidence_count}**",
                f"- Arquivos afetados: {files}",
            ]
        )

    return "\n".join(lines)


def _render_blueprint_markdown(issues: Sequence[GovernanceIssue], fingerprint: str) -> str:
    top_codes = [issue.code for issue in issues[:3]]
    focus = ", ".join(top_codes) if top_codes else "sem pendências críticas"

    return "\n".join(
        [
            "# Blueprint — Governança orientada a evidências",
            "",
            "## Objetivo",
            "Transformar findings determinísticos em plano de evolução arquitetural rastreável.",
            "",
            "## Entradas",
            f"- Relatório Sheer fingerprint: `{fingerprint}`",
            "- Conjunto de findings agrupados por código",
            "",
            "## Estratégia",
            f"- Priorizar ações para: {focus}.",
            "- Converter cada agrupamento em issue com critério de aceite verificável.",
            "- Revisar impacto em contratos e ADR antes de mudança estrutural.",
            "",
            "## Saídas",
            "- Backlog de issues priorizadas",
            "- ADR de governança atualizado",
            "- Evidências para auditoria técnica",
        ]
    )


def _render_adr_markdown(issues: Sequence[GovernanceIssue], fingerprint: str) -> str:
    decision = (
        "Adotar pipeline determinístico que converte relatório em backlog de governança "
        "(issue + blueprint + ADR) sem intervenção não rastreável."
    )

    consequences = [
        "Priorização reproduzível com função linear de severidade.",
        "Rastreabilidade forte entre finding, issue e decisão arquitetural.",
        "Necessidade de manter taxonomia de severidade estável ao longo das versões.",
    ]

    if not issues:
        consequences.append("Sem findings, pipeline mantém apenas evidência de conformidade.")

    lines = [
        "# ADR — Governança derivada de relatórios Sheer",
        "",
        "## Status",
        "Proposto",
        "",
        "## Contexto",
        "Há necessidade de transformar resultados de auditoria em decisões de engenharia auditáveis.",
        f"Este ADR foi derivado do relatório fingerprint `{fingerprint}`.",
        "",
        "## Decisão",
        decision,
        "",
        "## Consequências",
    ]

    lines.extend(f"- {item}" for item in consequences)
    return "\n".join(lines)


def build_governance_bundle(report: RepoModel) -> GovernanceBundle:
    """Gera issue/blueprint/ADR a partir do modelo de relatório."""

    fingerprint = _fingerprint_report(report)
    issues = build_governance_issues(report.findings)

    return GovernanceBundle(
        report_fingerprint=fingerprint,
        issues_markdown=_render_issues_markdown(issues, fingerprint),
        blueprint_markdown=_render_blueprint_markdown(issues, fingerprint),
        adr_markdown=_render_adr_markdown(issues, fingerprint),
    )
