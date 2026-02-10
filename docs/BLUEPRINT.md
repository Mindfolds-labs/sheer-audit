# BLUEPRINT — Sheer (Projeto Completo)

Este documento descreve a estrutura completa do projeto, responsabilidades e entregáveis auditáveis.

## 1. Objetivo
Ferramenta de auditoria estática e governança técnica com:
- determinismo
- evidence-first
- contract-first
- execução restrita (sem executar código analisado)

## 2. Topologia (v1)
- CLI local (sheer)
- core lógico (IR + policies)
- stages (I/O controlado)
- contracts versionados
- relatórios derivados

## 3. Layout recomendado do repositório

- docs/
  - architecture/ (arquitetura + ADR)
  - compliance/ (evidências e mapeamento de controles)
  - security/ (baselines)
- contracts/
  - v1/ (schemas/IDL)
- sheer/
  - crates/
    - sheer_core/ (puro)
    - sheer_stages/ (I/O)
    - sheer_cli/ (interface)
- artifacts/ (saídas geradas; não versionar por padrão)

## 4. Responsabilidades (core vs stages)

### Core (puro)
- build do IR (grafo)
- policies determinísticas
- findings com evidência
- sem I/O

### Stages (I/O)
- ingestão read-only
- outputs somente em artifacts/
- formatação para JSON/MD/HTML/CSV/SARIF

## 5. Contratos (contract-first)
- contracts/v1/*.schema.json
- compatibilidade: PATCH/MINOR/MAJOR
- IR inclui versões (producer/tool/profile)

## 6. Evidências (auditáveis)
Mínimo recomendado no CI:
- format/lint (rustfmt/clippy, ou equivalente)
- testes (unit + smoke)
- geração de artefatos de execução (quando aplicável)
- SBOM e verificação de licenças (quando aplicável)

## 7. Segurança (deny by default)
- sem execução do código analisado
- sem shell remoto (v2+)
- workspace isolado
- proibição de escrita fora do workspace
- IA apenas consumidora do IR

## 8. Roadmap (alto nível)

### v1
- CLI + IR + policies + relatórios
- docs completos e auditáveis
- CI gates mínimos

### v2+
- agent restritivo
- audit server (central)
- assinatura de policies
