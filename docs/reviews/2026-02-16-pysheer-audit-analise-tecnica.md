# Análise técnica — PySheer Audit

## Escopo e método
- Auditoria estática (sem execução do código analisado), alinhada ao princípio de determinismo do projeto.
- Foco em: correção lógica, coerência entre modelo de configuração e implementação, estabilidade do fluxo de coleta, e integração CI/Git.

## Achados principais

### 1) Consistência de domínio na coleta de arquivos
**Problema:** `collect_python_files` ignorava `include_dirs`, reduzindo controle do domínio de varredura.

**Impacto:** aumento de falso-positivo/ruído e risco de custo computacional fora do escopo esperado.

**Correção aplicada:** inclusão explícita de `include_dirs` no algoritmo, com guarda para impedir paths fora do `root`.

### 2) Heurística de exclusão de testes
**Problema:** regra original baseada em substring podia excluir arquivos incorretamente.

**Impacto:** perda de cobertura de análise (falso-negativo).

**Correção aplicada:** predicado determinístico `_is_test_path` por diretórios (`test/tests`) e padrões de nome (`test_*.py`, `*_test.py`).

### 3) Tipagem e contrato de dados
**Problema:** uso de `any` em vez de `typing.Any` no schema.

**Impacto:** quebra de checagem estática e ambiguidade do contrato.

**Correção aplicada:** ajuste para `Any` no campo `Finding.excerpt`.

### 4) Robustez do parser de configuração
**Problema:** defaults com `None` para listas aumentam ramos condicionais e risco de erro futuro.

**Impacto:** menor previsibilidade em evolução de código.

**Correção aplicada:** `default_factory` em dataclasses e normalização para listas em `load_config`.

### 5) CI inexistente
**Problema:** sem gate automatizado para regressão.

**Impacto:** risco de drift arquitetural e quebra silenciosa.

**Correção aplicada:** workflow com matriz Python (3.10/3.11/3.12), `compileall` e `pytest`.

## Validação matemática e de estabilidade
Embora o projeto atual não implemente algoritmos numéricos iterativos (sem dinâmica de convergência formal), há propriedades formais relevantes:

- **Determinismo:** saída da coleta é função determinística de `(root, include_dirs, exclude_dirs, include_tests, max_file_kb)` com ordenação canônica.
- **Estabilidade operacional:** uso de conjuntos e ordenação final reduz variância por ordem de travessia do FS.
- **Domínio bem-definido:** guarda de escopo impede inclusão de paths externos ao repositório.

## Recomendações científicas/técnicas (próximas etapas)
1. Definir e monitorar métricas clássicas de qualidade estática (complexidade ciclomática de McCabe e maintainability index) para regressão contínua.
2. Adicionar análise de precisão/recall para findings em dataset curado de exemplos (golden set).
3. Introduzir property-based tests para invariantes de determinismo de scan (ex.: ordem de criação de arquivos não altera saída).

### Referências úteis
- McCabe, T. J. (1976). *A Complexity Measure*. IEEE TSE.
- Basili, V. R., Briand, L. C., Melo, W. L. (1996). *A Validation of Object-Oriented Design Metrics as Quality Indicators*. IEEE TSE.
- Claessen, K., Hughes, J. (2000). *QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs*. ICFP.
