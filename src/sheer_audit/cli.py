from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .governance.axisfolds import AxisFoldsLock
from .model.db_engine import SheerDBEngine
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


@app.command("db")
def db_command(
    verify: bool = typer.Option(False, "--verify", help="Verifica integridade das assinaturas HMAC."),
    export_csv: str = typer.Option("", "--export-csv", help="Exporta banco para CSV no caminho indicado."),
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

    if purge:
        db.purge()
        console.print("Vault removido com sucesso.")

    if not any([verify, export_csv, purge]):
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
