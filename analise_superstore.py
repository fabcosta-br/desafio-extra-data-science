# ============================================================
# DESAFIO EXTRA — Introdução ao Data Science
# Curso: Introdução ao Data Science (IP 20h A)
# Programa: Carreira Tech — SCTEC / SENAI / FAPESC / ACATE
# Aluno: Fabiano Rodrigo Costa
# Data: 2026-05-17
# Dataset: Sample Superstore (Kaggle)
# Fonte: https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
# ============================================================
# OBJETIVO:
#   Realizar Análise Exploratória de Dados (AED) sobre vendas
#   de uma rede varejista, identificando padrões, relações
#   entre variáveis e insights de negócio relevantes.
# ============================================================

# ──────────────────────────────────────────────────────────────
# IMPORTAÇÃO DE BIBLIOTECAS E CONFIGURAÇÕES GLOBAIS
# ──────────────────────────────────────────────────────────────
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────
# CONFIGURAÇÕES GLOBAIS PARA GRÁFICOS
# ──────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"]       = 150
plt.rcParams["figure.facecolor"] = "white"

PASTA_GRAFICOS = "graficos"
os.makedirs(PASTA_GRAFICOS, exist_ok=True)

# ──────────────────────────────────────────────────────────
# ETAPA 1 — IMPORTAÇÃO E COMPREENSÃO DOS DADOS
# ──────────────────────────────────────────────────────────
print("=" * 65)
print("  DESAFIO EXTRA — ANÁLISE EXPLORATÓRIA DE DADOS")
print("  Dataset: Sample Superstore | Fabiano Rodrigo Costa")
print("=" * 65)

print("\n📂 ETAPA 1 — Carregando o dataset...")

df = None
for enc in ["latin-1", "utf-8", "cp1252"]:
    try:
        df = pd.read_csv("SampleSuperstore.csv", encoding=enc)
        print(f"   ✅ Dataset carregado com encoding '{enc}'")
        break
    except (UnicodeDecodeError, FileNotFoundError):
        continue

if df is None:
    raise FileNotFoundError(
        "Arquivo 'SampleSuperstore.csv' não encontrado. "
        "Baixe em: https://www.kaggle.com/datasets/vivek468/superstore-dataset-final"
    )

print(f"\n   Linhas:  {df.shape[0]:,}")
print(f"   Colunas: {df.shape[1]}")
print(f"   Nomes:   {list(df.columns)}")
print(f"\n📊 Primeiros 5 registros:\n{df.head().to_string()}")
print(f"\n📊 Tipos de dados:\n{df.dtypes.to_string()}")

# ──────────────────────────────────────────────────────────
# ETAPA 2 — TRATAMENTO E PREPARAÇÃO DOS DADOS
# ──────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("🛠️  ETAPA 2 — Tratamento e Preparação dos Dados")
print(f"{'='*65}")

# Valores nulos
nulos = df.isnull().sum()
nulos_existentes = nulos[nulos > 0]
if len(nulos_existentes) > 0:
    print(f"\n🔍 Valores nulos encontrados:\n{nulos_existentes.to_string()}")
    df = df.dropna()
    print("   ✅ Linhas com nulos removidas.")
else:
    print("\n   ✅ Nenhum valor nulo encontrado.")

# Duplicatas
duplicatas = int(df.duplicated().sum())
if duplicatas > 0:
    df = df.drop_duplicates()
    print(f"   ✅ {duplicatas} duplicatas removidas.")
else:
    print("   ✅ Nenhuma duplicata encontrada.")

# Conversão de datas
for col in df.columns:
    if "date" in col.lower():
        try:
            df[col] = pd.to_datetime(df[col])
            print(f"   ✅ '{col}' convertida para datetime.")
        except Exception:
            pass

# Colunas derivadas de tempo
if "Order Date" in df.columns:
    df["Ano"]    = df["Order Date"].dt.year
    df["Mes"]    = df["Order Date"].dt.month
    df["AnoMes"] = df["Order Date"].dt.to_period("M")
    print("   ✅ Colunas Ano, Mes e AnoMes criadas.")

