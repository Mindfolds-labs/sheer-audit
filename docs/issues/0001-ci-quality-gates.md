# Issue 0001 — Ausência de gates de CI para qualidade

## Problema
O repositório não possuía workflow de CI para validar sintaxe e testes em múltiplas versões de Python.

## Risco
- Regressões sem detecção precoce.
- Divergência entre ambientes de desenvolvimento e execução.

## Proposta
Adicionar workflow com:
- matrix Python 3.10/3.11/3.12
- instalação via `pip install -e .`
- `python -m compileall src`
- `pytest -q`

## Critério de aceite
PR bloqueada quando qualquer etapa falhar.
