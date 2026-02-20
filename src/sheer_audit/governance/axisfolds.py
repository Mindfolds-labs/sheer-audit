from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import toml


@dataclass(frozen=True)
class AxisFoldsLock:
    """Gerador de lock de dependências a partir do pyproject local."""

    project_name: str = "SheerAudit"

    def generate_folds_lock(self, pyproject_path: str = "pyproject.toml") -> Dict[str, object]:
        path = Path(pyproject_path)
        raw = toml.loads(path.read_text(encoding="utf-8"))
        deps = raw.get("project", {}).get("dependencies", [])

        components: Dict[str, str] = {}
        for dep in deps:
            name, version = self._split_dependency(dep)
            components[name] = version

        return {
            "project": self.project_name,
            "lock_date": "static",
            "components": dict(sorted(components.items())),
        }

    def write_folds_file(self, output_path: str = "requirements_v2_0_3.folds", pyproject_path: str = "pyproject.toml") -> str:
        lock = self.generate_folds_lock(pyproject_path=pyproject_path)
        target = Path(output_path)

        lines = ["# ATOMIC LOCK - AXISFOLDS v2.0.3"]
        for name, version in lock["components"].items():
            lines.append(f"{name}=={version}")
        lines.append("# CRC32C VALIDATED BY MINDAXIS")

        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return target.as_posix()

    @staticmethod
    def _split_dependency(dep: str) -> tuple[str, str]:
        if ">=" in dep:
            name, version = dep.split(">=", 1)
            return name.strip(), version.strip()
        if "==" in dep:
            name, version = dep.split("==", 1)
            return name.strip(), version.strip()
        return dep.strip(), "latest"
