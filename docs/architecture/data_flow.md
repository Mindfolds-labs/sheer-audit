# Fluxo de Dados e Evidência

## Entradas
- repositório alvo (somente leitura)
- configuração (profile/pipeline) explícita

## Processamento
- IR versionado (grafo semântico)
- policies puras geram findings

## Saídas
- findings (com evidência)
- relatórios derivados (console/JSON/MD/HTML/CSV/SARIF)
- (opcional) SBOM, listas de dependências, resumos

## Regras
- nenhum dado é enviado remotamente (v1)
- nenhuma escrita fora do workspace autorizado
- redaction/mascaramento é aplicado conforme data_policy (quando aplicável)
