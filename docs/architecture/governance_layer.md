# Camada de Governança Derivada de Relatórios

## Objetivo
Estabelecer uma camada deterministicamente auditável para transformar o relatório do Sheer em:
1. backlog de issues,
2. blueprint de evolução,
3. proposta de ADR.

## Motivação
Sem mecanismo explícito, findings podem virar ações ad hoc sem rastreabilidade formal.
A camada de governança fecha esse gap ligando evidência técnica a decisões de arquitetura.

O fluxo também é compatível com práticas do ecossistema Mindfolds (ex.: trilha issue → blueprint → ADR), preservando auditoria determinística no Sheer.

## Modelo de priorização
A priorização usa função linear sobre severidade:

\[
\text{score(issue)} = \sum_{f \in F(issue)} w(\text{severity}(f))
\]

Com pesos fixos e monotônicos:
- INFO = 1
- WARN = 3
- ERROR = 8
- CRITICAL = 13

Propriedades:
- monotonicidade: adicionar evidência nunca reduz score,
- interpretabilidade: score maior implica maior carga de risco,
- determinismo: sem tempo, rede ou estado externo.

## Fluxo
1. Consumir `RepoModel.findings`.
2. Agrupar por `finding.code`.
3. Calcular score, severidade máxima e cardinalidade de evidências.
4. Produzir artefatos Markdown com fingerprint SHA-256 do relatório normalizado.

## Evidências geradas
- `issues_markdown`: backlog priorizado por score.
- `blueprint_markdown`: plano de evolução focado nos códigos críticos.
- `adr_markdown`: decisão arquitetural proposta e consequências.

## Limites de segurança
- não executa código auditado,
- não depende de relógio,
- não faz I/O de rede,
- não decide findings: apenas transforma findings já determinísticos em governança.
