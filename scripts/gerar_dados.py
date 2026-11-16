"""
Gera as bases SIMULADAS usadas nos projetos de Power BI deste repositório.
Todos os dados são sintéticos (nenhuma informação real de empresa).
Uso: python scripts/gerar_dados.py   (semente fixa -> resultado reprodutível)
"""
import numpy as np
import pandas as pd
from pathlib import Path

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
# Estrutura: regional > estado > município > site (ERB) > serviço (2G/3G, 4G VoLTE, 5G voNR)
# Eficiência (QoE) = (tentativas - (congestionamento + falhas técnicas + quedas + rel31 + rel127)) / tentativas * 100
ESTRUTURA = {
    "Regional Sudeste 1": {"MG": [("Belo Horizonte", "BHZ", 1), ("Contagem", "CTG", 0), ("Uberlândia", "UDI", 0), ("Juiz de Fora", "JFA", 0)],
                           "ES": [("Vitória", "VIX", 1), ("Vila Velha", "VLV", 0)]},
    "Regional Sudeste 2": {"SP": [("São Paulo", "SPO", 1), ("Campinas", "CPQ", 0), ("Santos", "SSZ", 0)],
                           "RJ": [("Rio de Janeiro", "RIO", 1), ("Niterói", "NIT", 0)]},
    "Regional Sul": {"PR": [("Curitiba", "CWB", 1), ("Londrina", "LDB", 0)],
                     "SC": [("Florianópolis", "FLN", 1), ("Joinville", "JOI", 0)],
                     "RS": [("Porto Alegre", "POA", 1), ("Caxias do Sul", "CXS", 0)]},
    "Regional Nordeste": {"BA": [("Salvador", "SSA", 1), ("Feira de Santana", "FSA", 0)],
                          "PE": [("Recife", "REC", 1), ("Caruaru", "CAU", 0)],
                          "CE": [("Fortaleza", "FOR", 1), ("Juazeiro do Norte", "JDO", 0)]},
    "Regional Centro-Norte": {"GO": [("Goiânia", "GYN", 1), ("Anápolis", "APS", 0)],
                              "DF": [("Brasília", "BSB", 1)],
                              "AM": [("Manaus", "MAO", 1)],
                              "PA": [("Belém", "BEL", 1)]},
}
SERVICOS = ["2G/3G", "4G (VoLTE)", "5G (voNR)"]


