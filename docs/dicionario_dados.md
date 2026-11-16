# Dicionário de dados

## telecom_rede_movel.xlsx
Base diária de qualidade de voz (QoE) por site (ERB) e serviço — 2 anos (16/11/2024 a 15/11/2026), ~126 mil linhas.

| Coluna | Descrição |
|---|---|
| data | Dia da medição |
| regional | Regional (5): Sudeste 1, Sudeste 2, Sul, Nordeste, Centro-Norte |
| estado | UF (14 estados) |
| municipio | Município (28) |
| site_erb | Sigla simulada da ERB: UF + cidade + sequencial (ex.: MGBHZ01) |
| servico | 2G/3G, 4G (VoLTE) ou 5G (voNR) |
| congestionamento | Total de chamadas com congestionamento |
| falhas_tecnicas | Total de chamadas com falha técnica |
| quedas_chamadas | Total de quedas de chamadas |
| total_rel31 | Total de liberações REL 31 |
| total_rel127 | Total de liberações REL 127 |
| total_tentativas | Total de tentativas de chamada |
| total_chamadas_ok | Tentativas − (congestionamento + falhas + quedas + REL 31 + REL 127) |
| eficiencia_pct | QoE da linha = (tentativas − (cong. + falhas + quedas + REL 31 + REL 127)) / tentativas × 100 |

**Atenção ao calcular a eficiência no Power BI:** para regional, estado, mês etc., **não faça média** da coluna `eficiencia_pct`.
Use uma medida que soma antes de dividir:

```DAX
Eficiencia % =
DIVIDE(
    SUM(fato_qoe_diario[total_tentativas])
        - ( SUM(fato_qoe_diario[congestionamento]) + SUM(fato_qoe_diario[falhas_tecnicas])
          + SUM(fato_qoe_diario[quedas_chamadas]) + SUM(fato_qoe_diario[total_rel31])
          + SUM(fato_qoe_diario[total_rel127]) ),
    SUM(fato_qoe_diario[total_tentativas])
) * 100
```

Perfil simulado: eficiência global ≈ 93%; 2G/3G um pouco abaixo, 4G próximo da média e 5G acima.
A base inclui picos de congestionamento (Natal, Ano Novo, Carnaval, Dia das Mães), 8 casos de degradação
site/serviço (7 a 21 dias) e um evento de 4 dias na Bahia — o dashboard deve revelá-los.

## vendas_varejo.xlsx
| Tabela | Coluna | Descrição |
|---|---|---|
| fato_vendas | receita | quantidade × preço × (1 − desconto) |
| | custo_total | quantidade × custo unitário |
| fato_metas | meta_receita | Meta mensal por equipe |

Relacionamentos: fatos ligam às dimensões por `site_id`, `produto_id`, `cliente_id`, `vendedor_id` e `data`; metas por `ano_mes` + `equipe`.