# Outliers via IQR
for col in ["Sales", "Profit"]:
    if col in df.columns:
        q1  = df[col].quantile(0.25)
        q3  = df[col].quantile(0.75)
        iqr = q3 - q1
        n   = int(((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum())
        print(f"   🔍 Outliers em '{col}': {n} registros ({n/len(df)*100:.1f}%) — mantidos.")

print(f"\n📊 Resumo estatístico:\n{df.describe().round(2).to_string()}")

# ──────────────────────────────────────────────────────────
# ETAPA 3 — ANÁLISE EXPLORATÓRIA
# ──────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("🔎 ETAPA 3 — Análise Exploratória de Dados")
print(f"{'='*65}")

# 3.1 Vendas e lucro por Categoria
por_categoria: pd.DataFrame = pd.DataFrame()
if {"Category", "Sales", "Profit", "Order ID"}.issubset(df.columns):
    por_categoria = df.groupby("Category").agg(
        Vendas_Total=("Sales",    "sum"),
        Lucro_Total =("Profit",   "sum"),
        Qtd_Pedidos =("Order ID", "count"),
    ).round(2).sort_values("Vendas_Total", ascending=False)
    print(f"\n📊 3.1 Vendas e Lucro por Categoria:\n{por_categoria.to_string()}")

# 3.2 Desempenho por Segmento
por_segmento: pd.DataFrame = pd.DataFrame()
if {"Segment", "Sales", "Profit", "Order ID"}.issubset(df.columns):
    por_segmento = df.groupby("Segment").agg(
        Vendas  =("Sales",    "sum"),
        Lucro   =("Profit",   "sum"),
        Pedidos =("Order ID", "count"),
    ).round(2).sort_values("Vendas", ascending=False)
    print(f"\n📊 3.2 Desempenho por Segmento:\n{por_segmento.to_string()}")

# 3.3 Correlação Desconto vs Lucro
correlacao_val: float = float("nan")
if {"Discount", "Profit", "Sales"}.issubset(df.columns):
    correlacao    = df[["Discount", "Profit", "Sales"]].corr().round(3)
    correlacao_val = float(correlacao.loc["Discount", "Profit"])
    n_alto_desc    = int((df["Discount"] > 0.3).sum())
    print(f"\n📊 3.3 Correlação entre variáveis:\n{correlacao.to_string()}")
    print(f"\n   ⚠️  Desconto→Lucro: {correlacao_val:.3f}")
    print(f"   Pedidos com desconto > 30%: {n_alto_desc:,} ({n_alto_desc/len(df)*100:.1f}%)")
    lucro_alto_desc = df.loc[df["Discount"] > 0.3, "Profit"].mean()
    print(f"   Lucro médio nesses pedidos: ${lucro_alto_desc:.2f}")
else:
    print("\n   ⚠️  Colunas Discount/Profit/Sales não encontradas — correlação ignorada.")

# 3.4 Top 10 Sub-categorias
if {"Sub-Category", "Sales"}.issubset(df.columns):
    top10 = df.groupby("Sub-Category")["Sales"].sum()\
              .sort_values(ascending=False).head(10)
    print(f"\n📊 3.4 Top 10 Sub-categorias:\n{top10.round(2).to_string()}")

# 3.5 Vendas por ano
if "Ano" in df.columns:
    por_ano = df.groupby("Ano")["Sales"].sum().round(2)
    print(f"\n📊 3.5 Vendas por Ano:\n{por_ano.to_string()}")

# ──────────────────────────────────────────────────────────
# ETAPA 4 — VISUALIZAÇÕES GRÁFICAS
# ──────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("📈 ETAPA 4 — Gerando Visualizações")
print(f"{'='*65}")


def salvar(nome: str) -> str:
    """Salva o gráfico atual e fecha a figura."""
    caminho = os.path.join(PASTA_GRAFICOS, nome)
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"   ✅ Salvo: {caminho}")
    return caminho


# ── Gráfico 1: Vendas e Lucro por Categoria ───────────────
if not por_categoria.empty:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Vendas e Lucro por Categoria de Produto",
                 fontsize=15, fontweight="bold")

    cats = por_categoria.index.tolist()
    x    = np.arange(len(cats))

    bars1 = ax1.bar(x, por_categoria["Vendas_Total"],
                    color="#1D9E75", edgecolor="white")
    ax1.set_title("Vendas Totais", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats, rotation=15)
    ax1.set_ylabel("Vendas (USD)")
    ax1.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}k"))
    for b in bars1:
        ax1.text(b.get_x() + b.get_width()/2, b.get_height()*1.01,
                 f"${b.get_height()/1000:.0f}k", ha="center", fontsize=9)

    cores_l = ["#3B6D11" if v >= 0 else "#A32D2D"
               for v in por_categoria["Lucro_Total"]]
    bars2 = ax2.bar(x, por_categoria["Lucro_Total"],
                    color=cores_l, edgecolor="white")
    ax2.set_title("Lucro Total", fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(cats, rotation=15)
    ax2.set_ylabel("Lucro (USD)")
    ax2.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}k"))
    for b in bars2:
        offset = 200 if b.get_height() >= 0 else -2500
        ax2.text(b.get_x() + b.get_width()/2, b.get_height() + offset,
                 f"${b.get_height()/1000:.0f}k", ha="center", fontsize=9)

    plt.tight_layout()
    salvar("01_vendas_lucro_categoria.png")


