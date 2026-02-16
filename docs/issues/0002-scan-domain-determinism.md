# Issue 0002 — Domínio de scan e determinismo

## Problema
A coleta de arquivos não aplicava `include_dirs`, e havia risco de exclusão incorreta por heurística ampla de testes.

## Risco
- Ruído em findings por escopo excessivo.
- Falsos-negativos por exclusão indevida.

## Proposta
- Respeitar `include_dirs`.
- Implementar predicado de teste explícito e determinístico.
- Proteger contra paths fora do root.

## Critério de aceite
- Testes automatizados cobrindo inclusão/exclusão e proteção de escopo.
