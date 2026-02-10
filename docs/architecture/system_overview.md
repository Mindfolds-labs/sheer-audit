# Visão do Sistema

## Componentes (topologia lógica)

- **sheer (CLI)**: entrada do usuário, orquestra o pipeline e outputs
- **core**: construção do IR (grafo) + execução de policies puras + findings
- **stages**: adaptadores de I/O (ingestão read-only, escrita de artefatos)
- **contracts**: schemas/IDL versionados para entradas, saídas e IR

## Responsabilidades

### CLI
- parse de argumentos
- seleção de profile/pipeline permitido
- chama stages e core
- não contém lógica de auditoria

### Core
- sem I/O e sem efeitos colaterais
- constrói IR e avalia policies determinísticas
- findings incluem evidência + policy + severidade

### Stages
- leitura controlada do repositório alvo (read-only)
- escrita apenas no diretório de artefatos
- conversão para formatos (MD/HTML/CSV/SARIF)

### Contracts
- definem fronteiras estáveis
- são versionados (ex.: contracts/v1)
- mudanças seguem compatibilidade (PATCH/MINOR/MAJOR)