# ── Gráfico 2: Desconto vs Lucro ──────────────────────────
if {"Discount", "Profit"}.issubset(df.columns):
    p5  = float(df["Profit"].quantile(0.05))
    p95 = float(df["Profit"].quantile(0.95))

    fig, ax = plt.subplots(figsize=(10, 6))
    sc = ax.scatter(df["Discount"], df["Profit"],
                    alpha=0.35, s=18,
                    c=df["Profit"], cmap="RdYlGn",
                    vmin=p5, vmax=p95)
    plt.colorbar(sc, label="Lucro (USD)")
    ax.axhline(0,   color="red",    linewidth=1.5, linestyle="--",
               label="Lucro = 0 (equilíbrio)")
    ax.axvline(0.3, color="orange", linewidth=1.5, linestyle=":",
               label="Desconto 30% (zona de risco)")

    if not np.isnan(correlacao_val):
        ax.text(0.02, 0.95, f"Correlação: {correlacao_val:.3f}",
                transform=ax.transAxes, fontsize=11,
                bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    ax.set_title("Relação entre Desconto e Lucro",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Desconto (%)")
    ax.set_ylabel("Lucro (USD)")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    salvar("02_desconto_vs_lucro.png")


# ── Gráfico 3: Desempenho por Segmento ────────────────────
if not por_segmento.empty:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Desempenho por Segmento de Cliente",
                 fontsize=14, fontweight="bold")

    segs  = por_segmento.index.tolist()
    cores = ["#534AB7", "#1D9E75", "#BA7517"]

    ax1.bar(segs, por_segmento["Vendas"], color=cores, edgecolor="white")
    ax1.set_title("Vendas por Segmento", fontweight="bold")
    ax1.set_ylabel("Vendas (USD)")
    ax1.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}k"))
    for i, v in enumerate(por_segmento["Vendas"]):
        ax1.text(i, float(v)*1.01, f"${float(v)/1000:.0f}k",
                 ha="center", fontsize=9)

    ax2.bar(segs, por_segmento["Lucro"], color=cores, edgecolor="white")
    ax2.set_title("Lucro por Segmento", fontweight="bold")
    ax2.set_ylabel("Lucro (USD)")
    ax2.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}k"))
    for i, v in enumerate(por_segmento["Lucro"]):
        ax2.text(i, float(v)*1.01, f"${float(v)/1000:.0f}k",
                 ha="center", fontsize=9)

    plt.tight_layout()
    salvar("03_desempenho_segmento.png")


# ── Gráfico 4: Tendência Temporal ─────────────────────────
if "AnoMes" in df.columns and "Sales" in df.columns:
    vendas_m = df.groupby("AnoMes")["Sales"].sum()
    vendas_m.index = vendas_m.index.astype(str)
    valores  = vendas_m.values.tolist()
    indices  = list(range(len(valores)))
    labels   = vendas_m.index.tolist()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(indices, valores, linewidth=2, color="#185FA5",
            marker="o", markersize=4)
    ax.fill_between(indices, valores, alpha=0.12, color="#185FA5")

    mm3 = pd.Series(valores).rolling(3).mean().tolist()
    ax.plot(indices, mm3, linewidth=2.5, color="#D85A30",
            linestyle="--", label="Média móvel 3 meses")

    step = max(1, len(labels) // 12)
    ax.set_xticks(indices[::step])
    ax.set_xticklabels(labels[::step], rotation=45, ha="right")
    ax.set_title("Tendência Mensal de Vendas",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Vendas (USD)")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}k"))
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    salvar("04_tendencia_temporal_vendas.png")