def telecom():
    r = np.random.default_rng(2026)
    # sites (ERBs) com siglas simuladas: UF + cidade + sequencial
    sites = []
    for regional, ufs in ESTRUTURA.items():
        for uf, cidades in ufs.items():
            for cidade, cod, capital in cidades:
                n = int(r.integers(3, 5)) if capital else int(r.integers(1, 3))
                for i in range(1, n + 1):
                    sites.append({"regional": regional, "estado": uf, "municipio": cidade,
                                  "site_erb": f"{uf}{cod}{i:02d}", "capital": capital,
                                  "tem_5g": bool(r.random() < (0.55 if capital else 0.25))})
    sites = pd.DataFrame(sites)
    sites["porte"] = np.where(sites.capital == 1, r.lognormal(0.35, .25, len(sites)), r.lognormal(-0.2, .3, len(sites)))
    sites["fator_falha"] = r.lognormal(0, .22, len(sites))        # sites melhores / piores

    # combinações site x serviço (5G só nos sites que têm)
    pares = []
    for _, s in sites.iterrows():
        for sv in SERVICOS:
            if sv == "5G (voNR)" and not s.tem_5g:
                continue
            pares.append({**s.to_dict(), "servico": sv})
    pares = pd.DataFrame(pares)

    datas = pd.date_range(end="2026-11-15", periods=730, freq="D")   # últimos 2 anos
    nd, npair = len(datas), len(pares)
    t = np.arange(nd)
    dow = datas.weekday.values
    mes_dia = datas.strftime("%m-%d").values

    # sazonalidade: fim de semana mais fraco; Natal/Ano Novo/Carnaval/Dia das Mães com pico de chamadas
    fator_dia = np.where(dow >= 5, 0.88, 1.0)
    pico = np.isin(mes_dia, ["12-24", "12-25", "12-31", "01-01", "05-10", "05-11"]) | \
           np.isin(datas.strftime("%Y-%m-%d").values, ["2025-03-03", "2025-03-04", "2026-02-16", "2026-02-17"])
    fator_pico = np.where(pico, 1.35, 1.0)

    base_vol = {"2G/3G": 3500, "4G (VoLTE)": 11000, "5G (voNR)": 4200}
    cresc = {"2G/3G": -0.00035, "4G (VoLTE)": 0.00025, "5G (voNR)": 0.0016}   # tendência de migração
    falha_srv = {"2G/3G": 1.18, "4G (VoLTE)": 0.95, "5G (voNR)": 0.88}

    # taxas-base por categoria (soma ~6,7% => eficiência ~93%)
    taxa = {"cong": .0215, "falha": .0135, "queda": .0155, "rel31": .0085, "rel127": .0065}

    # degradações programadas: 8 pares site-serviço + 1 evento estadual
    idx_deg = r.choice(npair, 8, replace=False)
    deg = {int(i): (int(r.integers(30, 690)), int(r.integers(6, 22)), float(r.uniform(2.5, 5.0))) for i in idx_deg}
    evento_uf, evento_ini = "BA", 400     # evento regional de 4 dias

    frames = []
    for i, p in pares.iterrows():
        vol = (base_vol[p.servico] * p.porte * (1 + cresc[p.servico] * t) * fator_dia * fator_pico
               * r.normal(1, .07, nd))
        tent = np.maximum(vol, 50).round().astype(int)
        mult = np.full(nd, p.fator_falha * falha_srv[p.servico])
        mult = mult * r.normal(1, .10, nd)
        cong_mult = mult * (1 + 0.35 * (fator_pico > 1)) * (1 + 0.15 * (p.capital == 1))
        m = {k: np.full(nd, 1.0) for k in taxa}
        if i in deg:
            ini, dur, forca = deg[i]
            sl = slice(ini, ini + dur)
            m["queda"][sl] = forca; m["falha"][sl] = forca * .8; m["rel127"][sl] = forca * .9
            m["cong"][sl] = 1.0 + (forca - 1) * .3
        if p.estado == evento_uf:
            sl = slice(evento_ini, evento_ini + 4)
            m["falha"][sl] = 3.0; m["queda"][sl] = 2.5
        cong = r.binomial(tent, np.clip(taxa["cong"] * cong_mult * m["cong"], 0, .5))
        falh = r.binomial(tent, np.clip(taxa["falha"] * mult * m["falha"], 0, .5))
        qued = r.binomial(tent, np.clip(taxa["queda"] * mult * m["queda"], 0, .5))
        r31 = r.binomial(tent, np.clip(taxa["rel31"] * mult * m["rel31"], 0, .5))
        r127 = r.binomial(tent, np.clip(taxa["rel127"] * mult * m["rel127"], 0, .5))
        ok = tent - (cong + falh + qued + r31 + r127)
        frames.append(pd.DataFrame({
            "data": datas, "regional": p.regional, "estado": p.estado, "municipio": p.municipio,
            "site_erb": p.site_erb, "servico": p.servico,
            "congestionamento": cong, "falhas_tecnicas": falh, "quedas_chamadas": qued,
            "total_rel31": r31, "total_rel127": r127, "total_tentativas": tent, "total_chamadas_ok": ok}))
    fato = pd.concat(frames, ignore_index=True)
    fato["eficiencia_pct"] = ((fato.total_tentativas - (fato.congestionamento + fato.falhas_tecnicas + fato.quedas_chamadas
                               + fato.total_rel31 + fato.total_rel127)) / fato.total_tentativas * 100).round(2)
    fato = fato.sort_values(["data", "regional", "estado", "municipio", "site_erb", "servico"]).reset_index(drop=True)
    assert (fato.total_chamadas_ok >= 0).all()

    cal = calendario(datas.min(), datas.max())
    with pd.ExcelWriter(OUT / "telecom_rede_movel.xlsx", engine="openpyxl", datetime_format="yyyy-mm-dd") as w:
        fato.to_excel(w, sheet_name="fato_qoe_diario", index=False)
        cal.to_excel(w, sheet_name="dim_calendario", index=False)
    tot = fato.total_tentativas.sum()
    ef = (tot - fato[["congestionamento", "falhas_tecnicas", "quedas_chamadas", "total_rel31", "total_rel127"]].sum().sum()) / tot * 100
    print(f"telecom: {len(fato)} linhas, {fato.site_erb.nunique()} sites, eficiência global {ef:.2f}%")


# ----------------------------------------------------------------- VENDAS
def vendas():
    rng = np.random.default_rng(7)
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
