# Diagrama — Threat Model (texto)

Entradas não confiáveis: repositório alvo
Superfícies:
- parsers (ingestão)
- geração de relatórios
- dependências da toolchain

Defesas:
- sem execução de código
- I/O restrito
- deny-by-default
- CI gates (lint/test)
