from __future__ import annotations

import os
from pathlib import Path
from typing import List

from ..config import ScanConfig


def _is_test_path(relative_path: Path) -> bool:
    """Return True when path clearly belongs to test code.

    A regra usa apenas o caminho relativo (determinístico) e evita heurísticas
    amplas demais que poderiam excluir arquivos válidos por acidente.
    """

    test_dirs = {"test", "tests"}
    for part in relative_path.parts[:-1]:
        if part.lower() in test_dirs:
            return True

    return relative_path.name.startswith("test_") or relative_path.name.endswith("_test.py")


def collect_python_files(root: str, cfg: ScanConfig) -> List[str]:
    """Coleta arquivos Python no repositório respeitando filtros.

    Invariantes:
    - determinístico (ordenação final + caminhos relativos canônicos)
    - read-only (somente metadata via stat)
    - respeita include_dirs/exclude_dirs da configuração
    """

    rootp = Path(root).resolve()
    exclude = {d.lower() for d in (cfg.exclude_dirs or [])}
    include_dirs = cfg.include_dirs or ["."]

    files: List[str] = []

    for include_dir in include_dirs:
        base_dir = (rootp / include_dir).resolve()
        if not base_dir.exists() or not base_dir.is_dir():
            continue

        if rootp not in {base_dir, *base_dir.parents}:
            # Segurança: ignora include_dir fora do root para manter escopo de varredura.
            continue

        rel_base = base_dir.relative_to(rootp) if base_dir != rootp else Path(".")
        if rel_base != Path(".") and any(part.lower() in exclude for part in rel_base.parts):
            continue

        for dirpath, dirnames, filenames in os.walk(base_dir):
            dirnames[:] = [d for d in dirnames if d.lower() not in exclude]

            for fn in filenames:
                if not fn.endswith(".py"):
                    continue

                full = Path(dirpath) / fn
                rel_path = full.relative_to(rootp)

                if not cfg.include_tests and _is_test_path(rel_path):
                    continue

                size_kb = full.stat().st_size / 1024
                if size_kb > cfg.max_file_kb:
                    continue

                files.append(rel_path.as_posix())

    return sorted(set(files))
