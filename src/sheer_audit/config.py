from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml


@dataclass(frozen=True)
class ProjectConfig:
    name: str = "SheerAudit"
    root: str = "."


@dataclass(frozen=True)
class ScanConfig:
    include_dirs: List[str] = field(default_factory=lambda: ["."])
    exclude_dirs: List[str] = field(default_factory=list)
    max_file_kb: int = 512
    include_tests: bool = True


@dataclass(frozen=True)
class AuditConfig:
    scope: List[str] = field(default_factory=lambda: ["."])
    exclude: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ParserConfig:
    mode: str = "tolerant"
    python_version: str = "3.11"


@dataclass(frozen=True)
class TraceConfig:
    enabled: bool = True
    output_dir: str = "artifacts/trace"
    max_depth: int = 200
    ignore_modules: List[str] = field(default_factory=lambda: ["typing", "dataclasses"])


@dataclass(frozen=True)
class UMLConfig:
    engine: str = "plantuml"
    output_dir: str = "artifacts/uml"


@dataclass(frozen=True)
class SequenceConfig:
    max_depth: int = 60


@dataclass(frozen=True)
class ArchitectureConfig:
    layers: List[str] = field(default_factory=list)
    layer_paths: List[str] = field(default_factory=list)
    forbidden_imports: List[Dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class DocsConfig:
    adr_dir: str = "docs/adr"
    blueprints_dir: str = "docs/blueprints"
    atas_dir: str = "docs/atas"


@dataclass(frozen=True)
class SheerConfig:
    project: ProjectConfig
    scan: ScanConfig
    audit: AuditConfig
    parser: ParserConfig
    trace: TraceConfig
    uml: UMLConfig
    sequence: SequenceConfig
    architecture: ArchitectureConfig
    docs: DocsConfig


def _as_int(data: Dict[str, Any], key: str, default: int) -> int:
    return int(data.get(key, default))


def load_config(path: str = "sheer.toml") -> SheerConfig:
    """Carrega configuração do arquivo TOML de forma determinística."""

    if not Path(path).exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    raw = toml.load(path)

    project = ProjectConfig(**raw.get("project", {}))

    scan_raw = raw.get("scan", {})
    scan = ScanConfig(
        include_dirs=list(scan_raw.get("include_dirs", ["."])),
        exclude_dirs=list(scan_raw.get("exclude_dirs", [])),
        max_file_kb=_as_int(scan_raw, "max_file_kb", 512),
        include_tests=bool(scan_raw.get("include_tests", True)),
    )

    audit_raw = raw.get("audit", {})
    audit = AuditConfig(
        scope=list(audit_raw.get("scope", ["."])),
        exclude=list(audit_raw.get("exclude", [])),
    )

    parser = ParserConfig(**raw.get("parser", {}))

    trace_raw = raw.get("trace", {})
    trace = TraceConfig(
        enabled=bool(trace_raw.get("enabled", True)),
        output_dir=str(trace_raw.get("output_dir", "artifacts/trace")),
        max_depth=_as_int(trace_raw, "max_depth", 200),
        ignore_modules=list(trace_raw.get("ignore_modules", ["typing", "dataclasses"])),
    )

    uml_raw = dict(raw.get("uml", {}))
    seq_from_uml = uml_raw.pop("sequence", {})
    uml = UMLConfig(**uml_raw)

    # Compatibilidade: aceita [uml.sequence] (preferido) e [sequence] (legado).
    seq_raw = seq_from_uml or raw.get("sequence", {})
    sequence = SequenceConfig(max_depth=_as_int(seq_raw, "max_depth", 60))

    arch_raw = raw.get("architecture", {})
    architecture = ArchitectureConfig(
        layers=list(arch_raw.get("layers", [])),
        layer_paths=list(arch_raw.get("layer_paths", [])),
        forbidden_imports=list(arch_raw.get("forbidden_imports", [])),
    )

    docs = DocsConfig(**raw.get("docs", {}))

    return SheerConfig(
        project=project,
        scan=scan,
        audit=audit,
        parser=parser,
        trace=trace,
        uml=uml,
        sequence=sequence,
        architecture=architecture,
        docs=docs,
    )
