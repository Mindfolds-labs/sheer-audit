# Issue 0003 — Camada de governança derivada de relatórios

## Problema
Findings técnicos não tinham mecanismo padrão para virar backlog priorizado e decisão arquitetural rastreável.

## Risco
- Perda de rastreabilidade entre evidência e ação.
- Priorização inconsistente entre ciclos de auditoria.
- ADRs criados tardiamente ou sem vínculo explícito com evidências.

## Proposta
Implementar pipeline determinístico que converte `RepoModel.findings` em:
- issues priorizadas,
- blueprint de evolução,
- texto-base de ADR.

A priorização segue função linear monotônica por severidade com pesos fixos.

## Critério de aceite
- Mesmas entradas geram os mesmos artefatos de governança.
- Backlog ordenado por score e severidade máxima.
- Artefatos incluem fingerprint do relatório origem.
