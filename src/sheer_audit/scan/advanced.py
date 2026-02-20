from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, List, Set, Tuple


class SheerAdvancedEngine:
    """Motor de engenharia avançada para análise estrutural determinística."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self._calls: DefaultDict[str, Set[str]] = defaultdict(set)
        self.hotspots: List[Dict[str, object]] = []

    def _python_files(self) -> List[Path]:
        files = [p for p in self.repo_path.rglob("*.py") if p.is_file()]
        return sorted(files, key=lambda item: item.as_posix())

    def _relative(self, path: Path) -> str:
        return path.relative_to(self.repo_path).as_posix()

    def _scan_file(self, path: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
        cartesian: List[Dict[str, object]] = []
        errors: List[Dict[str, object]] = []

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (UnicodeDecodeError, SyntaxError) as exc:
            errors.append(
                {
                    "file": self._relative(path),
                    "line": getattr(exc, "lineno", None),
                    "type": "SyntaxError",
                    "impact": "CRITICAL",
                    "correction": "Corrigir sintaxe para permitir análise estática completa.",
                }
            )
            return cartesian, errors

        class_depth = 0
        func_depth = 0

        class Visitor(ast.NodeVisitor):
            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                nonlocal class_depth
                class_depth += 1
                cartesian.append(
                    {
                        "component": self_name,
                        "file": rel,
                        "kind": "class",
                        "name": node.name,
                        "x": rel,
                        "y": class_depth,
                        "line": node.lineno,
                    }
                )
                self.generic_visit(node)
                class_depth -= 1

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                nonlocal func_depth
                func_depth += 1
                fqname = f"{rel}:{node.name}"
                cartesian.append(
                    {
                        "component": fqname,
                        "file": rel,
                        "kind": "function",
                        "name": node.name,
                        "x": rel,
                        "y": func_depth,
                        "line": node.lineno,
                    }
                )

                call_names = {
                    n.func.id
                    for n in ast.walk(node)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                }
                self_calls = {
                    n.func.attr
                    for n in ast.walk(node)
                    if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == "self"
                }
                for call in sorted(call_names | self_calls):
                    self_graph[fqname].add(call)

                complexity = 1 + sum(
                    1
                    for n in ast.walk(node)
                    if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp, ast.With, ast.Match))
                )
                if complexity >= 10:
                    hotspots.append(
                        {
                            "component": fqname,
                            "risk": "high",
                            "reason": "high_cyclomatic_complexity",
                            "value": complexity,
                        }
                    )

                if isinstance(node.body[-1], ast.Pass):
                    errors.append(
                        {
                            "file": rel,
                            "line": node.body[-1].lineno,
                            "type": "DeadBranch",
                            "impact": "WARN",
                            "correction": f"Revisar função '{node.name}' com bloco pass terminal.",
                        }
                    )

                self.generic_visit(node)
                func_depth -= 1

        rel = self._relative(path)
        self_name = rel
        self_graph = self._calls
        hotspots = self.hotspots

        Visitor().visit(tree)
        return cartesian, errors

    def generate_cartesian_map(self) -> Dict[str, object]:
        mapping: Dict[str, object] = {"components": [], "relations": []}

        for file_path in self._python_files():
            components, _ = self._scan_file(file_path)
            mapping["components"].extend(components)

        relations = []
        for src, dst_set in sorted(self._calls.items()):
            for dst in sorted(dst_set):
                relations.append({"src": src, "dst": dst, "type": "CALL"})
        mapping["relations"] = relations

        return mapping

    def detect_structural_errors(self) -> List[Dict[str, object]]:
        errors: List[Dict[str, object]] = []
        self.hotspots = []
        self._calls.clear()

        for file_path in self._python_files():
            _, local_errors = self._scan_file(file_path)
            errors.extend(local_errors)

        # Detecta ciclos simples em chamadas internas com DFS determinístico
        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            stack.add(node)
            for nxt in sorted(self._calls.get(node, set())):
                target = nxt if ":" in nxt else None
                if target is None:
                    continue
                if target not in visited:
                    dfs(target)
                elif target in stack:
                    errors.append(
                        {
                            "file": node.split(":", 1)[0],
                            "line": None,
                            "type": "CircularDependency",
                            "impact": "ERROR",
                            "correction": f"Remover ciclo entre {node} e {target}.",
                        }
                    )
            stack.remove(node)

        for node in sorted(self._calls.keys()):
            if node not in visited:
                dfs(node)

        return sorted(errors, key=lambda item: (str(item.get("file")), item.get("line") or -1, str(item.get("type"))))

    def export_ieee_pack(self, output_dir: str) -> None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        files = {
            "IEEE_1016_Architecture.md": "# IEEE 1016 Architecture Report\n\nRelatório gerado automaticamente pelo Sheer Advanced Engine.\n",
            "IEEE_1028_Audit.md": "# IEEE 1028 Audit Report\n\nChecklist de auditoria derivado de evidências estáticas.\n",
            "IEEE_829_TestPlan.md": "# IEEE 829 Test Plan\n\nPlano de testes sugerido para rastreabilidade de findings.\n",
        }

        for name, content in files.items():
            (out / name).write_text(content, encoding="utf-8")
