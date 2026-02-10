from __future__ import annotations
from pathlib import Path
import os
from typing import List
from ..config import ScanConfig

def collect_python_files(root: str, cfg: ScanConfig) -> List[str]:
    '''Coleta arquivos Python no repositório respeitando filtros'''

    rootp = Path(root).resolve()
    exclude = set(cfg.exclude_dirs or [])
    files: List[str] = []

    for dirpath, dirnames, filenames in os.walk(rootp):
        # Remove diretórios excluídos
        dirnames[:] = [d for d in dirnames if d not in exclude]

        for fn in filenames:
            if not fn.endswith('.py'):
                continue

            full = Path(dirpath) / fn
            rel = str(full.relative_to(rootp))

            # Filtro de testes
            if not cfg.include_tests:
                if 'test' in full.parts or fn.startswith('test_'):
                    continue

            # Filtro de tamanho
            size_kb = full.stat().st_size / 1024
            if size_kb > cfg.max_file_kb:
                continue

            files.append(rel)

    return sorted(set(files))
