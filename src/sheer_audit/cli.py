from __future__ import annotations

import json
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
    full_scan: bool = typer.Option(True, help="Executa varredura estrutural completa."),
    uml: bool = typer.Option(False, help="Emite aviso para etapa UML."),
    ieee: bool = typer.Option(False, help="Exporta templates IEEE."),
    export: str = typer.Option("docs/sheer_audit/", help="Diretório de saída de artefatos."),
) -> None:
    """Executa o modo de engenharia avançada."""

    console.print("[bold blue]Iniciando Suite de Auditoria Avançada IEEE/ITIL...[/bold blue]")
    engine = SheerAdvancedEngine(".")
    db = SheerDBEngine()

    if full_scan:
        mapping = engine.generate_cartesian_map()
        errors = engine.detect_structural_errors()
        for error in errors:
            db.commit_record("system_errors", error)
        for component in mapping.get("components", []):
            db.commit_record("cartesian", component)

        manifest = {
            "audit_version": "2.0.3",
            "compliance": ["IEEE-1016", "IEEE-1028"],
            "metrics": {
                "total_components": len(mapping.get("components", [])),
                "total_relations": len(mapping.get("relations", [])),
                "structural_errors": len(errors),
            },
            "hotspots": engine.hotspots,
        }
        manifest_path = Path(export) / "ieee" / "IEEE_AUDIT_MANIFEST.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        console.print(
            f"Indexing completo: {manifest['metrics']['total_components']} componentes, "
            f"{manifest['metrics']['structural_errors']} erros estruturais."
        )

    if uml:
        console.print("Gerando Diagramas de Sequência e Classe... (roadmap Fase 5)")

    if ieee:
        engine.export_ieee_pack(export)
        console.print(f"Relatórios IEEE gerados em {export}")


@app.command("audit-secure")
def audit_secure() -> None:
    """Executa auditoria estrutural e persiste em SheerDB."""
    engine = SheerAdvancedEngine(".")
    db = SheerDBEngine()

    errors = engine.detect_structural_errors()
    for error in errors:
        db.commit_record("system_errors", error)

    console.print(f"✅ Auditoria concluída. {len(errors)} registos blindados no SheerDB.")


@app.command()
def db(
    verify: bool = typer.Option(False, "--verify", help="Verifica integridade de assinaturas."),
    export_csv: bool = typer.Option(False, "--export-csv", help="Exporta o banco para CSV."),
    purge: bool = typer.Option(False, "--purge", help="Remove todos os registros do banco."),
    output: str = typer.Option("docs/sheer_audit/vault/audit.csv", help="Saída para --export-csv."),
) -> None:
    """Comandos de manutenção do SheerDB."""

    db_engine = SheerDBEngine()

    if verify:
        stats = db_engine.verify_integrity()
        console.print(f"Registros: {stats['total']} | válidos: {stats['valid']} | inválidos: {stats['invalid']}")

    if export_csv:
        path = db_engine.export_csv(output)
        console.print(f"CSV exportado em {path}")

    if purge:
        db_engine.purge()
        console.print("Vault SheerDB limpo com sucesso.")

    if not any([verify, export_csv, purge]):
        console.print("Nenhuma operação selecionada. Use --verify, --export-csv ou --purge.")


@app.command("axisfolds-lock")
def axisfolds_lock(output: str = typer.Option("requirements_v2_0_3.folds")) -> None:
    """Gera lock de dependências e metadados de integridade."""

    lock = AxisFoldsLock()
    path = lock.write_folds_lock(output)
    console.print(f"Lock gerado em {path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
