# AGENTS.md — Instruções para Codex (Sheer Audit)

Você é um agente de engenharia trabalhando no repositório **Sheer**.
Seu trabalho deve ser **auditável**, **determinístico** e **alinhado** aos ADRs e à arquitetura.

## Fontes de Verdade
- docs/architecture/README.md
- docs/architecture/architecture_principles.md
- docs/architecture/system_overview.md
- docs/architecture/execution_model.md
- docs/architecture/data_flow.md
- docs/architecture/security_model.md
- docs/architecture/adr/ (ADRs Accepted)

## Regras de Ouro
1) Não executar código analisado (auditoria estática).
2) Core é puro: sem I/O, rede, FS, env, relógio.
3) Stages fazem I/O: ingestão read-only; outputs só em workspace/artefatos permitidos.
4) Determinismo: mesmas entradas => mesmas saídas.
5) Evidence-first: findings devem ter evidência verificável.
6) Contract-first: contratos versionados; compatibilidade explícita.
7) Deny by default: perfis/pipelines restritivos por padrão.
8) IA não decide: pode sugerir, mas findings oficiais vêm de policies determinísticas.

## Organização
- sheer/crates/sheer_core/ — lógica pura (IR + policies)
- sheer/crates/sheer_stages/ — I/O e formatos
- sheer/crates/sheer_cli/ — CLI
- contracts/ — schemas versionados
- docs/ — governança e evidências
- .github/workflows/ — CI gates

## Processo de mudança
1) Identifique ADR/docs impactados.
2) Plano curto (3–6 passos).
3) Mudanças pequenas e revisáveis.
4) Atualize docs/ADRs se necessário.
5) Rode validações e registre evidência.

## Validações obrigatórias
cd sheer
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all --all-features

## Proibições
- Não adicionar I/O/rede ao sheer_core.
- Não introduzir não-determinismo (tempo/aleatório sem seed fixo).
- Não remover gates de CI.
- Não criar shell remoto.
