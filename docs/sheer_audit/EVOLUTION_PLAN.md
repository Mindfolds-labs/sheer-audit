# Plano de Evolução Determinística — Sheer Audit

## Objetivo
Implementar monitoramento de múltiplas versões do repositório com comparação de snapshots, classificação de estabilidade e geração automática de artefatos de governança.

## Escopo entregue
1. Persistência append-only de snapshots no SheerDB com assinatura HMAC.
2. Comparação determinística entre snapshots (componentes/findings).
3. Classificação de estabilidade (`ESTAVEL`, `EM_EVOLUCAO`, `INSTAVEL`).
4. Geração de relatório de evolução + issue/ADR/blueprint derivados.
5. Checklist pré-execução para operação de IA com privilégio mínimo.

## Fluxo operacional
1. `sheer snapshot --id <id>` grava componentes, findings, dependências e árvore de execução.
2. `sheer evolution --old <id1> --new <id2>` gera diff + artefatos de governança.
3. `sheer preflight` valida role, diretório de logs e snapshot de rollback.
4. `sheer db --verify` verifica integridade do vault.

## Checklist de gabinete (pré-execução)
- [ ] Credencial operacional definida como `USER_IA_SERVICE`.
- [ ] Vault íntegro (`sheer db --verify` sem inválidos).
- [ ] Snapshot de rollback disponível no banco.
- [ ] Diretório de logs monitorado e existente.
- [ ] Saídas de issue/ADR com destino em `docs/issues` e `docs/architecture/adr`.

## Observações de segurança
- SheerDB mantém trilha append-only com HMAC por registro.
- O core analítico permanece estático/determinístico (sem execução do código auditado).
- Artefatos de governança são derivados por função determinística a partir dos findings.
