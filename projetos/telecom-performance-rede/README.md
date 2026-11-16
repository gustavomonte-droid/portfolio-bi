# Performance de Rede Móvel (dados simulados)

## Contexto e problema
Operadoras acompanham milhares de sites. O desafio é **achar rápido os desvios de performance**
(queda de chamadas, acesso, vazão e latência) e priorizar a ação.

## Dados (`dados/telecom_rede_movel.xlsx`)
`dim_calendario`, `dim_site`, `fato_kpi_diario` (24 mil linhas), `fato_incidentes`.
Contém 10 sites com degradação propositalmente injetada — o dashboard deve revelá-los.

## O que o dashboard mostra (sugestão)
- KPIs: tráfego, queda %, acesso %, throughput, latência, disponibilidade
- Mapa de sites por criticidade e ranking dos piores ofensores
- Tendência diária com banda de desvio (média ± 2σ)
- Incidentes por causa e severidade (Pareto) e MTTR

## Técnicas
Power Query (ETL), modelo estrela, medidas DAX (YTD, variação vs. período anterior,
detecção de desvio), tooltips e drill-through.

## Resultados / insights
_Preencha com 3 achados reais do seu dashboard._

## Print
![dashboard](../../docs/imagens/telecom.png)
