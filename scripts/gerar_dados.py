"""
Gera as bases SIMULADAS usadas nos projetos de Power BI deste repositório.
Todos os dados são sintéticos (nenhuma informação real de empresa).
Uso: python scripts/gerar_dados.py   (semente fixa -> resultado reprodutível)
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parent.parent / "dados"
OUT.mkdir(exist_ok=True)


def calendario(ini, fim):
    d = pd.date_range(ini, fim, freq="D")
    nomes_mes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    nomes_dia = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
    return pd.DataFrame({
        "data": d, "ano": d.year, "mes": d.month,
        "mes_nome": [nomes_mes[m-1] for m in d.month],
        "ano_mes": d.strftime("%Y-%m"),
        "trimestre": "T" + d.quarter.astype(str),
        "dia_semana": [nomes_dia[w] for w in d.weekday],
        "fim_de_semana": d.weekday >= 5,
    })


# ---------------------------------------------------------------- TELECOM
def telecom():
    cidades = [("Belo Horizonte","Centro-Sul",-19.92,-43.94),("Contagem","Centro-Sul",-19.93,-44.05),
               ("Betim","Centro-Sul",-19.97,-44.20),("Uberlândia","Triângulo",-18.92,-48.28),
               ("Juiz de Fora","Zona da Mata",-21.76,-43.35),("Montes Claros","Norte",-16.73,-43.86),
               ("Ipatinga","Vale do Aço",-19.47,-42.54),("Uberaba","Triângulo",-19.75,-47.93),
               ("Divinópolis","Oeste",-20.14,-44.88),("Poços de Caldas","Sul",-21.79,-46.56)]
    fornecedores = ["Fornecedor A","Fornecedor B","Fornecedor C"]
    n_sites = 80
    sites = pd.DataFrame({
        "site_id": [f"SIT{str(i).zfill(3)}" for i in range(1, n_sites + 1)],
    })
    idx = rng.integers(0, len(cidades), n_sites)
    sites["cidade"] = [cidades[i][0] for i in idx]
    sites["regiao"] = [cidades[i][1] for i in idx]
    sites["latitude"] = [round(cidades[i][2] + rng.normal(0, .04), 5) for i in idx]
    sites["longitude"] = [round(cidades[i][3] + rng.normal(0, .04), 5) for i in idx]
    sites["tecnologia"] = rng.choice(["4G", "5G"], n_sites, p=[.65, .35])
    sites["fornecedor"] = rng.choice(fornecedores, n_sites)
    sites["morfologia"] = rng.choice(["Urbano denso", "Urbano", "Suburbano", "Rural"], n_sites, p=[.25, .4, .25, .1])

    cal = calendario("2026-01-01", "2026-10-31")
    datas = cal["data"].values
    rows = []
    base_trafego = {"Urbano denso": 900, "Urbano": 550, "Suburbano": 300, "Rural": 120}
    # sites com degradação programada (história para a análise de desvios)
    degradados = rng.choice(sites["site_id"], 10, replace=False)
    janela = {s: (rng.integers(30, 250), rng.integers(7, 25)) for s in degradados}
    for _, s in sites.iterrows():
        t = np.arange(len(datas))
        crescimento = 1 + 0.0009 * t                      # tráfego cresce ao longo do ano
        semana = 1 - 0.08 * (pd.DatetimeIndex(datas).weekday >= 5)
        fator5g = 1.6 if s.tecnologia == "5G" else 1.0
        traf = base_trafego[s.morfologia] * fator5g * crescimento * semana * rng.normal(1, .06, len(t))
        usuarios = traf / rng.normal(0.35, .03, len(t))
        prb = np.clip(35 + traf / base_trafego[s.morfologia] * 20 + rng.normal(0, 4, len(t)), 5, 99)
        queda = np.clip(rng.normal(0.35, .12, len(t)) + (prb > 85) * .5, 0.02, None)
        acesso = np.clip(rng.normal(99.2, .25, len(t)) - (prb > 85) * 1.2, 90, 100)
        thr = np.clip(rng.normal(38 if s.tecnologia == "4G" else 160, 6, len(t)) * (1.15 - prb / 250), 3, None)
        lat = np.clip(rng.normal(32 if s.tecnologia == "4G" else 14, 3, len(t)) * (1 + (prb > 85) * .35), 5, None)
        disp = np.clip(rng.normal(99.85, .08, len(t)), 97, 100)
        if s.site_id in janela:
            ini, dur = janela[s.site_id]
            sl = slice(ini, ini + dur)
            queda[sl] += rng.uniform(1.5, 3.5); acesso[sl] -= rng.uniform(3, 7)
            thr[sl] *= .55; lat[sl] *= 1.8; disp[sl] -= rng.uniform(.5, 2)
        rows.append(pd.DataFrame({
            "data": datas, "site_id": s.site_id,
            "trafego_dados_gb": traf.round(1), "usuarios_medios": usuarios.round(0).astype(int),
            "utilizacao_prb_pct": prb.round(1), "taxa_queda_pct": queda.round(2),
            "taxa_sucesso_acesso_pct": acesso.round(2), "throughput_mbps": thr.round(1),
            "latencia_ms": lat.round(1), "disponibilidade_pct": disp.round(2),
        }))
    kpi = pd.concat(rows, ignore_index=True)

    # incidentes
    n_inc = 420
    inc = pd.DataFrame({
        "incidente_id": [f"INC{str(i).zfill(4)}" for i in range(1, n_inc + 1)],
        "data_inicio": pd.to_datetime(rng.choice(datas, n_inc)),
        "site_id": rng.choice(sites["site_id"], n_inc),
        "severidade": rng.choice(["Crítica", "Alta", "Média", "Baixa"], n_inc, p=[.08, .22, .4, .3]),
        "causa": rng.choice(["Energia", "Transmissão", "Hardware", "Software", "Configuração", "Vandalismo"], n_inc,
                            p=[.3, .22, .15, .13, .12, .08]),
    })
    inc["duracao_min"] = (rng.gamma(2.0, 60, n_inc) * inc["severidade"].map(
        {"Crítica": 2.2, "Alta": 1.5, "Média": 1.0, "Baixa": .6})).round(0).astype(int)
    inc = inc.sort_values("data_inicio").reset_index(drop=True)

    with pd.ExcelWriter(OUT / "telecom_rede_movel.xlsx", engine="openpyxl", datetime_format="yyyy-mm-dd") as w:
        cal.to_excel(w, "dim_calendario", index=False)
        sites.to_excel(w, "dim_site", index=False)
        kpi.to_excel(w, "fato_kpi_diario", index=False)
        inc.to_excel(w, "fato_incidentes", index=False)
    print("telecom:", len(kpi), "linhas de KPI,", len(inc), "incidentes")


# ----------------------------------------------------------------- VENDAS
def vendas():
    cal = calendario("2024-01-01", "2026-10-31")
    cats = {"Eletrônicos": (400, 3500, .22), "Informática": (250, 6000, .18), "Casa": (60, 900, .35),
            "Esporte": (50, 700, .38), "Papelaria": (8, 120, .5)}
    prod = []
    for c, (lo, hi, margem) in cats.items():
        for i in range(1, 13):
            preco = round(float(np.exp(rng.uniform(np.log(lo), np.log(hi)))), 2)
            prod.append({"produto_id": f"P{len(prod)+1:03d}", "produto": f"{c} Modelo {i}", "categoria": c,
                         "preco_lista": preco, "custo": round(preco * (1 - margem * rng.uniform(.8, 1.2)), 2)})
    prod = pd.DataFrame(prod)

    estados = {"MG": .3, "SP": .35, "RJ": .15, "BA": .08, "PR": .07, "RS": .05}
    n_cli = 600
    cli = pd.DataFrame({
        "cliente_id": [f"C{str(i).zfill(4)}" for i in range(1, n_cli + 1)],
        "segmento": rng.choice(["Varejo", "Corporativo", "Governo"], n_cli, p=[.7, .25, .05]),
        "estado": rng.choice(list(estados), n_cli, p=list(estados.values())),
    })
    vend = pd.DataFrame({"vendedor_id": [f"V{i:02d}" for i in range(1, 16)],
                         "vendedor": [f"Vendedor {i}" for i in range(1, 16)],
                         "equipe": rng.choice(["Norte", "Sul", "Sudeste"], 15)})

    n = 24000
    datas = cal["data"].values
    peso = np.array([1 + .35 * (pd.Timestamp(d).month in (11, 12)) + .0012 * i for i, d in enumerate(datas)])
    dt = rng.choice(datas, n, p=peso / peso.sum())
    p = prod.sample(n, replace=True, random_state=1).reset_index(drop=True)
    f = pd.DataFrame({
        "pedido_id": [f"PED{i:06d}" for i in range(1, n + 1)],
        "data": pd.to_datetime(dt),
        "cliente_id": rng.choice(cli["cliente_id"], n),
        "produto_id": p["produto_id"], "vendedor_id": rng.choice(vend["vendedor_id"], n),
        "quantidade": rng.choice([1, 1, 1, 2, 2, 3, 5, 10], n),
        "preco_unitario": p["preco_lista"],
        "desconto_pct": rng.choice([0, 0, 0, 5, 10, 15], n),
        "custo_unitario": p["custo"],
    })
    f["receita"] = (f.quantidade * f.preco_unitario * (1 - f.desconto_pct / 100)).round(2)
    f["custo_total"] = (f.quantidade * f.custo_unitario).round(2)
    f = f.sort_values("data").reset_index(drop=True)

    meses = pd.period_range("2024-01", "2026-10", freq="M").astype(str)
    metas = pd.DataFrame([(m, e, round(float(rng.uniform(.9, 1.15) * 450000 * (1 + .01 * i)), 0))
                          for i, m in enumerate(meses) for e in ["Norte", "Sul", "Sudeste"]],
                         columns=["ano_mes", "equipe", "meta_receita"])

    with pd.ExcelWriter(OUT / "vendas_varejo.xlsx", engine="openpyxl", datetime_format="yyyy-mm-dd") as w:
        cal.to_excel(w, "dim_calendario", index=False)
        prod.to_excel(w, "dim_produto", index=False)
        cli.to_excel(w, "dim_cliente", index=False)
        vend.to_excel(w, "dim_vendedor", index=False)
        f.to_excel(w, "fato_vendas", index=False)
        metas.to_excel(w, "fato_metas", index=False)
    print("vendas:", len(f), "linhas")


if __name__ == "__main__":
    telecom()
    vendas()
