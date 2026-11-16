# Vendas Varejo (dados simulados)

## Contexto e problema
Acompanhar receita, margem e atingimento de meta por equipe, categoria e cliente.

## Dados (`dados/vendas_varejo.xlsx`)
`fato_vendas` (24 mil pedidos), `fato_metas`, `dim_produto`, `dim_cliente`, `dim_vendedor`, `dim_calendario`.

## O que o dashboard mostra (sugestão)
- Receita, margem %, ticket médio e pedidos, com comparação vs. ano anterior
- Realizado × meta por equipe e mês
- Curva ABC de produtos/clientes e impacto de descontos na margem

## Técnicas
Modelo estrela, DAX (time intelligence, ABC, atingimento de meta), segmentação e RLS (opcional).

## Resultados / insights
_Preencha com 3 achados reais do seu dashboard._

## Print
![dashboard](../../docs/imagens/vendas.png)
