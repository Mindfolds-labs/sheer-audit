from __future__ import annotations

import json
try:
    import tomllib
except ModuleNotFoundError:  # py<3.11
    import tomli as tomllib
from pathlib import Path

import typer
from rich.console import Console

from .db.triggers import run_forward_fix_audit
from .governance.axisfolds import AxisFoldsLock
from .governance.planning import build_governance_bundle
from .model.db_engine import SheerDBEngine
from .model.hybrid_db import HybridAuditDB
from .model.schema import Finding, RepoInfo, RepoModel
from .scan.advanced import SheerAdvancedEngine

app = typer.Typer(help="Sheer Audit CLI")
analyze_app = typer.Typer(help="Análise granular de componentes")
blueprint_app = typer.Typer(help="Blueprinting arquitetural")
evolution_app = typer.Typer(help="Comandos de evolução")
console = Console()

app.add_typer(analyze_app, name="analyze")
app.add_typer(blueprint_app, name="blueprint")
app.add_typer(evolution_app, name="evolution")


@app.command()
def advanced(
    full_scan: bool = typer.Option(True, help="Executa mapeamento cartesiano e detecção estrutural."),
    uml: bool = typer.Option(False, help="Exibe etapa de UML (placeholder determinístico)."),
    ieee: bool = typer.Option(False, help="Gera pacote IEEE 1016/1028."),
    export: str = typer.Option("docs/sheer_audit", help="Diretório de exportação de artefatos."),
) -> None:
    """Executa o modo de engenharia avançada IEEE/ITIL."""

    console.print("[bold blue]Iniciando Suite de Auditoria Avançada IEEE/ITIL...[/bold blue]")
    engine = SheerAdvancedEngine(".")

    if full_scan:
        cartesian = engine.generate_cartesian_map()
        errors = engine.detect_structural_errors()
        console.print(
            f"Indexing concluído: {len(cartesian['coordinates'])} componentes, "
            f"{len(errors)} erros estruturais."
        )

    if uml:
        console.print("Gerando Diagramas de Sequência e Classe... (roadmap)")

    if ieee:
        manifest = engine.export_ieee_pack(export)
        console.print(f"Relatórios IEEE gerados em {export} com {manifest['metrics']}.")


@app.command()
def scan(
    target_path: str = typer.Argument("docs/", help="Escopo alvo da varredura."),
    output: str = typer.Option("docs/sheeraudit/2.0.0/repo_model.json", help="Arquivo JSON de saída."),
    mode: str = typer.Option("stability-check", help="Modo de execução da auditoria."),
    db_user: str = typer.Option("USER_IA_SERVICE", "--db-user", help="Identidade de serviço para trilha."),
    audit_version: str = typer.Option("2.0.0", help="Versão da linha de auditoria."),
    vault_path: str = typer.Option("docs/sheeraudit/2.0.0/logs/audit.sheerdb", help="Vault append-only."),
) -> None:
    """Executa scan com gatilho Forward-Fix e consolida evidências."""

    result = run_forward_fix_audit(
        target_path=target_path,
        reports_path=f"docs/sheeraudit/{audit_version}/reports",
        repo_path=".",
        run_id=f"{audit_version}-{mode}",
    )

    payload = {
        "audit_version": audit_version,
        "mode": mode,
        "db_user": db_user,
        "target_path": target_path,
        "status": result["status"],
        "findings": result["findings"],
        "artifacts": result["artifacts"],
    }

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    db = SheerDBEngine(vault_path=vault_path)
    db.commit_record(
        "forward_fix_runs",
        {
            "audit_version": audit_version,
            "mode": mode,
            "db_user": db_user,
            "target_path": target_path,
            "status": result["status"],
            "run_id": result["artifacts"].get("run_id", f"{audit_version}-{mode}"),
        },
        timestamp=f"audit-{audit_version}",
    )

    if result["status"] == "failed":
        console.print("❌ Falhas encontradas. Issues/ADRs de correção foram geradas.")
    else:
        console.print("✅ Auditoria limpa. Snapshot pronto para publicação.")
    console.print(f"Snapshot salvo em {output_path}")


