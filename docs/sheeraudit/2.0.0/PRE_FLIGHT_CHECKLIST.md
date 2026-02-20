# Pre-flight 2.0.0 (Auditoria `docs/`)

## 1) Identidade e credenciais

- [ ] Operar com credencial `USER_IA_SERVICE`.
- [ ] Permissões: leitura de código + escrita em `docs/sheeraudit/2.0.0/`.

## 2) Artefatos e diretórios

- [ ] `docs/sheeraudit/2.0.0/logs/` existe.
- [ ] `docs/sheeraudit/2.0.0/reports/` existe.
- [ ] `src/sheer_audit/db/triggers.py` disponível para modo Forward-Fix.

## 3) Execução de auditoria

```bash
python -m sheer_audit.cli scan docs/ \
  --output docs/sheeraudit/2.0.0/repo_model.json \
  --mode stability-check \
  --db-user USER_IA_SERVICE \
  --audit-version 2.0.0
```

## 4) Critério de saída

- [ ] Se houver falhas críticas: gerar `ISSUE_AUDIT_*.md` e `ADR_DRAFT_*.md`.
- [ ] Se limpo: manter snapshot `repo_model.json` para publicação.
