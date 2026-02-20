# SheerAudit 2.0.0 — Linha de Auditoria

Este diretório consolida a execução da fase **Forward-Fix** para auditorias na pasta `docs/`.

## Estrutura

- `logs/`: trilhas de execução e snapshots auxiliares.
- `reports/`: issues e rascunhos de ADR gerados automaticamente.

## Comando recomendado

```bash
python -m sheer_audit.cli scan docs/ \
  --output docs/sheeraudit/2.0.0/repo_model.json \
  --mode stability-check \
  --db-user USER_IA_SERVICE \
  --audit-version 2.0.0

# análise granular por componente
python -m sheer_audit.cli analyze \
  --repo-path . \
  --component src/sheer_audit/cli.py \
  --component src/sheer_audit/model/db_engine.py \
  --output docs/sheeraudit/2.0.0/reports/component_analysis.json

# snapshots + evolução (gráfico e saúde)
python -m sheer_audit.cli snapshot --id s1 --repo-path . --vault-path docs/sheeraudit/2.0.0/logs/audit.sheerdb
python -m sheer_audit.cli snapshot --id s2 --repo-path . --vault-path docs/sheeraudit/2.0.0/logs/audit.sheerdb
python -m sheer_audit.cli evolution-graph --vault-path docs/sheeraudit/2.0.0/logs/audit.sheerdb
python -m sheer_audit.cli evolution-health --vault-path docs/sheeraudit/2.0.0/logs/audit.sheerdb

# blueprint arquitetural
python -m sheer_audit.cli blueprint generate --snapshot-id s2 --vault-path docs/sheeraudit/2.0.0/logs/audit.sheerdb
python -m sheer_audit.cli blueprint diff --old s1 --new s2 --vault-path docs/sheeraudit/2.0.0/logs/audit.sheerdb
```
