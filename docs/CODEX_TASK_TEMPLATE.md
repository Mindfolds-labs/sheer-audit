# CODEX_TASK_TEMPLATE — Cole no Codex

## Objetivo
(Descreva a mudança em 1–3 linhas)

## Escopo permitido
- Pode mexer em:
  - (liste pastas/arquivos)
- Não pode mexer em:
  - (liste pastas/arquivos)

## Restrições (obrigatório respeitar)
- Core (sheer_core) sem I/O/FS/rede/env/relógio
- Determinismo (entradas iguais => saídas iguais)
- Contract-first (se mudar schema, versionar)
- Evidence-first (findings com evidência)

## ADRs e Docs impactados
- ADR-XXXX (…)
- docs/architecture/… (…)
(Se nenhum, diga explicitamente “nenhum”.)

## Passos esperados
1)
2)
3)

## Validação obrigatória
cd sheer
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all --all-features

## Evidência no PR
- Comandos rodados + resultado
- Arquivos tocados
- Referência aos ADRs
