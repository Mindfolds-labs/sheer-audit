from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Dict


class AxisFoldsLock:
    """Snapshot de dependências Python com fingerprint de integridade."""

    def generate_folds_lock(self) -> Dict[str, object]:
        result = subprocess.run(["pip", "freeze"], capture_output=True, text=True, check=False)
        lines = sorted([line.strip() for line in result.stdout.splitlines() if "==" in line])

        components = {}
        for line in lines:
            name, version = line.split("==", 1)
            components[name] = version

        canonical = "\n".join(f"{name}=={components[name]}" for name in sorted(components))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return {
            "project": "SheerAudit",
            "version": "2.0.3",
            "components": components,
            "sha256": digest,
        }

    def write_folds_lock(self, output_path: str = "requirements_v2_0_3.folds") -> Path:
        data = self.generate_folds_lock()
        out = Path(output_path)

        lines = ["# ATOMIC LOCK - AXISFOLDS v2.0.3"]
        for name in sorted(data["components"]):
            lines.append(f"{name}=={data['components'][name]}")
        lines.append(f"# SHA256={data['sha256']}")

        out.write_text("\n".join(lines) + "\n", encoding="utf-8")

        meta = out.with_suffix(out.suffix + ".json")
        meta.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        return out
