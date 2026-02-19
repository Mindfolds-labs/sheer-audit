# Sheer — Arquitetura do Sistema

Este diretório documenta a arquitetura técnica e de governança do **Sheer**.

A arquitetura é definida por:
- princípios não negociáveis
- modelo de execução determinístico
- separação clara de responsabilidades (core vs stages)
- decisões registradas em ADRs

## Visão geral

O Sheer é uma ferramenta de auditoria estática e governança técnica que:
- **não executa código analisado**
- opera de forma **determinística**
- produz **artefatos auditáveis baseados em evidência**
- separa core lógico (puro) de adaptadores de I/O

## Documentos principais
- [Princípios de Arquitetura](architecture_principles.md)
- [Visão do Sistema](system_overview.md)
- [Modelo de Execução](execution_model.md)
- [Fluxo de Dados e Evidência](data_flow.md)
- [Modelo de Segurança](security_model.md)
- [Camada de Governança](governance_layer.md)

## Decisões Arquiteturais (ADR)
- [ADR Index](adr/README.md)

## Escopo por versão

### v1 (atual)
- CLI local
- ingestão somente leitura
- IR baseado em grafo
- policies determinísticas (funções puras sobre IR)
- relatórios derivados (JSON/MD/HTML/CSV/SARIF)

### v2+ (planejado)
- agent restritivo
- auditoria central
- assinatura e distribuição de policies

## Fora de escopo explícito
- execução de código analisado
- shell remoto
- IA como executor/decisor (IA apenas consumidora/leitura do IR)
