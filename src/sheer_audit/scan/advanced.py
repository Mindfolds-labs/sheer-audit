from __future__ import annotations

import ast
import json
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set

from ..config import ScanConfig
from .repo import collect_python_files


@dataclass(frozen=True)
class StructuralError:
    file: str
    line: int
    error_type: str
    impact: str
    fix: str


class SheerAdvancedEngine:
    """Motor determinístico para engenharia avançada de auditoria estática."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.hotspots: List[Dict[str, str]] = []

    def _iter_python_files(self) -> Iterable[Path]:
        cfg = ScanConfig(include_dirs=["."], exclude_dirs=[".git", ".venv", "venv"], include_tests=True)
        for rel in collect_python_files(str(self.repo_path), cfg):
            yield self.repo_path / rel

    def generate_cartesian_map(self) -> Dict[str, object]:
        """Mapeia componentes X (arquivo:símbolo) e Y (profundidade de chamada lexical)."""

        coordinates: List[Dict[str, object]] = []
        max_depth = 0

        for file_path in self._iter_python_files():
            relative = file_path.relative_to(self.repo_path).as_posix()
            source = file_path.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(source, filename=relative)
            except SyntaxError:
                continue

            stack: List[ast.AST] = []

            def walk(node: ast.AST) -> None:
                nonlocal max_depth
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    depth = len(stack)
                    max_depth = max(max_depth, depth)
                    name = getattr(node, "name", "<anonymous>")
                    coordinates.append({"x": f"{relative}:{name}", "y": depth, "kind": type(node).__name__})
                    stack.append(node)
                    for child in ast.iter_child_nodes(node):
                        walk(child)
                    stack.pop()
                    return

                for child in ast.iter_child_nodes(node):
                    walk(child)

            walk(tree)

        return {
            "model": "R subset CxFxE",
            "equation": "F(x,y)=sum_i d(Module_x)/d(Stage_y)",
            "coordinates": sorted(coordinates, key=lambda item: (item["x"], item["y"])),
            "max_depth": max_depth,
        }

    def _collect_import_graph(self) -> Dict[str, Set[str]]:
        graph: Dict[str, Set[str]] = {}
        repo_modules: Set[str] = set()

        for file_path in self._iter_python_files():
            rel = file_path.relative_to(self.repo_path)
            module_name = ".".join(rel.with_suffix("").parts)
            repo_modules.add(module_name)

        for file_path in self._iter_python_files():
            rel = file_path.relative_to(self.repo_path)
            module_name = ".".join(rel.with_suffix("").parts)
            imports: Set[str] = set()
            source = file_path.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(source, filename=rel.as_posix())
            except SyntaxError:
                graph[module_name] = imports
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)

            graph[module_name] = {imp for imp in imports if imp in repo_modules}

        return graph

    def detect_structural_errors(self) -> List[Dict[str, object]]:
        """Detecta erros estruturais determinísticos (syntax + dependência circular)."""

        errors: List[StructuralError] = []

        for file_path in self._iter_python_files():
            rel = file_path.relative_to(self.repo_path).as_posix()
            source = file_path.read_text(encoding="utf-8", errors="replace")
            try:
                ast.parse(source, filename=rel)
            except SyntaxError as exc:
                errors.append(
                    StructuralError(
                        file=rel,
                        line=exc.lineno or 1,
                        error_type="SyntaxError",
                        impact="CRITICAL",
                        fix="Corrigir sintaxe para restaurar parse estático.",
                    )
                )

        graph = self._collect_import_graph()

        def find_cycles() -> Set[str]:
            cycles: Set[str] = set()
            visiting: Set[str] = set()
            visited: Set[str] = set()

            def dfs(node: str, ancestry: List[str]) -> None:
                if node in visiting:
                    start = ancestry.index(node)
                    for item in ancestry[start:]:
                        cycles.add(item)
                    return
                if node in visited:
                    return

                visiting.add(node)
                ancestry.append(node)
                for nxt in sorted(graph.get(node, set())):
                    dfs(nxt, ancestry)
                ancestry.pop()
                visiting.remove(node)
                visited.add(node)

            for item in sorted(graph):
                dfs(item, [])

            return cycles

        for module in sorted(find_cycles()):
            errors.append(
                StructuralError(
                    file=f"{module.replace('.', '/')}.py",
                    line=1,
                    error_type="CircularDependency",
                    impact="HIGH",
                    fix="Quebrar ciclo com inversão de dependência ou extração de interface.",
                )
            )

        return [
            {
                "file": e.file,
                "line": e.line,
                "type": e.error_type,
                "impact": e.impact,
                "fix": e.fix,
            }
            for e in sorted(errors, key=lambda item: (item.file, item.line, item.error_type))
        ]



    def build_component_inventory(self) -> List[Dict[str, object]]:
        """Inventário determinístico de componentes com hash por arquivo/símbolo."""

        inventory: List[Dict[str, object]] = []
        cartesian = self.generate_cartesian_map()
        for item in cartesian["coordinates"]:
            component_id = str(item["x"])
            digest = hashlib.sha256(component_id.encode("utf-8")).hexdigest()
            inventory.append(
                {
                    "id": component_id,
                    "kind": item["kind"],
                    "depth": int(item["y"]),
                    "hash": digest,
                }
            )

        return sorted(inventory, key=lambda value: value["id"])

    def build_execution_tree(self) -> Dict[str, List[str]]:
        """Mapa de execução lexical (arquivo -> símbolos)."""

        tree: Dict[str, List[str]] = {}
        for component in self.build_component_inventory():
            file_part, symbol = str(component["id"]).split(":", 1)
            tree.setdefault(file_part, []).append(symbol)

        for key in sorted(tree):
            tree[key] = sorted(tree[key])

        return {key: tree[key] for key in sorted(tree)}

    def analyze_component(self, component_name: str) -> Dict[str, object]:
        """Analisa componente único por id `arquivo.py:simbolo` ou por nome de módulo."""

        inventory = self.build_component_inventory()
        execution_tree = self.build_execution_tree()

        matched = [item for item in inventory if component_name in str(item["id"]) or component_name == str(item["id"]).split(":", 1)[0]]
        if not matched:
            return {
                "component": component_name,
                "found": False,
                "components": [],
                "execution": [],
            }

        files = sorted({str(item["id"]).split(":", 1)[0] for item in matched})
        execution: Dict[str, List[str]] = {item: execution_tree.get(item, []) for item in files}
        ast_blobs: Dict[str, Dict[str, object]] = {}
        for file_path in files:
            absolute = self.repo_path / file_path
            source = absolute.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=file_path)
            ast_blobs[file_path] = ast.dump(tree, annotate_fields=True, include_attributes=False)

        return {
            "component": component_name,
            "found": True,
            "components": sorted(matched, key=lambda item: str(item["id"])),
            "execution": execution,
            "ast": ast_blobs,
        }

    def export_ieee_pack(self, output_dir: str) -> Dict[str, object]:
        """Gera pacote IEEE (docs + manifest JSON) com métricas determinísticas."""

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        ieee_dir = out / "ieee"
        ieee_dir.mkdir(parents=True, exist_ok=True)

        cartesian = self.generate_cartesian_map()
        errors = self.detect_structural_errors()

        architecture_md = out / "IEEE_1016_Architecture.md"
        testplan_md = out / "IEEE_1028_AuditPlan.md"
        manifest_json = ieee_dir / "IEEE_AUDIT_MANIFEST.json"

        architecture_md.write_text(
            "\n".join(
                [
                    "# IEEE 1016 Architecture Report",
                    "",
                    f"Repository: `{self.repo_path.name}`",
                    f"Components mapped: **{len(cartesian['coordinates'])}**",
                    f"Max lexical depth: **{cartesian['max_depth']}**",
                ]
            ),
            encoding="utf-8",
        )

        testplan_md.write_text(
            "\n".join(
                [
                    "# IEEE 1028 Audit Plan",
                    "",
                    "## Findings",
                    f"- Structural errors found: **{len(errors)}**",
                    "- Method: deterministic static analysis",
                ]
            ),
            encoding="utf-8",
        )

        manifest = {
            "audit_version": "2.0.3",
            "compliance": ["IEEE-1016", "IEEE-1028"],
            "metrics": {
                "components_mapped": len(cartesian["coordinates"]),
                "circular_dependencies": sum(1 for e in errors if e["type"] == "CircularDependency"),
                "syntax_errors": sum(1 for e in errors if e["type"] == "SyntaxError"),
            },
            "hotspots": self.hotspots,
        }
        manifest_json.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        return manifest
