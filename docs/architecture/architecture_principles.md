# Princípios de Arquitetura — Sheer

Os princípios abaixo são **obrigatórios**. Violação só com ADR explícito.

## 1. Determinismo
- Mesmas entradas ⇒ mesmas saídas
- Sem dependência de tempo, rede ou estado externo

## 2. Evidence-first
- Todo finding deve conter evidência verificável
- Sem “opinião implícita”: evidência aponta para entidades/caminhos no IR

## 3. Separação de responsabilidades
- CLI orquestra
- Core contém lógica pura (IR + policies)
- Stages fazem I/O controlado (ingestão/outputs)

## 4. Side-effect free core
- Core não acessa FS, rede, env, relógio, secrets
- Core expõe funções puras (ou quase puras, com erros determinísticos)

## 5. Contract-first
- Contratos versionados e revisados
- Compatibilidade explícita e rastreável

## 6. Deny by default
- Tudo que não é permitido é proibido
- Perfis de execução restringem pipelines e formatos

## 7. Auditoria como requisito
- Evidências geradas automaticamente (CI)
- Artefatos versionados e reprodutíveis
