# Policy — Uso do ChatGPT Codex no Sheer

## Princípios do projeto (obrigatórios)
- Core puro (sem I/O, rede, FS, env, relógio)
- Determinismo
- Contract-first (schemas versionados)
- Evidence-first (findings com evidência)
- Deny-by-default
- Sem execução de código analisado

## O agente deve sempre:
- ler \docs/architecture/README.md\ e ADRs relevantes
- declarar o impacto em arquitetura/ADRs
- registrar verificação (comandos e resultados)
- registrar evidências (paths/artefatos/logs)

## Proibido:
- adicionar I/O ao core
- introduzir não-determinismo sem controle
- remover gates de CI
- criar shell remoto
