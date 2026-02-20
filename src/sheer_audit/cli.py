from __future__ import annotations

import json
try:
    import tomllib
except ModuleNotFoundError:  # py<3.11
    import tomli as tomllib
from pathlib import Path

import typer
from rich.console import Console

from .governance.axisfolds import AxisFoldsLock
from .governance.planning import build_governance_bundle
from .model.db_engine import SheerDBEngine
from .model.schema import Finding, RepoInfo, RepoModel
from .scan.advanced import SheerAdvancedEngine

app = typer.Typer(help="Sheer Audit CLI")
console = Console()


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


@app.command("preflight")
def preflight_command(
    role: str = typer.Option("USER_IA_SERVICE", help="Perfil operacional corrente."),
    log_dir: str = typer.Option("docs/sheer_audit", help="Diretório monitorado para logs."),
    snapshot_id: str = typer.Option("", help="Snapshot esperado para rollback recente."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Checklist pré-execução para operações de IA com privilégio mínimo."""

    db = SheerDBEngine(vault_path=vault_path)
    checks = {
        "check_role": role == "USER_IA_SERVICE",
        "check_log_dir": Path(log_dir).exists(),
        "check_rollback_snapshot": bool(snapshot_id) and db.get_snapshot(snapshot_id) is not None,
    }

    report = {"checks": checks, "all_passed": all(checks.values())}
    console.print_json(json.dumps(report, ensure_ascii=False))
    if not report["all_passed"]:
        raise typer.Exit(code=1)


@app.command("db")
def db_command(
    verify: bool = typer.Option(False, "--verify", help="Verifica integridade das assinaturas HMAC."),
    export_csv: str = typer.Option("", "--export-csv", help="Exporta banco para CSV no caminho indicado."),
    list_snapshots: bool = typer.Option(False, "--list-snapshots", help="Lista snapshots persistidos."),
    purge: bool = typer.Option(False, "--purge", help="Remove arquivo de banco local."),
    vault_path: str = typer.Option("docs/sheer_audit/vault/audit.sheerdb", help="Arquivo SheerDB."),
) -> None:
    """Gerencia operações de manutenção do SheerDB."""

    db = SheerDBEngine(vault_path=vault_path)

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

    if not any([verify, export_csv, list_snapshots, purge]):
        console.print("Nenhuma operação escolhida. Use --help.")


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