@app.command()
def audit_secure(
    repo_path: str = typer.Option(".", help="Raiz do repositório para análise."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Executa auditoria profunda e salva resultados no SheerDB."""

    engine = SheerAdvancedEngine(repo_path)
    db = SheerDBEngine(vault_path=vault_path)

    errors = engine.detect_structural_errors()
    for error in errors:
        db.commit_record("system_errors", error)

    console.print(f"✅ Auditoria concluída. {len(errors)} registos blindados no SheerDB.")


def _extract_dependencies(repo_path: Path) -> list[dict[str, str]]:
    pyproject_path = repo_path / "pyproject.toml"
    if not pyproject_path.exists():
        return []

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    dependencies = data.get("project", {}).get("dependencies", [])
    parsed: list[dict[str, str]] = []
    for dep in dependencies:
        if "==" in dep:
            name, version = dep.split("==", 1)
        else:
            name, version = dep, "unspecified"
        parsed.append({"name": name.strip(), "version": version.strip(), "ecosystem": "pip"})
    return sorted(parsed, key=lambda item: item["name"])


@app.command("snapshot")
def snapshot_command(
    snapshot_id: str = typer.Option(..., "--id", help="Identificador estável da fotografia."),
    repo_path: str = typer.Option(".", help="Raiz do repositório analisado."),
    ref: str = typer.Option("working-tree", help="Commit/tag/branch da fotografia."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
    timestamp: str = typer.Option("static", help="Timestamp lógico determinístico."),
) -> None:
    """Cria snapshot com componentes, findings, dependências e mapa de execução."""

    repo = Path(repo_path)
    engine = SheerAdvancedEngine(str(repo))
    db = SheerDBEngine(vault_path=vault_path)

    findings = engine.detect_structural_errors()
    components = engine.build_component_inventory()
    execution_tree = engine.build_execution_tree()
    dependencies = _extract_dependencies(repo)

    payload: dict[str, object] = {
        "snapshot_id": snapshot_id,
        "repo": repo.resolve().as_posix(),
        "ref": ref,
        "components": components,
        "findings": findings,
        "dependencies": dependencies,
        "execution_tree": execution_tree,
        "metrics": {
            "components_total": len(components),
            "findings_total": len(findings),
            "dependencies_total": len(dependencies),
        },
    }

    db.record_snapshot(payload, timestamp=timestamp)
    console.print(
        f"📸 Snapshot `{snapshot_id}` salvo com {len(components)} componentes e {len(findings)} findings."
    )


@app.command("analyze")
def analyze_command(
    component: list[str] = typer.Option([], "--component", help="Filtro de componente(s) por substring."),
    repo_path: str = typer.Option(".", help="Raiz do repositório analisado."),
    output: str = typer.Option("docs/sheeraudit/2.0.0/component_analysis.json", help="Saída JSON."),
) -> None:
    """Executa análise granular por componente (um ou vários)."""

    engine = SheerAdvancedEngine(repo_path)
    components = engine.build_component_inventory()
    findings = engine.detect_structural_errors()

    if component:
        filters = [token.lower() for token in component]
        components = [
            item for item in components if any(token in str(item["id"]).lower() for token in filters)
        ]
        findings = [
            item
            for item in findings
            if any(token in str(item["file"]).lower() for token in filters)
        ]

    payload = {
        "repo_path": str(Path(repo_path).resolve()),
        "filters": component,
        "components_total": len(components),
        "findings_total": len(findings),
        "components": components,
        "findings": findings,
    }

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"🔎 Análise de componentes exportada para {target}")


@blueprint_app.command("generate")
def blueprint_generate_command(
    snapshot_id: str = typer.Option("", help="Snapshot opcional para gerar blueprint persistido."),
    repo_path: str = typer.Option(".", help="Raiz do repositório analisado (fallback)."),
    output: str = typer.Option("docs/BLUEPRINT.md", help="Arquivo markdown de saída."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Gera blueprint arquitetural atual."""

    components: list[dict[str, object]]
    findings: list[dict[str, object]]
    source = "workspace"

    if snapshot_id:
        db = SheerDBEngine(vault_path=vault_path)
        snapshot = db.get_snapshot(snapshot_id)
        if snapshot is None:
            raise typer.BadParameter("Snapshot não encontrado para gerar blueprint.")
        components = list(snapshot.get("components", []))
        findings = list(snapshot.get("findings", []))
        source = f"snapshot:{snapshot_id}"
    else:
        engine = SheerAdvancedEngine(repo_path)
        components = engine.build_component_inventory()
        findings = engine.detect_structural_errors()

    by_kind: dict[str, int] = {}
    for component in components:
        kind = str(component.get("kind", "Unknown"))
        by_kind[kind] = by_kind.get(kind, 0) + 1

    lines = [
        "# Blueprint de Arquitetura",
        "",
        f"- Fonte: `{source}`",
        f"- Componentes: **{len(components)}**",
        f"- Findings: **{len(findings)}**",
        "",
        "## Distribuição por tipo",
    ]
    lines.extend([f"- {kind}: **{count}**" for kind, count in sorted(by_kind.items())])

    if components:
        lines.extend(["", "## Componentes amostrados"])
        for item in sorted(components, key=lambda row: str(row.get("id", "")))[:20]:
            lines.append(f"- `{item.get('id', '<unknown>')}` ({item.get('kind', 'Unknown')})")

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"🧭 Blueprint gerado em {target}")


@blueprint_app.command("diff")
def blueprint_diff_command(
    old_snapshot: str = typer.Option(..., "--old", help="Snapshot base."),
    new_snapshot: str = typer.Option(..., "--new", help="Snapshot alvo."),
    output: str = typer.Option("docs/sheeraudit/2.0.0/reports/BLUEPRINT_DIFF.md", help="Arquivo markdown."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Gera diff arquitetural entre snapshots."""

    db = SheerDBEngine(vault_path=vault_path)
    diff = db.diff_snapshots(old_snapshot, new_snapshot)
    lines = [
        f"# Blueprint Diff `{old_snapshot}` → `{new_snapshot}`",
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

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"🧩 Blueprint diff salvo em {target}")


@app.command("evolution")
def evolution_command(
    old_snapshot: str = typer.Option(..., "--old", help="Snapshot base para comparação."),
    new_snapshot: str = typer.Option(..., "--new", help="Snapshot alvo para comparação."),
    markdown_out: str = typer.Option("docs/sheer_audit/RELATORIO_EVOLUCAO.md", help="Relatório de evolução."),
    issue_out: str = typer.Option("docs/issues/0004-evolution-generated.md", help="Issue derivada."),
    adr_out: str = typer.Option("docs/architecture/adr/ADR-0020-evolution-governance.md", help="ADR derivado."),
    blueprint_out: str = typer.Option("docs/BLUEPRINT.md", help="Blueprint derivado do diff."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Compara snapshots e gera relatório + artefatos de governança (issue/ADR/blueprint)."""

    db = SheerDBEngine(vault_path=vault_path)
    diff = db.export_evolution_markdown(old_snapshot, new_snapshot, markdown_out)

    new_data = db.get_snapshot(new_snapshot)
    if new_data is None:
        raise typer.BadParameter("Snapshot alvo não encontrado para gerar governança.")

    report = RepoModel(
        repo=RepoInfo(root=str(new_data.get("repo", ".")), name=Path(str(new_data.get("repo", "."))).name),
        findings=[
            Finding(
                code=str(item.get("type", "UNKNOWN")),
                severity="CRITICAL" if item.get("impact") == "CRITICAL" else "ERROR",
                file=str(item.get("file", "<unknown>")),
                line=int(item.get("line", 1)),
                message=str(item.get("fix", "sem correção")),
            )
            for item in new_data.get("findings", [])
        ],
        metrics={
            "diff_added_components": len(diff["components"]["added"]),
            "diff_changed_components": len(diff["components"]["changed"]),
            "diff_new_findings": int(diff["findings"]["new"]),
        },
    )

    bundle = build_governance_bundle(report)

    issue_path = Path(issue_out)
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    issue_path.write_text(bundle.issues_markdown, encoding="utf-8")

    adr_path = Path(adr_out)
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    adr_path.write_text(bundle.adr_markdown, encoding="utf-8")

    blueprint_path = Path(blueprint_out)
    blueprint_path.parent.mkdir(parents=True, exist_ok=True)
    blueprint_path.write_text(bundle.blueprint_markdown, encoding="utf-8")

    console.print(
        "📈 Evolução gerada com sucesso: "
        f"relatório={markdown_out}, issue={issue_out}, adr={adr_out}, blueprint={blueprint_out}."
    )


@evolution_app.command("graph")
def evolution_graph_command(
    output: str = typer.Option("docs/sheer_audit/EVOLUTION_GRAPH.md", help="Saída markdown do grafo temporal."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Gera linha do tempo de snapshots [falha -> versão -> correção]."""

    db = SheerDBEngine(vault_path=vault_path)
    snapshots = db.list_snapshots()

    lines = ["# Evolution Graph", "", "| Snapshot | Findings | Componentes | Estado |", "|---|---:|---:|---|"]
    for snapshot in snapshots:
        findings_total = int(snapshot.get("metrics", {}).get("findings_total", 0))
        components_total = int(snapshot.get("metrics", {}).get("components_total", 0))
        status = "FIXED" if findings_total == 0 else "FAIL"
        lines.append(
            f"| {snapshot.get('snapshot_id', 'unknown')} | {findings_total} | {components_total} | {status} |"
        )

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"📈 Evolution graph gerado em {target.as_posix()}.")


@evolution_app.command("health")
def evolution_health_command(
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Classifica componentes em maduros vs zonas de risco (alto churn)."""

    db = SheerDBEngine(vault_path=vault_path)
    snapshots = db.list_snapshots()
    component_changes: dict[str, int] = {}
    for index in range(1, len(snapshots)):
        old_id = str(snapshots[index - 1].get("snapshot_id", ""))
        new_id = str(snapshots[index].get("snapshot_id", ""))
        diff = db.diff_snapshots(old_id, new_id)
        for changed in diff["components"]["changed"]:
            component_changes[changed] = component_changes.get(changed, 0) + 1

    mature = sorted([name for name, churn in component_changes.items() if churn <= 1])
    risk = sorted([name for name, churn in component_changes.items() if churn > 1])
    console.print_json(json.dumps({"mature": mature, "risk_zones": risk}, ensure_ascii=False))


@app.command("preflight")
def preflight_command(
    role: str = typer.Option("USER_IA_SERVICE", help="Perfil operacional corrente."),
    log_dir: str = typer.Option("docs/sheer_audit", help="Diretório monitorado para logs."),
    snapshot_id: str = typer.Option("", help="Snapshot esperado para rollback recente."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
    blob_dir: str = typer.Option("docs/sheer_audit/2.0.0/data", help="Diretório NoSQL de blobs semânticos."),
) -> None:
    """Checklist pré-execução para operações de IA com privilégio mínimo."""

    db = SheerDBEngine(vault_path=vault_path)
    checks = {
        "check_role": role == "USER_IA_SERVICE",
        "check_log_dir": Path(log_dir).exists(),
        "check_db_initialized": Path(vault_path).exists(),
        "check_blob_path_writable": Path(blob_dir).exists() and Path(blob_dir).is_dir(),
        "check_rollback_snapshot": bool(snapshot_id) and db.get_snapshot(snapshot_id) is not None,
    }

    report = {"checks": checks, "all_passed": all(checks.values())}
    console.print_json(json.dumps(report, ensure_ascii=False))
    if not report["all_passed"]:
        raise typer.Exit(code=1)


@app.command("db")
def db_command(
    init: bool = typer.Option(False, "--init", help="Inicializa o SheerDB local."),
    verify: bool = typer.Option(False, "--verify", help="Verifica integridade das assinaturas HMAC."),
    export_csv: str = typer.Option("", "--export-csv", help="Exporta banco para CSV no caminho indicado."),
    list_snapshots: bool = typer.Option(False, "--list-snapshots", help="Lista snapshots persistidos."),
    purge: bool = typer.Option(False, "--purge", help="Remove arquivo de banco local."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Gerencia operações de manutenção do SheerDB."""

    db = SheerDBEngine(vault_path=vault_path)

    if init:
        path = db.init_storage()
        console.print(f"SheerDB inicializado em {path}.")

    if verify:
        stats = db.verify_integrity()
        console.print(f"Integridade: total={stats['total']} valid={stats['valid']} invalid={stats['invalid']}")

    if export_csv:
        count = db.export_csv(export_csv)
        console.print(f"CSV exportado em {export_csv} com {count} entradas válidas.")

    if list_snapshots:
        snapshots = db.list_snapshots()
        console.print_json(json.dumps(snapshots, ensure_ascii=False, indent=2))

    if purge:
        db.purge()
        console.print("Vault removido com sucesso.")

    if not any([init, verify, export_csv, list_snapshots, purge]):
        console.print("Nenhuma operação escolhida. Use --help.")


@analyze_app.command("component")
def analyze_component_command(
    name: str = typer.Argument(..., help="Identificador do componente (arquivo.py:símbolo ou módulo)."),
    repo_path: str = typer.Option(".", help="Raiz do repositório."),
    sql_path: str = typer.Option("docs/sheer_audit/vault/lineage.db", help="Banco SQL de linhagem."),
    blob_root: str = typer.Option("docs/sheer_audit/2.0.0/data", help="Diretório NoSQL de blobs."),
    version_tag: str = typer.Option("2.0.0", help="Versão de referência para o registro."),
) -> None:
    """Analisa um único componente e persiste AST em camada híbrida."""

    engine = SheerAdvancedEngine(repo_path)
    hybrid = HybridAuditDB(sql_path=sql_path, blob_root=blob_root)
    component_data = engine.analyze_component(name)
    record = hybrid.persist_component_audit(component_data=component_data, version_tag=version_tag)
    console.print_json(json.dumps(record, ensure_ascii=False))


@blueprint_app.command("generate")
def blueprint_generate_command(
    repo_path: str = typer.Option(".", help="Raiz do repositório."),
    output: str = typer.Option("docs/BLUEPRINT.md", help="Saída do blueprint markdown."),
) -> None:
    """Gera blueprint textual do estado atual."""

    engine = SheerAdvancedEngine(repo_path)
    components = engine.build_component_inventory()
    execution_tree = engine.build_execution_tree()

    lines = ["# Blueprint Atual", "", f"- Componentes: **{len(components)}**", "", "## Execução"]
    for module_name, symbols in execution_tree.items():
        lines.append(f"- `{module_name}`: {', '.join(symbols)}")

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"🧭 Blueprint gerado em {target.as_posix()}.")


@blueprint_app.command("diff")
def blueprint_diff_command(
    v1: str = typer.Argument(..., help="Snapshot base."),
    v2: str = typer.Argument(..., help="Snapshot alvo."),
    output: str = typer.Option("docs/sheer_audit/BLUEPRINT_DIFF.md", help="Saída do diff."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Mostra alterações arquiteturais entre dois snapshots."""

    db = SheerDBEngine(vault_path=vault_path)
    diff = db.diff_snapshots(v1, v2)
    lines = [
        f"# Blueprint Diff `{v1}` -> `{v2}`",
        "",
        "## Componentes",
        f"- Adicionados: {', '.join(diff['components']['added']) or 'nenhum'}",
        f"- Removidos: {', '.join(diff['components']['removed']) or 'nenhum'}",
        f"- Alterados: {', '.join(diff['components']['changed']) or 'nenhum'}",
    ]

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"🧩 Blueprint diff gerado em {target.as_posix()}.")


@app.command()
def axisfolds(
    output: str = typer.Option("requirements_v2_0_3.folds", help="Arquivo de lock de dependências."),
    pyproject: str = typer.Option("pyproject.toml", help="Fonte de dependências."),
) -> None:
    """Gera arquivo de lock AxisFolds a partir do pyproject."""

    lock = AxisFoldsLock()
    path = lock.write_folds_file(output_path=output, pyproject_path=pyproject)
    console.print(f"🔒 AxisFolds lock gerado em {path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
