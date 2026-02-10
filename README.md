# 🔍 Sheer Audit (Ushel)

Sistema profissional de análise de código Python (static analysis + modelagem semântica do repositório), com geração de relatórios, UML e validação de arquitetura.

> Foco: **entender e auditar** repositórios Python — símbolos (classes/funções/métodos), dependências, chamadas, camadas e evidências (findings).

---

## ✅ Recursos

- ✅ Scan completo do repositório (coleta de arquivos Python com filtros)
- ✅ Análise AST + geração de *findings*
- ✅ Modelagem de repositório (symbols/edges/findings/metrics)
- ✅ UML (Class / Package / Sequence)
- ✅ Trace real via pytest (quando habilitado)
- ✅ Relatórios em múltiplos formatos (ex.: Markdown/CSV)
- ✅ Validação de arquitetura (layers + regras de import)

---

## 🚀 Quick Start

### 1) Instalar em modo desenvolvimento
```bash
cd tools/sheer-audit
pip install -e .
2) Scan + Report + UML (exemplo)
sheer scan . -o artifacts/scan/repo_model.json
sheer report md . -o reports/report.md
sheer uml class . -o artifacts/uml/class.puml
Observação: se você estiver no Windows/PowerShell, pode usar os mesmos comandos.

🧭 Comandos principais
# Scan do repositório (gera o modelo: símbolos/arestas/findings/métricas)
sheer scan .

# Relatórios
sheer report md .
sheer report csv .

# UML
sheer uml class .
sheer uml package .
sheer uml sequence .

# Trace (quando configurado)
sheer trace pytest .
🧱 Arquitetura do projeto
O Sheer Audit segue uma organização em camadas, separando:

model (schema/contratos de dados)

config (carregamento de configurações)

scan (coleta do repositório)

cli (interface de linha de comando)

(e futuramente) analisadores AST / grafo / relatórios / geração UML / trace

Estrutura de pastas (atual)
sheer-audit/
├─ src/
│  └─ sheer_audit/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ config.py
│     ├─ model/
│     │  ├─ __init__.py
│     │  └─ schema.py
│     └─ scan/
│        ├─ __init__.py
│        └─ repo.py
│
├─ docs/
│  ├─ adr/
│  │  └─ 0001-template.md
│  ├─ blueprints/
│  │  └─ template.md
│  └─ atas/
│     └─ 0001-template.md
│
├─ artifacts/          # saída de execuções (scan, uml, trace, etc.)
├─ reports/            # relatórios gerados
├─ tests/              # testes automatizados
├─ pyproject.toml
├─ sheer.toml          # configuração do projeto (scanner/audit/trace/uml/etc.)
└─ README.md
⚙️ Configuração (sheer.toml)
A configuração do Sheer Audit é carregada via sheer.toml (TOML).
Pontos importantes:

scan: include/exclude dirs, limite de tamanho, incluir testes

audit: escopo e exclusões

trace: habilitar, profundidade, módulos ignorados

uml: engine, output_dir

architecture: layers, paths e regras de import proibidas

docs: diretórios de ADR/blueprints/atas

🧾 ADR (Architecture Decision Records)
Decisões de arquitetura ficam em: docs/adr/.

Como criar um ADR novo
Copie o template:

cp docs/adr/0001-template.md docs/adr/0002-<titulo-curto>.md
Preencha:

Contexto

Decisão

Consequências

Alternativas consideradas

Faça commit junto com a mudança de código que motivou a decisão.

Regra prática: mudou arquitetura, formato de schema, pipeline de scan/análise ou CLI? Crie/atualize um ADR.

🧪 Desenvolvimento
Rodar testes
pytest -q
Estilo e qualidade
Recomendado usar:

ruff (lint/format)

mypy (tipagem)

👤 Autor
jrduães — JRDUAES90@GMAIL.COM
