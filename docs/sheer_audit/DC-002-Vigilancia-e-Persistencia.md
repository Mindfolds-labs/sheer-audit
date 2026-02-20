# DC-SA-002: Especificação de Vigilância Semântica e Persistência Binária

## 1. Objetivo
Estabelecer a camada de segurança interna (MindAxis), gestão atómica de dependências (AxisFolds) e persistência imutável de registos (SheerDB).

## 2. Componentes
- **MindAxis / advanced scan**: validação estrutural via AST.
- **AxisFolds**: lock de dependências a partir do `pyproject.toml`.
- **SheerDB**: append-only log com assinatura HMAC por linha.

## 3. Fluxo de Integridade
`Deteção -> Assinatura HMAC -> Escrita Append-Only -> Verificação`

## 4. Operações CLI
- `sheer advanced --ieee`
- `sheer audit-secure`
- `sheer db --verify | --export-csv | --purge`
- `sheer axisfolds`
