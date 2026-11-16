# Dicionário de dados

## telecom_rede_movel.xlsx
| Tabela | Coluna | Descrição |
|---|---|---|
| fato_kpi_diario | trafego_dados_gb | Volume de dados do dia no site |
| | usuarios_medios | Usuários simultâneos médios |
| | utilizacao_prb_pct | Ocupação de recursos de rádio (PRB) |
| | taxa_queda_pct | % de chamadas/sessões derrubadas |
| | taxa_sucesso_acesso_pct | % de acessos bem-sucedidos |
| | throughput_mbps | Vazão média por usuário |
| | latencia_ms | Latência média |
| | disponibilidade_pct | Disponibilidade do site |
| fato_incidentes | duracao_min | Duração do incidente em minutos |
| dim_site | morfologia | Urbano denso, Urbano, Suburbano, Rural |

## vendas_varejo.xlsx
| Tabela | Coluna | Descrição |
|---|---|---|
| fato_vendas | receita | quantidade × preço × (1 − desconto) |
| | custo_total | quantidade × custo unitário |
| fato_metas | meta_receita | Meta mensal por equipe |

Relacionamentos: fatos ligam às dimensões por `site_id`, `produto_id`, `cliente_id`, `vendedor_id` e `data`; metas por `ano_mes` + `equipe`.
