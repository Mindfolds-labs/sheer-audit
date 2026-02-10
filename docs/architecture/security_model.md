# Modelo de Segurança

## Objetivo
Minimizar superfície de ataque e evitar exfiltração/execução indevida.

## Ameaças consideradas
- execução de código malicioso do repo analisado
- escrita fora do workspace (persistence/overwrites)
- exfiltração via outputs/relatórios
- shell remoto (agent)
- injeção/alteração maliciosa de policies
- IA usada como agente decisor/executor

## Mitigações por design
- não executar código analisado
- workspace e I/O restritos
- deny by default por profile
- policies versionadas e testáveis
- (v2+) policies assinadas para distribuição
- IA apenas consumidora do IR (sem decisões oficiais)
