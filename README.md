# Portfólio de Business Intelligence

Projetos de BI e análise de dados desenvolvidos por **Gustavo Monteiro** (Power BI, SQL, Python, ETL).
Todos os dados são **simulados** (gerados por `scripts/gerar_dados.py`) — nenhuma informação real de empresa.

## Projetos

| Projeto | Pergunta de negócio | Ferramentas | Arquivo |
|---|---|---|---|
| [Performance de Rede Móvel](projetos/telecom-performance-rede) | Quais sites estão degradando e qual o impacto na experiência do cliente? | Power BI, DAX, Power Query | `.pbix` |
| [Vendas Varejo](projetos/vendas-varejo) | Onde estão a receita, a margem e o desvio em relação à meta? | Power BI, DAX, Power Query | `.pbix` |

> Adicione aqui um print de cada dashboard (pasta `docs/imagens`).

## Como reproduzir

1. `pip install pandas numpy openpyxl`
2. `python scripts/gerar_dados.py` → cria os `.xlsx` em `dados/`
3. Abra o `.pbix` no Power BI Desktop e, se pedido, aponte a fonte para a pasta `dados/`.

## Estrutura

```
dados/        bases simuladas (.xlsx)
projetos/     um diretório por projeto (.pbix, README, prints)
sql/          consultas de apoio e análises
python/       notebooks e scripts de análise
docs/         dicionário de dados, modelo de dados, imagens
scripts/      gerador das bases
```

## Contato

LinkedIn: _adicione seu link_ · E-mail: _adicione seu e-mail_