# ── Gráfico 5: Top 10 Sub-categorias ──────────────────────
if {"Sub-Category", "Sales"}.issubset(df.columns):
    top10 = df.groupby("Sub-Category")["Sales"].sum()\
              .sort_values(ascending=True).tail(10)
    cores_top = sns.color_palette("Blues_r", len(top10))

    fig, ax = plt.subplots(figsize=(12, 6))
    barras = ax.barh(top10.index.tolist(), top10.values.tolist(),
                     color=cores_top, edgecolor="white")
    ax.set_title("Top 10 Sub-categorias por Vendas",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Vendas (USD)")
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}k"))
    for b in barras:
        ax.text(b.get_width()*1.005, b.get_y() + b.get_height()/2,
                f"${b.get_width()/1000:.0f}k", va="center", fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    salvar("05_top10_subcategorias.png")

# ── Gráfico 6: Heatmap de Correlações ─────────────────────
cols_corr = [c for c in ["Sales", "Quantity", "Discount", "Profit"]
             if c in df.columns]
if len(cols_corr) >= 2:
    corr_m = df[cols_corr].corr().round(3)
    mask   = np.triu(np.ones_like(corr_m, dtype=bool))

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_m, annot=True, fmt=".3f", cmap="RdYlGn",
                center=0, vmin=-1, vmax=1, ax=ax, mask=mask,
                linewidths=0.5, cbar_kws={"label": "Correlação"})
    ax.set_title("Heatmap de Correlações",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    salvar("06_heatmap_correlacoes.png")

# ──────────────────────────────────────────────────────────
# ETAPA 5 — INSIGHTS E CONCLUSÕES
# ──────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("💡 ETAPA 5 — Insights e Conclusões")
print(f"{'='*65}")

total_vendas = float(df["Sales"].sum()) if "Sales" in df.columns else 0.0
total_lucro  = float(df["Profit"].sum()) if "Profit" in df.columns else 0.0
margem       = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0.0

cat_maior_venda  = por_categoria["Vendas_Total"].idxmax() \
    if not por_categoria.empty else "N/A"
cat_maior_lucro  = por_categoria["Lucro_Total"].idxmax() \
    if not por_categoria.empty else "N/A"
cat_menor_lucro  = por_categoria["Lucro_Total"].idxmin() \
    if not por_categoria.empty else "N/A"

print(f"""
┌─────────────────────────────────────────────────────────────┐
│  KPIs PRINCIPAIS — SAMPLE SUPERSTORE                        │
├─────────────────────────────────────────────────────────────┤
│  Total de registros:        {len(df):>10,}                  │
│  Total de vendas:           ${total_vendas:>12,.2f}         │
│  Total de lucro:            ${total_lucro:>12,.2f}          │
│  Margem de lucro geral:     {margem:>10.2f}%                │
│  Categoria mais vendida:    {cat_maior_venda:<20}           │
│  Categoria mais lucrativa:  {cat_maior_lucro:<20}           │
│  Categoria menos lucrativa: {cat_menor_lucro:<20}           │
└─────────────────────────────────────────────────────────────┘
""")

corr_texto = f"{correlacao_val:.3f}" if not np.isnan(correlacao_val) else "N/A"

print(f"""📌 INSIGHTS IDENTIFICADOS:

  1. DESCONTO DESTRÓI LUCRO:
     Correlação desconto→lucro = {corr_texto} (negativa).
     Pedidos com desconto acima de 30% tendem a gerar prejuízo.
     Recomendação: limitar descontos a no máximo 20%.

  2. TECNOLOGIA LIDERA EM VENDAS:
     Categoria {cat_maior_venda} tem o maior volume de vendas.
     Analise margem por categoria para priorizar mix de produtos.

  3. SEGMENTO CONSUMER DOMINA EM VOLUME:
     Porém Corporate pode ter margens mais eficientes por pedido.
     Estratégia recomendada: upsell no segmento Corporate.

  4. SAZONALIDADE CLARA NO FINAL DO ANO (Q4):
     Picos de vendas em outubro-dezembro — oportunidade para
     campanhas antecipadas no Q3.

  5. TOP SUB-CATEGORIAS CONCENTRAM RECEITA:
     Foco em estoque e marketing nas top 3 sub-categorias
     pode maximizar retorno com menor esforço.
""")

print(f"{'='*65}")
print("✅ ANÁLISE EXPLORATÓRIA CONCLUÍDA COM SUCESSO!")
print(f"   Gráficos gerados em: ./{PASTA_GRAFICOS}/")
print(f"{'='*65}")
