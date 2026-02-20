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
```
