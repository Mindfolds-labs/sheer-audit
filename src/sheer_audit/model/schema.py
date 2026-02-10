from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, List

SymbolKind = Literal['module', 'class', 'function', 'method']
EdgeType = Literal['IMPORT', 'CONTAINS', 'INHERITS', 'CALLS', 'TRACE_CALL', 'LAYER_VIOLATION']
Severity = Literal['INFO', 'WARN', 'ERROR', 'CRITICAL']

class RepoInfo(BaseModel):
    root: str
    name: Optional[str] = None
    commit: Optional[str] = None

class Symbol(BaseModel):
    id: str
    kind: SymbolKind
    name: str
    qname: str
    file: str
    line: int
    doc: Optional[str] = None
    params: List[str] = Field(default_factory=list)
    returns: Optional[str] = None
    bases: List[str] = Field(default_factory=list)
    decorators: List[str] = Field(default_factory=list)

class Edge(BaseModel):
    type: EdgeType
    src: str
    dst: str
    meta: Dict[str, str] = Field(default_factory=dict)

class Finding(BaseModel):
    code: str
    severity: Severity
    file: str
    line: Optional[int] = None
    column: Optional[int] = None
    message: str
    hint: Optional[str] = None
    excerpt: Optional[Dict[str, any]] = None

class RepoModel(BaseModel):
    schema_version: str = '2.0'
    repo: RepoInfo
    symbols: List[Symbol] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    metrics: Dict[str, int] = Field(default_factory=dict)
