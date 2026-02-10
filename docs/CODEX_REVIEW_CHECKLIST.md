# CODEX_REVIEW_CHECKLIST — Aprovação de mudanças

## Arquitetura e governança
- [ ] Mudança respeita core vs stages
- [ ] Não introduziu I/O no core
- [ ] Determinismo preservado
- [ ] ADR/docs atualizados quando necessário

## Qualidade
- [ ] cargo fmt ok
- [ ] cargo clippy -D warnings ok
- [ ] cargo test ok

## Segurança e compliance
- [ ] Não adicionou execução de código analisado
- [ ] I/O restrito ao workspace/artefatos
- [ ] Outputs não vazam segredos/dados sensíveis

## Contratos
- [ ] Se tocou contracts, versionou corretamente
- [ ] Compatibilidade registrada (PATCH/MINOR/MAJOR)
