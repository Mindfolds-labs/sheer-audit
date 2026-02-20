# DC-SA-002: Especificação de Vigilância Semântica e Persistência Binária

## 1. Objetivo
Estabelecer a camada de segurança interna (MindAxis), a gestão atómica de dependências (AxisFolds) e a persistência imutável de registos (SheerDB).

## 2. Componentes de Segurança
- **MindAxis**: auditor estrutural AST.
- **AxisFolds**: controlador de snapshot determinístico de dependências.
- **SheerDB**: base append-only com assinatura HMAC por linha.

## 3. Fluxo de Integridade
`Deteção (Scanner) -> Assinatura (HMAC) -> Escrita (SheerDB) -> Alinhamento (Plano Cartesiano)`
