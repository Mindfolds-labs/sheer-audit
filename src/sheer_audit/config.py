from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import toml
from pathlib import Path

@dataclass(frozen=True)
class ProjectConfig:
    name: str = 'SheerAudit'
    root: str = '.'

@dataclass(frozen=True)
class ScanConfig:
    include_dirs: List[str]
    exclude_dirs: List[str]
    max_file_kb: int = 512
    include_tests: bool = True

@dataclass(frozen=True)
class AuditConfig:
    scope: List[str]
    exclude: List[str]

@dataclass(frozen=True)
class ParserConfig:
    mode: str = 'tolerant'
    python_version: str = '3.11'

@dataclass(frozen=True)
class TraceConfig:
    enabled: bool = True
    output_dir: str = 'artifacts/trace'
    max_depth: int = 200
    ignore_modules: List[str] = None

@dataclass(frozen=True)
class UMLConfig:
    engine: str = 'plantuml'
    output_dir: str = 'artifacts/uml'

@dataclass(frozen=True)
class SequenceConfig:
    max_depth: int = 60

@dataclass(frozen=True)
class ArchitectureConfig:
    layers: List[str] = None
    layer_paths: List[str] = None
    forbidden_imports: List[Dict[str, str]] = None

@dataclass(frozen=True)
class DocsConfig:
    adr_dir: str = 'docs/adr'
    blueprints_dir: str = 'docs/blueprints'
    atas_dir: str = 'docs/atas'

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

def load_config(path: str = 'sheer.toml') -> SheerConfig:
    '''Carrega configuração do arquivo TOML'''

    if not Path(path).exists():
        raise FileNotFoundError(f'Config file not found: {path}')

    raw = toml.load(path)

    project = ProjectConfig(**raw.get('project', {}))

    scan_raw = raw.get('scan', {})
    scan = ScanConfig(
        include_dirs=scan_raw.get('include_dirs', ['.']),
        exclude_dirs=scan_raw.get('exclude_dirs', []),
        max_file_kb=int(scan_raw.get('max_file_kb', 512)),
        include_tests=bool(scan_raw.get('include_tests', True)),
    )

    audit_raw = raw.get('audit', {})
    audit = AuditConfig(
        scope=audit_raw.get('scope', ['.']),
        exclude=audit_raw.get('exclude', []),
    )

    parser = ParserConfig(**raw.get('parser', {}))

    trace_raw = raw.get('trace', {})
    trace = TraceConfig(
        enabled=bool(trace_raw.get('enabled', True)),
        output_dir=str(trace_raw.get('output_dir', 'artifacts/trace')),
        max_depth=int(trace_raw.get('max_depth', 200)),
        ignore_modules=trace_raw.get('ignore_modules', ['typing', 'dataclasses']),
    )

    uml = UMLConfig(**raw.get('uml', {}))

    seq_raw = raw.get('uml', {}).get('sequence', {})
    sequence = SequenceConfig(max_depth=int(seq_raw.get('max_depth', 60)))

    arch_raw = raw.get('architecture', {})
    architecture = ArchitectureConfig(
        layers=arch_raw.get('layers'),
        layer_paths=arch_raw.get('layer_paths'),
        forbidden_imports=arch_raw.get('forbidden_imports'),
    )

    docs = DocsConfig(**raw.get('docs', {}))

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
