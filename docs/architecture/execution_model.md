# Modelo de Execução

## Pipeline padrão (v1)

1. **Ingestão (read-only)**
   - lê repositório alvo (somente leitura)
2. **Normalização**
   - converte dados para representações canônicas
3. **Construção do IR (grafo)**
   - nós = entidades; arestas = relações
4. **Execução de policies**
   - funções puras sobre o IR
5. **Geração de artefatos**
   - relatórios derivados (JSON/MD/HTML/CSV/SARIF)

## Garantias
- determinismo (entradas iguais ⇒ saídas iguais)
- workspace isolado
- I/O restrito (somente paths autorizados)
- sem execução do código analisado
