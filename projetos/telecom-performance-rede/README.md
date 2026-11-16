# Qualidade de Voz da Rede Móvel — QoE (dados simulados)

## Contexto e problema
Acompanhar a **eficiência (QoE) das chamadas** por regional, estado, município, site (ERB) e serviço
(2G/3G, 4G VoLTE, 5G voNR) e **achar rápido onde a experiência do cliente está degradando**.

## Dados (`dados/telecom_rede_movel.xlsx`)
- `fato_qoe_diario`: 126 mil linhas, 70 sites, 28 municípios, 14 estados, 2 anos diários.
- `dim_calendario`.
- Métricas: congestionamento, falhas técnicas, quedas, REL 31, REL 127, tentativas, chamadas OK e eficiência.
- Eficiência = (tentativas − (cong. + falhas + quedas + REL 31 + REL 127)) / tentativas × 100 — global ≈ 93%.

## O que o dashboard mostra (sugestão)
- KPI de eficiência vs. meta, com variação contra o período anterior
- Drill regional → estado → município → site, por serviço
- Tendência diária com banda de desvio e destaque dos dias fora do padrão
- Composição das perdas (congestionamento, falhas, quedas, REL 31, REL 127) e ranking dos piores sites

## Técnicas
Power Query (ETL), DAX (medida de eficiência ponderada, YTD, variação), hierarquia geográfica, drill-through.

## Resultados / insights
_Preencha com 3 achados reais do seu dashboard._

## Print
![dashboard](../../docs/imagens/telecom.png)
