# 🔍 Sheer Audit / Ushel

Sistema profissional de análise de código Python.

## Quick Start

\\\ash
cd tools\sheer-audit
pip install -e .

sheer scan . -o artifacts/scan/repo_model.json
sheer report md . -o reports/report.md
sheer uml class . -o artifacts/uml/class.puml
\\\

## Recursos

- ✅ Scan completo de código
- ✅ Análise AST com findings
- ✅ UML (Class/Package/Sequence)
- ✅ Trace real via pytest
- ✅ Relatórios múltiplos formatos
- ✅ Arquitetura validada

## Comandos

\\\ash
sheer scan .
sheer report md .
sheer report csv .
sheer uml class .
sheer trace pytest .
\\\

## Autor

jrduães (JRDUAES90@GMAIL.COM)

## Licença

MIT