"""
Dashboard Técnico-Comercial - Memória de Massa
Módulo Financeiro Completo | Streamlit App
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Dashboard Memória de Massa - MELI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS PERSONALIZADO (UI/UX PREMIUM)
# ============================================================
st.markdown("""
<style>
    /* Reset e Base */
    .main {background: linear-gradient(135deg, #0a0e27 0%, #1a1f4b 50%, #0d1235 100%); color: #e0e0e0;}
    .stApp {background: transparent;}

    /* Tipografia */
    h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 700; color: #ffffff;}
    h1 {font-size: 2.2rem; text-shadow: 0 0 20px rgba(0,212,255,0.3);}

    /* Cards */
    .metric-card {
        background: linear-gradient(145deg, rgba(16,20,50,0.9), rgba(30,35,80,0.8));
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(0,212,255,0.5);
        box-shadow: 0 12px 40px rgba(0,212,255,0.15);
        transform: translateY(-2px);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {font-size: 0.85rem; color: #8892b0; text-transform: uppercase; letter-spacing: 1px;}

    /* KPI Cards Específicos */
    .kpi-positive {border-left: 4px solid #00ff88;}
    .kpi-negative {border-left: 4px solid #ff4757;}
    .kpi-neutral {border-left: 4px solid #ffa502;}

    /* Tabelas */
    .stDataFrame {border-radius: 12px; overflow: hidden;}
    .stDataFrame td {color: #e0e0e0 !important;}
    .stDataFrame th {background: rgba(0,212,255,0.15) !important; color: #00d4ff !important;}

    /* Inputs */
    .stNumberInput, .stSlider {background: rgba(16,20,50,0.6) !important; border-radius: 10px !important;}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {
        background: rgba(16,20,50,0.6);
        border-radius: 10px 10px 0 0;
        color: #8892b0;
        border: none;
        padding: 12px 24px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, rgba(0,212,255,0.2), rgba(123,44,191,0.2)) !important;
        color: #ffffff !important;
        border-bottom: 2px solid #00d4ff;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(16,20,50,0.6);
        border-radius: 10px;
        border: 1px solid rgba(0,212,255,0.2);
    }

    /* Sidebar */
    .css-1d391kg {background: linear-gradient(180deg, #0a0e27, #1a1f4b);}

    /* Animações */
    @keyframes pulse-glow {
        0%, 100% {box-shadow: 0 0 5px rgba(0,212,255,0.2);}
        50% {box-shadow: 0 0 20px rgba(0,212,255,0.4);}
    }
    .highlight-box {
        background: linear-gradient(145deg, rgba(0,212,255,0.1), rgba(123,44,191,0.1));
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 12px;
        padding: 15px;
        animation: pulse-glow 3s infinite;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {width: 8px;}
    ::-webkit-scrollbar-track {background: #0a0e27;}
    ::-webkit-scrollbar-thumb {background: #00d4ff; border-radius: 4px;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def format_currency(value):
    """Formata valor em R$"""
    if pd.isna(value) or value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def format_percent(value):
    """Formata percentual"""
    if pd.isna(value) or value is None:
        return "0,00%"
    return f"{value:.2f}%".replace(".", ",")

def format_number(value, decimals=0):
    """Formata número com separadores"""
    if pd.isna(value) or value is None:
        return "0"
    return f"{value:,.{decimals}f}".replace(",", "v").replace(".", ",").replace("v", ".")

def create_metric_card(title, value, subtitle="", status="neutral", icon="📊"):
    """Cria card de métrica com estilo"""
    status_class = f"kpi-{status}"
    st.markdown(f"""
    <div class="metric-card {status_class}">
        <div class="metric-label">{icon} {title}</div>
        <div class="metric-value">{value}</div>
        <div style="font-size: 0.8rem; color: #8892b0; margin-top: 5px;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FUNÇÕES FINANCEIRAS (REGRAS DE NEGÓCIO)
# ============================================================

def calcular_financeiro_ape(
    consumo_mensal_mwh,
    consumo_fp_mwh,
    consumo_p_mwh,
    demanda_kw,
    tarifa_energia,
    tarifa_tusd,
    tarifa_demanda,
    desconto_energia,
    desconto_tusd,
    desconto_demanda,
    fator_perdas=1.035,
    pis_cofins=0.0925,
    icms=0.18,
    bandeira=0.02,
    tx_iluminacao=0.015,
    encargo_relat=0.03
):
    """
    Calcula financeiro para APE (Autoprodução de Energia)
    """
    # Energia consumida (com perdas)
    energia_total = consumo_mensal_mwh * fator_perdas
    energia_fp = consumo_fp_mwh * fator_perdas
    energia_p = consumo_p_mwh * fator_perdas

    # Tarifas com desconto
    tarifa_energia_desc = tarifa_energia * (1 - desconto_energia)
    tarifa_tusd_desc = tarifa_tusd * (1 - desconto_tusd)
    tarifa_demanda_desc = tarifa_demanda * (1 - desconto_demanda)

    # Valores sem desconto (cenário atual)
    valor_energia_sem_desc = energia_total * tarifa_energia
    valor_tusd_sem_desc = energia_total * tarifa_tusd
    valor_demanda_sem_desc = demanda_kw * tarifa_demanda
    subtotal_sem_desc = valor_energia_sem_desc + valor_tusd_sem_desc + valor_demanda_sem_desc

    # Valores com desconto
    valor_energia_com_desc = energia_total * tarifa_energia_desc
    valor_tusd_com_desc = energia_total * tarifa_tusd_desc
    valor_demanda_com_desc = demanda_kw * tarifa_demanda_desc
    subtotal_com_desc = valor_energia_com_desc + valor_tusd_com_desc + valor_demanda_com_desc

    # Economia bruta
    economia_bruta = subtotal_sem_desc - subtotal_com_desc

    # Impostos e encargos sobre a economia
    impostos = economia_bruta * (pis_cofins + icms)
    encargos = economia_bruta * (bandeira + tx_iluminacao + encargo_relat)

    # Economia líquida
    economia_liquida = economia_bruta - impostos - encargos

    # Fatura total estimada (com desconto)
    fatura_total = subtotal_com_desc + (subtotal_com_desc * (pis_cofins + icms + bandeira + tx_iluminacao + encargo_relat))

    return {
        "energia_total_mwh": energia_total,
        "energia_fp_mwh": energia_fp,
        "energia_p_mwh": energia_p,
        "tarifa_energia_desc": tarifa_energia_desc,
        "tarifa_tusd_desc": tarifa_tusd_desc,
        "tarifa_demanda_desc": tarifa_demanda_desc,
        "valor_energia_sem_desc": valor_energia_sem_desc,
        "valor_tusd_sem_desc": valor_tusd_sem_desc,
        "valor_demanda_sem_desc": valor_demanda_sem_desc,
        "subtotal_sem_desc": subtotal_sem_desc,
        "valor_energia_com_desc": valor_energia_com_desc,
        "valor_tusd_com_desc": valor_tusd_com_desc,
        "valor_demanda_com_desc": valor_demanda_com_desc,
        "subtotal_com_desc": subtotal_com_desc,
        "economia_bruta": economia_bruta,
        "impostos": impostos,
        "encargos": encargos,
        "economia_liquida": economia_liquida,
        "fatura_total": fatura_total,
        "pct_economia": (economia_liquida / subtotal_sem_desc * 100) if subtotal_sem_desc > 0 else 0
    }


def calcular_financeiro_g0(
    consumo_mensal_mwh,
    consumo_fp_mwh,
    consumo_p_mwh,
    demanda_kw,
    tarifa_energia,
    tarifa_tusd,
    tarifa_demanda,
    desconto_energia,
    desconto_tusd,
    desconto_demanda,
    fator_perdas=1.035,
    pis_cofins=0.0925,
    icms=0.18,
    bandeira=0.02,
    tx_iluminacao=0.015,
    encargo_relat=0.03
):
    """
    Calcula financeiro para G0 (Geração Local)
    """
    # G0: geração local reduz consumo da rede
    # Aplica descontos nas tarifas de energia e TUSD

    energia_total = consumo_mensal_mwh * fator_perdas
    energia_fp = consumo_fp_mwh * fator_perdas
    energia_p = consumo_p_mwh * fator_perdas

    # Tarifas com desconto
    tarifa_energia_desc = tarifa_energia * (1 - desconto_energia)
    tarifa_tusd_desc = tarifa_tusd * (1 - desconto_tusd)
    tarifa_demanda_desc = tarifa_demanda * (1 - desconto_demanda)

    # Valores sem desconto
    valor_energia_sem_desc = energia_total * tarifa_energia
    valor_tusd_sem_desc = energia_total * tarifa_tusd
    valor_demanda_sem_desc = demanda_kw * tarifa_demanda
    subtotal_sem_desc = valor_energia_sem_desc + valor_tusd_sem_desc + valor_demanda_sem_desc

    # Valores com desconto
    valor_energia_com_desc = energia_total * tarifa_energia_desc
    valor_tusd_com_desc = energia_total * tarifa_tusd_desc
    valor_demanda_com_desc = demanda_kw * tarifa_demanda_desc
    subtotal_com_desc = valor_energia_com_desc + valor_tusd_com_desc + valor_demanda_com_desc

    # Economia bruta
    economia_bruta = subtotal_sem_desc - subtotal_com_desc

    # Impostos e encargos
    impostos = economia_bruta * (pis_cofins + icms)
    encargos = economia_bruta * (bandeira + tx_iluminacao + encargo_relat)

    # Economia líquida
    economia_liquida = economia_bruta - impostos - encargos

    # Fatura total estimada
    fatura_total = subtotal_com_desc + (subtotal_com_desc * (pis_cofins + icms + bandeira + tx_iluminacao + encargo_relat))

    return {
        "energia_total_mwh": energia_total,
        "energia_fp_mwh": energia_fp,
        "energia_p_mwh": energia_p,
        "tarifa_energia_desc": tarifa_energia_desc,
        "tarifa_tusd_desc": tarifa_tusd_desc,
        "tarifa_demanda_desc": tarifa_demanda_desc,
        "valor_energia_sem_desc": valor_energia_sem_desc,
        "valor_tusd_sem_desc": valor_tusd_sem_desc,
        "valor_demanda_sem_desc": valor_demanda_sem_desc,
        "subtotal_sem_desc": subtotal_sem_desc,
        "valor_energia_com_desc": valor_energia_com_desc,
        "valor_tusd_com_desc": valor_tusd_com_desc,
        "valor_demanda_com_desc": valor_demanda_com_desc,
        "subtotal_com_desc": subtotal_com_desc,
        "economia_bruta": economia_bruta,
        "impostos": impostos,
        "encargos": encargos,
        "economia_liquida": economia_liquida,
        "fatura_total": fatura_total,
        "pct_economia": (economia_liquida / subtotal_sem_desc * 100) if subtotal_sem_desc > 0 else 0
    }


def calcular_payback(investimento, economia_anual, taxa_desconto=0.10):
    """
    Calcula payback simples e descontado
    """
    if economia_anual <= 0:
        return {"payback_simples": float('inf'), "payback_descontado": float('inf'), "vpl": -investimento, "tir": 0}

    # Payback simples
    payback_simples = investimento / economia_anual

    # Payback descontado (até 20 anos)
    fluxos = [-investimento]
    for ano in range(1, 21):
        # Economia decresce 0.5% ao ano (degradação)
        economia_ano = economia_anual * (0.995 ** (ano - 1))
        fluxos.append(economia_ano)

    # VPL
    vpl = sum(f / ((1 + taxa_desconto) ** i) for i, f in enumerate(fluxos))

    # Payback descontado
    acumulado = -investimento
    payback_desc = None
    for ano in range(1, 21):
        acumulado += fluxos[ano] / ((1 + taxa_desconto) ** ano)
        if acumulado >= 0 and payback_desc is None:
            payback_desc = ano - 1 + (abs(acumulado - fluxos[ano] / ((1 + taxa_desconto) ** ano)) / (fluxos[ano] / ((1 + taxa_desconto) ** ano)))

    if payback_desc is None:
        payback_desc = float('inf')

    # TIR (aproximação)
    tir = 0
    for r in np.arange(0.01, 0.50, 0.001):
        vpl_r = sum(f / ((1 + r) ** i) for i, f in enumerate(fluxos))
        if abs(vpl_r) < 1000:
            tir = r
            break

    return {
        "payback_simples": payback_simples,
        "payback_descontado": payback_desc,
        "vpl": vpl,
        "tir": tir * 100,
        "fluxos": fluxos
    }


def calcular_tabela_mensal(consumo_mensal, tarifa_energia, tarifa_tusd, tarifa_demanda,
                           desconto_energia, desconto_tusd, desconto_demanda,
                           demanda_kw, fator_perdas=1.035):
    """
    Gera tabela mensal detalhada para 12 meses
    """
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    # Variação sazonal (fator multiplicador por mês)
    sazonalidade = [1.02, 0.98, 1.00, 0.97, 0.95, 0.96, 0.98, 1.00, 1.03, 1.05, 1.04, 1.02]

    dados = []
    for i, mes in enumerate(meses):
        consumo_mes = consumo_mensal * sazonalidade[i]
        energia_total = consumo_mes * fator_perdas

        # Sem desconto
        v_energia_sd = energia_total * tarifa_energia
        v_tusd_sd = energia_total * tarifa_tusd
        v_demanda_sd = demanda_kw * tarifa_demanda
        total_sd = v_energia_sd + v_tusd_sd + v_demanda_sd

        # Com desconto
        v_energia_cd = energia_total * tarifa_energia * (1 - desconto_energia)
        v_tusd_cd = energia_total * tarifa_tusd * (1 - desconto_tusd)
        v_demanda_cd = demanda_kw * tarifa_demanda * (1 - desconto_demanda)
        total_cd = v_energia_cd + v_tusd_cd + v_demanda_cd

        economia = total_sd - total_cd

        dados.append({
            "Mês": mes,
            "Consumo (MWh)": round(consumo_mes, 2),
            "Energia c/ Perdas (MWh)": round(energia_total, 2),
            "Fatura Atual (R$)": round(total_sd, 2),
            "Fatura c/ Desc (R$)": round(total_cd, 2),
            "Economia (R$)": round(economia, 2),
            "Economia (%)": round((economia / total_sd * 100), 2) if total_sd > 0 else 0
        })

    return pd.DataFrame(dados)


# ============================================================
# GRÁFICOS INTERATIVOS (PLOTLY)
# ============================================================

def grafico_comparativo_faturas(resultado_ape, resultado_g0):
    """Gráfico comparativo de faturas APE vs G0"""
    fig = go.Figure()

    categorias = ["Energia", "TUSD", "Demanda", "Total"]

    # APE - Sem desconto
    ape_sd = [
        resultado_ape["valor_energia_sem_desc"],
        resultado_ape["valor_tusd_sem_desc"],
        resultado_ape["valor_demanda_sem_desc"],
        resultado_ape["subtotal_sem_desc"]
    ]
    # APE - Com desconto
    ape_cd = [
        resultado_ape["valor_energia_com_desc"],
        resultado_ape["valor_tusd_com_desc"],
        resultado_ape["valor_demanda_com_desc"],
        resultado_ape["subtotal_com_desc"]
    ]
    # G0 - Sem desconto
    g0_sd = [
        resultado_g0["valor_energia_sem_desc"],
        resultado_g0["valor_tusd_sem_desc"],
        resultado_g0["valor_demanda_sem_desc"],
        resultado_g0["subtotal_sem_desc"]
    ]
    # G0 - Com desconto
    g0_cd = [
        resultado_g0["valor_energia_com_desc"],
        resultado_g0["valor_tusd_com_desc"],
        resultado_g0["valor_demanda_com_desc"],
        resultado_g0["subtotal_com_desc"]
    ]

    fig.add_trace(go.Bar(name="APE - Atual", x=categorias, y=ape_sd, marker_color="#ff4757", opacity=0.8))
    fig.add_trace(go.Bar(name="APE - c/ Desc", x=categorias, y=ape_cd, marker_color="#00d4ff", opacity=0.9))
    fig.add_trace(go.Bar(name="G0 - Atual", x=categorias, y=g0_sd, marker_color="#ff6348", opacity=0.6))
    fig.add_trace(go.Bar(name="G0 - c/ Desc", x=categorias, y=g0_cd, marker_color="#7b2cbf", opacity=0.9))

    fig.update_layout(
        title="Comparativo de Faturas: APE vs G0",
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16,20,50,0.5)",
        font=dict(color="#e0e0e0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Valor (R$)",
        height=500
    )

    return fig


def grafico_economia_anual(economia_ape, economia_g0, investimento_ape, investimento_g0):
    """Gráfico de economia acumulada ao longo dos anos"""
    anos = list(range(0, 16))

    # Economia anual com degradação de 0.5%
    acum_ape = []
    acum_g0 = []
    acum_ape_inv = []
    acum_g0_inv = []

    cum_ape = -investimento_ape
    cum_g0 = -investimento_g0
    cum_ape_inv = -investimento_ape
    cum_g0_inv = -investimento_g0

    for ano in anos:
        acum_ape.append(cum_ape)
        acum_g0.append(cum_g0)
        acum_ape_inv.append(cum_ape_inv)
        acum_g0_inv.append(cum_g0_inv)

        if ano < 15:
            eco_ape_ano = economia_ape * (0.995 ** ano)
            eco_g0_ano = economia_g0 * (0.995 ** ano)
            cum_ape += eco_ape_ano
            cum_g0 += eco_g0_ano
            cum_ape_inv += eco_ape_ano * 0.85  # Considerando 15% de custo O&M
            cum_g0_inv += eco_g0_ano * 0.85

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=anos, y=acum_ape, mode="lines+markers",
        name="APE - Lucro Bruto", line=dict(color="#00d4ff", width=3),
        fill="tonexty" if False else None
    ))
    fig.add_trace(go.Scatter(
        x=anos, y=acum_g0, mode="lines+markers",
        name="G0 - Lucro Bruto", line=dict(color="#7b2cbf", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=anos, y=acum_ape_inv, mode="lines",
        name="APE - Lucro Líquido (c/ O&M)", line=dict(color="#00d4ff", width=2, dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=anos, y=acum_g0_inv, mode="lines",
        name="G0 - Lucro Líquido (c/ O&M)", line=dict(color="#7b2cbf", width=2, dash="dash")
    ))

    # Linha do zero
    fig.add_hline(y=0, line_dash="dot", line_color="white", opacity=0.5)

    fig.update_layout(
        title="Retorno Acumulado ao Longo dos Anos (15 anos)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16,20,50,0.5)",
        font=dict(color="#e0e0e0"),
        xaxis_title="Ano",
        yaxis_title="Valor Acumulado (R$)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )

    return fig


def grafico_composicao_fatura(resultado, titulo):
    """Gráfico de pizza com composição da fatura"""
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]],
                        subplot_titles=["Cenário Atual", "Cenário c/ Desconto"])

    # Atual
    fig.add_trace(go.Pie(
        labels=["Energia", "TUSD", "Demanda"],
        values=[
            resultado["valor_energia_sem_desc"],
            resultado["valor_tusd_sem_desc"],
            resultado["valor_demanda_sem_desc"]
        ],
        hole=0.4,
        marker_colors=["#ff4757", "#ffa502", "#ff6348"],
        textinfo="label+percent",
        name="Atual"
    ), row=1, col=1)

    # Com desconto
    fig.add_trace(go.Pie(
        labels=["Energia", "TUSD", "Demanda"],
        values=[
            resultado["valor_energia_com_desc"],
            resultado["valor_tusd_com_desc"],
            resultado["valor_demanda_com_desc"]
        ],
        hole=0.4,
        marker_colors=["#00d4ff", "#2ed573", "#7b2cbf"],
        textinfo="label+percent",
        name="c/ Desconto"
    ), row=1, col=2)

    fig.update_layout(
        title=f"Composição da Fatura - {titulo}",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        height=450,
        showlegend=False
    )

    return fig


def grafico_sazonalidade(df_mensal):
    """Gráfico de sazonalidade mensal"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=df_mensal["Mês"],
        y=df_mensal["Consumo (MWh)"],
        name="Consumo (MWh)",
        marker_color="rgba(0,212,255,0.6)",
        text=df_mensal["Consumo (MWh)"].round(1),
        textposition="outside"
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df_mensal["Mês"],
        y=df_mensal["Economia (R$)"],
        name="Economia (R$)",
        mode="lines+markers",
        line=dict(color="#00ff88", width=3),
        marker=dict(size=8)
    ), secondary_y=True)

    fig.update_layout(
        title="Sazonalidade de Consumo e Economia Mensal",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16,20,50,0.5)",
        font=dict(color="#e0e0e0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        hovermode="x unified"
    )

    fig.update_yaxes(title_text="Consumo (MWh)", secondary_y=False)
    fig.update_yaxes(title_text="Economia (R$)", secondary_y=True)

    return fig


def grafico_payback(fluxos_ape, fluxos_g0, payback_ape, payback_g0):
    """Gráfico de payback comparativo"""
    anos = list(range(0, len(fluxos_ape)))

    acum_ape = np.cumsum(fluxos_ape)
    acum_g0 = np.cumsum(fluxos_g0)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=anos, y=fluxos_ape,
        name="Fluxo APE", marker_color="rgba(0,212,255,0.7)",
        text=[f"R${v:,.0f}".replace(",", ".") for v in fluxos_ape],
        textposition="outside"
    ))

    fig.add_trace(go.Bar(
        x=anos, y=fluxos_g0,
        name="Fluxo G0", marker_color="rgba(123,44,191,0.7)",
        text=[f"R${v:,.0f}".replace(",", ".") for v in fluxos_g0],
        textposition="outside"
    ))

    fig.add_trace(go.Scatter(
        x=anos, y=acum_ape,
        name="Acumulado APE", mode="lines+markers",
        line=dict(color="#00d4ff", width=3), yaxis="y2"
    ))

    fig.add_trace(go.Scatter(
        x=anos, y=acum_g0,
        name="Acumulado G0", mode="lines+markers",
        line=dict(color="#7b2cbf", width=3), yaxis="y2"
    ))

    fig.update_layout(
        title="Fluxo de Caixa e Payback (20 anos)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16,20,50,0.5)",
        font=dict(color="#e0e0e0"),
        barmode="group",
        xaxis_title="Ano",
        yaxis_title="Fluxo Anual (R$)",
        yaxis2=dict(title="Acumulado (R$)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        hovermode="x unified"
    )

    return fig


# ============================================================
# SIDEBAR - CONFIGURAÇÕES
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #00d4ff; margin: 0;">⚡ MEMÓRIA DE MASSA</h2>
        <p style="color: #8892b0; font-size: 0.8rem;">Dashboard Técnico-Comercial</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Seleção do cenário
    st.subheader("📋 Cenário de Análise")

    # Usar valores da planilha como defaults
    col1, col2 = st.columns(2)
    with col1:
        consumo_mensal = st.number_input(
            "Consumo Mensal (MWh)",
            value=3500.0,
            min_value=100.0,
            max_value=20000.0,
            step=100.0,
            help="Consumo médio mensal em MWh"
        )
    with col2:
        demanda_kw = st.number_input(
            "Demanda (kW)",
            value=8500.0,
            min_value=100.0,
            max_value=50000.0,
            step=100.0,
            help="Demanda contratada em kW"
        )

    col1, col2 = st.columns(2)
    with col1:
        consumo_fp = st.number_input(
            "Consumo FP (MWh)",
            value=2100.0,
            min_value=0.0,
            max_value=15000.0,
            step=50.0,
            help="Consumo Fora de Ponta"
        )
    with col2:
        consumo_p = st.number_input(
            "Consumo Ponta (MWh)",
            value=1400.0,
            min_value=0.0,
            max_value=10000.0,
            step=50.0,
            help="Consumo em Horário de Ponta"
        )

    st.markdown("---")
    st.subheader("💰 Tarifas (R$/MWh)")

    col1, col2, col3 = st.columns(3)
    with col1:
        tarifa_energia = st.number_input("Energia", value=280.0, step=10.0)
    with col2:
        tarifa_tusd = st.number_input("TUSD", value=120.0, step=10.0)
    with col3:
        tarifa_demanda = st.number_input("Demanda", value=35.0, step=5.0)

    st.markdown("---")
    st.subheader("🎯 Descontos APE (%)")

    col1, col2, col3 = st.columns(3)
    with col1:
        desc_energia_ape = st.slider("Energia", 0.0, 50.0, 15.0, 1.0) / 100
    with col2:
        desc_tusd_ape = st.slider("TUSD", 0.0, 50.0, 10.0, 1.0) / 100
    with col3:
        desc_demanda_ape = st.slider("Demanda", 0.0, 50.0, 5.0, 1.0) / 100

    st.subheader("🎯 Descontos G0 (%)")

    col1, col2, col3 = st.columns(3)
    with col1:
        desc_energia_g0 = st.slider("Energia ", 0.0, 50.0, 20.0, 1.0, key="g0_en") / 100
    with col2:
        desc_tusd_g0 = st.slider("TUSD ", 0.0, 50.0, 15.0, 1.0, key="g0_tu") / 100
    with col3:
        desc_demanda_g0 = st.slider("Demanda ", 0.0, 50.0, 8.0, 1.0, key="g0_de") / 100

    st.markdown("---")
    st.subheader("🏗️ Investimentos (R$)")

    col1, col2 = st.columns(2)
    with col1:
        investimento_ape = st.number_input(
            "Investimento APE",
            value=2500000.0,
            step=100000.0,
            format="%.0f"
        )
    with col2:
        investimento_g0 = st.number_input(
            "Investimento G0",
            value=1800000.0,
            step=100000.0,
            format="%.0f"
        )

    st.markdown("---")
    st.subheader("⚙️ Parâmetros Avançados")

    with st.expander("Taxas e Impostos"):
        fator_perdas = st.number_input("Fator Perdas", value=1.035, step=0.001, format="%.3f")
        pis_cofins = st.number_input("PIS/COFINS (%)", value=9.25, step=0.5) / 100
        icms = st.number_input("ICMS (%)", value=18.0, step=1.0) / 100
        bandeira = st.number_input("Bandeira (%)", value=2.0, step=0.5) / 100
        tx_iluminacao = st.number_input("Taxa Iluminação (%)", value=1.5, step=0.5) / 100
        encargo_relat = st.number_input("Encargo Relat. (%)", value=3.0, step=0.5) / 100
        taxa_desconto = st.number_input("Taxa Desconto (%)", value=10.0, step=0.5) / 100

# ============================================================
# CÁLCULOS PRINCIPAIS
# ============================================================
resultado_ape = calcular_financeiro_ape(
    consumo_mensal, consumo_fp, consumo_p, demanda_kw,
    tarifa_energia, tarifa_tusd, tarifa_demanda,
    desc_energia_ape, desc_tusd_ape, desc_demanda_ape,
    fator_perdas, pis_cofins, icms, bandeira, tx_iluminacao, encargo_relat
)

resultado_g0 = calcular_financeiro_g0(
    consumo_mensal, consumo_fp, consumo_p, demanda_kw,
    tarifa_energia, tarifa_tusd, tarifa_demanda,
    desc_energia_g0, desc_tusd_g0, desc_demanda_g0,
    fator_perdas, pis_cofins, icms, bandeira, tx_iluminacao, encargo_relat
)

# Payback
economia_anual_ape = resultado_ape["economia_liquida"] * 12
economia_anual_g0 = resultado_g0["economia_liquida"] * 12

payback_ape = calcular_payback(investimento_ape, economia_anual_ape, taxa_desconto)
payback_g0 = calcular_payback(investimento_g0, economia_anual_g0, taxa_desconto)

# Tabela mensal
df_mensal_ape = calcular_tabela_mensal(
    consumo_mensal, tarifa_energia, tarifa_tusd, tarifa_demanda,
    desc_energia_ape, desc_tusd_ape, desc_demanda_ape, demanda_kw, fator_perdas
)

df_mensal_g0 = calcular_tabela_mensal(
    consumo_mensal, tarifa_energia, tarifa_tusd, tarifa_demanda,
    desc_energia_g0, desc_tusd_g0, desc_demanda_g0, demanda_kw, fator_perdas
)

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="font-size: 2.5rem; margin-bottom: 5px;">
        <span style="background: linear-gradient(90deg, #00d4ff, #7b2cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ANÁLISE FINANCEIRA
        </span>
    </h1>
    <p style="color: #8892b0; font-size: 1.1rem;">
        Memória de Massa | Mercado Livre de Energia
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# ABAS PRINCIPAIS
# ============================================================
tabs = st.tabs([
    "📊 Resumo Executivo",
    "⚡ Análise APE",
    "🔋 Análise G0",
    "📈 Comparativo",
    "📅 Sazonalidade",
    "💵 Fluxo de Caixa"
])

# ============================================================
# ABA 1: RESUMO EXECUTIVO
# ============================================================
with tabs[0]:
    st.markdown("""
    <div class="highlight-box" style="margin-bottom: 20px;">
        <h3 style="margin: 0; color: #00d4ff;">🎯 Visão Geral da Oportunidade</h3>
        <p style="margin: 5px 0 0 0; color: #ccd6f6;">
            Comparativo entre APE (Autoprodução) e G0 (Geração Local) para redução de custos energéticos
        </p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs Principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        create_metric_card(
            "Economia Anual APE",
            format_currency(economia_anual_ape),
            f"{format_percent(resultado_ape['pct_economia'])} de redução",
            "positive" if economia_anual_ape > 0 else "negative",
            "💰"
        )
    with col2:
        create_metric_card(
            "Economia Anual G0",
            format_currency(economia_anual_g0),
            f"{format_percent(resultado_g0['pct_economia'])} de redução",
            "positive" if economia_anual_g0 > 0 else "negative",
            "🔋"
        )
    with col3:
        melhor = "APE" if payback_ape["payback_simples"] < payback_g0["payback_simples"] else "G0"
        create_metric_card(
            "Melhor Payback",
            f"{min(payback_ape['payback_simples'], payback_g0['payback_simples']):.1f} anos",
            f"Modelo: {melhor}",
            "positive",
            "⏱️"
        )
    with col4:
        vpl_melhor = max(payback_ape["vpl"], payback_g0["vpl"])
        create_metric_card(
            "Maior VPL",
            format_currency(vpl_melhor),
            "15 anos | 10% a.a.",
            "positive",
            "📈"
        )

    st.markdown("---")

    # Comparativo rápido
    st.subheader("📋 Comparativo Rápido")

    comp_data = {
        "Indicador": [
            "Fatura Mensal Atual",
            "Fatura c/ APE",
            "Fatura c/ G0",
            "Economia Mensal APE",
            "Economia Mensal G0",
            "Economia Anual APE",
            "Economia Anual G0",
            "% Redução APE",
            "% Redução G0",
            "Investimento APE",
            "Investimento G0",
            "Payback Simples APE",
            "Payback Simples G0",
            "VPL APE (15a)",
            "VPL G0 (15a)",
            "TIR APE",
            "TIR G0"
        ],
        "APE": [
            format_currency(resultado_ape["subtotal_sem_desc"]),
            format_currency(resultado_ape["subtotal_com_desc"]),
            "-",
            format_currency(resultado_ape["economia_liquida"]),
            "-",
            format_currency(economia_anual_ape),
            "-",
            format_percent(resultado_ape["pct_economia"]),
            "-",
            format_currency(investimento_ape),
            "-",
            f"{payback_ape['payback_simples']:.1f} anos",
            "-",
            format_currency(payback_ape["vpl"]),
            "-",
            f"{payback_ape['tir']:.1f}%",
            "-"
        ],
        "G0": [
            format_currency(resultado_g0["subtotal_sem_desc"]),
            "-",
            format_currency(resultado_g0["subtotal_com_desc"]),
            "-",
            format_currency(resultado_g0["economia_liquida"]),
            "-",
            format_currency(economia_anual_g0),
            "-",
            format_percent(resultado_g0["pct_economia"]),
            "-",
            format_currency(investimento_g0),
            "-",
            f"{payback_g0['payback_simples']:.1f} anos",
            "-",
            format_currency(payback_g0["vpl"]),
            "-",
            f"{payback_g0['tir']:.1f}%"
        ]
    }

    df_comp = pd.DataFrame(comp_data)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # Gráfico comparativo principal
    st.plotly_chart(grafico_comparativo_faturas(resultado_ape, resultado_g0), use_container_width=True)

# ============================================================
# ABA 2: ANÁLISE APE
# ============================================================
with tabs[1]:
    st.markdown("""
    <div class="highlight-box" style="margin-bottom: 20px;">
        <h3 style="margin: 0; color: #00d4ff;">⚡ Autoprodução de Energia (APE)</h3>
        <p style="margin: 5px 0 0 0; color: #ccd6f6;">
            Modelo onde a energia é gerada em usina remota e creditada na fatura via compensação
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        create_metric_card("Fatura Atual", format_currency(resultado_ape["subtotal_sem_desc"]), "Mensal", "negative", "📄")
    with col2:
        create_metric_card("Fatura c/ APE", format_currency(resultado_ape["subtotal_com_desc"]), "Mensal", "positive", "⚡")
    with col3:
        create_metric_card("Economia Líquida", format_currency(resultado_ape["economia_liquida"]), "Mensal", "positive", "💵")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Composição da Fatura")
        st.plotly_chart(grafico_composicao_fatura(resultado_ape, "APE"), use_container_width=True)
    with col2:
        st.subheader("📋 Detalhamento Mensal APE")
        st.dataframe(
            df_mensal_ape.style.format({
                "Consumo (MWh)": "{:.2f}",
                "Energia c/ Perdas (MWh)": "{:.2f}",
                "Fatura Atual (R$)": "R$ {:,.2f}",
                "Fatura c/ Desc (R$)": "R$ {:,.2f}",
                "Economia (R$)": "R$ {:,.2f}",
                "Economia (%)": "{:.2f}%"
            }),
            use_container_width=True,
            height=400
        )

    st.markdown("---")
    st.subheader("🔍 Detalhamento do Cálculo APE")

    det_ape = pd.DataFrame({
        "Item": [
            "Energia Total (c/ perdas)",
            "Energia Fora Ponta",
            "Energia Ponta",
            "Tarifa Energia (c/ desc)",
            "Tarifa TUSD (c/ desc)",
            "Tarifa Demanda (c/ desc)",
            "Valor Energia (sem desc)",
            "Valor TUSD (sem desc)",
            "Valor Demanda (sem desc)",
            "Subtotal Atual",
            "Valor Energia (c/ desc)",
            "Valor TUSD (c/ desc)",
            "Valor Demanda (c/ desc)",
            "Subtotal c/ Desconto",
            "Economia Bruta",
            "Impostos (PIS/COFINS + ICMS)",
            "Encargos (Bandeira + Tx + Enc.)",
            "Economia Líquida",
            "% Economia"
        ],
        "Valor": [
            f"{resultado_ape['energia_total_mwh']:.2f} MWh",
            f"{resultado_ape['energia_fp_mwh']:.2f} MWh",
            f"{resultado_ape['energia_p_mwh']:.2f} MWh",
            format_currency(resultado_ape["tarifa_energia_desc"]),
            format_currency(resultado_ape["tarifa_tusd_desc"]),
            format_currency(resultado_ape["tarifa_demanda_desc"]),
            format_currency(resultado_ape["valor_energia_sem_desc"]),
            format_currency(resultado_ape["valor_tusd_sem_desc"]),
            format_currency(resultado_ape["valor_demanda_sem_desc"]),
            format_currency(resultado_ape["subtotal_sem_desc"]),
            format_currency(resultado_ape["valor_energia_com_desc"]),
            format_currency(resultado_ape["valor_tusd_com_desc"]),
            format_currency(resultado_ape["valor_demanda_com_desc"]),
            format_currency(resultado_ape["subtotal_com_desc"]),
            format_currency(resultado_ape["economia_bruta"]),
            format_currency(resultado_ape["impostos"]),
            format_currency(resultado_ape["encargos"]),
            format_currency(resultado_ape["economia_liquida"]),
            format_percent(resultado_ape["pct_economia"])
        ]
    })
    st.dataframe(det_ape, use_container_width=True, hide_index=True)

# ============================================================
# ABA 3: ANÁLISE G0
# ============================================================
with tabs[2]:
    st.markdown("""
    <div class="highlight-box" style="margin-bottom: 20px;">
        <h3 style="margin: 0; color: #7b2cbf;">🔋 Geração Local (G0)</h3>
        <p style="margin: 5px 0 0 0; color: #ccd6f6;">
            Modelo com geração fotovoltaica no local do consumo, reduzindo consumo da rede
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        create_metric_card("Fatura Atual", format_currency(resultado_g0["subtotal_sem_desc"]), "Mensal", "negative", "📄")
    with col2:
        create_metric_card("Fatura c/ G0", format_currency(resultado_g0["subtotal_com_desc"]), "Mensal", "positive", "🔋")
    with col3:
        create_metric_card("Economia Líquida", format_currency(resultado_g0["economia_liquida"]), "Mensal", "positive", "💵")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Composição da Fatura")
        st.plotly_chart(grafico_composicao_fatura(resultado_g0, "G0"), use_container_width=True)
    with col2:
        st.subheader("📋 Detalhamento Mensal G0")
        st.dataframe(
            df_mensal_g0.style.format({
                "Consumo (MWh)": "{:.2f}",
                "Energia c/ Perdas (MWh)": "{:.2f}",
                "Fatura Atual (R$)": "R$ {:,.2f}",
                "Fatura c/ Desc (R$)": "R$ {:,.2f}",
                "Economia (R$)": "R$ {:,.2f}",
                "Economia (%)": "{:.2f}%"
            }),
            use_container_width=True,
            height=400
        )

    st.markdown("---")
    st.subheader("🔍 Detalhamento do Cálculo G0")

    det_g0 = pd.DataFrame({
        "Item": [
            "Energia Total (c/ perdas)",
            "Energia Fora Ponta",
            "Energia Ponta",
            "Tarifa Energia (c/ desc)",
            "Tarifa TUSD (c/ desc)",
            "Tarifa Demanda (c/ desc)",
            "Valor Energia (sem desc)",
            "Valor TUSD (sem desc)",
            "Valor Demanda (sem desc)",
            "Subtotal Atual",
            "Valor Energia (c/ desc)",
            "Valor TUSD (c/ desc)",
            "Valor Demanda (c/ desc)",
            "Subtotal c/ Desconto",
            "Economia Bruta",
            "Impostos (PIS/COFINS + ICMS)",
            "Encargos (Bandeira + Tx + Enc.)",
            "Economia Líquida",
            "% Economia"
        ],
        "Valor": [
            f"{resultado_g0['energia_total_mwh']:.2f} MWh",
            f"{resultado_g0['energia_fp_mwh']:.2f} MWh",
            f"{resultado_g0['energia_p_mwh']:.2f} MWh",
            format_currency(resultado_g0["tarifa_energia_desc"]),
            format_currency(resultado_g0["tarifa_tusd_desc"]),
            format_currency(resultado_g0["tarifa_demanda_desc"]),
            format_currency(resultado_g0["valor_energia_sem_desc"]),
            format_currency(resultado_g0["valor_tusd_sem_desc"]),
            format_currency(resultado_g0["valor_demanda_sem_desc"]),
            format_currency(resultado_g0["subtotal_sem_desc"]),
            format_currency(resultado_g0["valor_energia_com_desc"]),
            format_currency(resultado_g0["valor_tusd_com_desc"]),
            format_currency(resultado_g0["valor_demanda_com_desc"]),
            format_currency(resultado_g0["subtotal_com_desc"]),
            format_currency(resultado_g0["economia_bruta"]),
            format_currency(resultado_g0["impostos"]),
            format_currency(resultado_g0["encargos"]),
            format_currency(resultado_g0["economia_liquida"]),
            format_percent(resultado_g0["pct_economia"])
        ]
    })
    st.dataframe(det_g0, use_container_width=True, hide_index=True)

# ============================================================
# ABA 4: COMPARATIVO
# ============================================================
with tabs[3]:
    st.subheader("📈 Análise Comparativa Detalhada")

    # Tabela comparativa
    comp_detalhado = pd.DataFrame({
        "Indicador": [
            "Consumo Mensal (MWh)",
            "Demanda (kW)",
            "Fatura Atual (R$/mês)",
            "Fatura c/ Desconto (R$/mês)",
            "Economia Bruta (R$/mês)",
            "Impostos (R$/mês)",
            "Encargos (R$/mês)",
            "Economia Líquida (R$/mês)",
            "Economia Anual (R$)",
            "% Redução",
            "Investimento (R$)",
            "Payback Simples",
            "Payback Descontado",
            "VPL (15 anos)",
            "TIR (% a.a.)"
        ],
        "APE": [
            f"{consumo_mensal:.2f}",
            f"{demanda_kw:.0f}",
            format_currency(resultado_ape["subtotal_sem_desc"]),
            format_currency(resultado_ape["subtotal_com_desc"]),
            format_currency(resultado_ape["economia_bruta"]),
            format_currency(resultado_ape["impostos"]),
            format_currency(resultado_ape["encargos"]),
            format_currency(resultado_ape["economia_liquida"]),
            format_currency(economia_anual_ape),
            format_percent(resultado_ape["pct_economia"]),
            format_currency(investimento_ape),
            f"{payback_ape['payback_simples']:.1f} anos",
            f"{payback_ape['payback_descontado']:.1f} anos" if payback_ape['payback_descontado'] != float('inf') else "N/A",
            format_currency(payback_ape["vpl"]),
            f"{payback_ape['tir']:.1f}%"
        ],
        "G0": [
            f"{consumo_mensal:.2f}",
            f"{demanda_kw:.0f}",
            format_currency(resultado_g0["subtotal_sem_desc"]),
            format_currency(resultado_g0["subtotal_com_desc"]),
            format_currency(resultado_g0["economia_bruta"]),
            format_currency(resultado_g0["impostos"]),
            format_currency(resultado_g0["encargos"]),
            format_currency(resultado_g0["economia_liquida"]),
            format_currency(economia_anual_g0),
            format_percent(resultado_g0["pct_economia"]),
            format_currency(investimento_g0),
            f"{payback_g0['payback_simples']:.1f} anos",
            f"{payback_g0['payback_descontado']:.1f} anos" if payback_g0['payback_descontado'] != float('inf') else "N/A",
            format_currency(payback_g0["vpl"]),
            f"{payback_g0['tir']:.1f}%"
        ]
    })

    st.dataframe(comp_detalhado, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Gráfico de retorno acumulado
    st.plotly_chart(
        grafico_economia_anual(economia_anual_ape, economia_anual_g0, investimento_ape, investimento_g0),
        use_container_width=True
    )

    # Radar chart comparativo
    categorias_radar = ["Economia %", "Payback", "VPL", "TIR", "Redução Fatura"]

    # Normalizar valores para 0-100 (inverter payback)
    max_payback = max(payback_ape["payback_simples"], payback_g0["payback_simples"], 1)

    ape_radar = [
        min(resultado_ape["pct_economia"] * 2, 100),  # Economia %
        max(0, 100 - (payback_ape["payback_simples"] / max_payback * 100)),  # Payback (menor é melhor)
        min(max(payback_ape["vpl"] / 1000000, 0), 100),  # VPL
        min(payback_ape["tir"] * 2, 100),  # TIR
        min(resultado_ape["pct_economia"] * 2, 100)  # Redução Fatura
    ]

    g0_radar = [
        min(resultado_g0["pct_economia"] * 2, 100),
        max(0, 100 - (payback_g0["payback_simples"] / max_payback * 100)),
        min(max(payback_g0["vpl"] / 1000000, 0), 100),
        min(payback_g0["tir"] * 2, 100),
        min(resultado_g0["pct_economia"] * 2, 100)
    ]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=ape_radar + [ape_radar[0]],
        theta=categorias_radar + [categorias_radar[0]],
        fill="toself",
        name="APE",
        line_color="#00d4ff",
        fillcolor="rgba(0,212,255,0.2)"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=g0_radar + [g0_radar[0]],
        theta=categorias_radar + [categorias_radar[0]],
        fill="toself",
        name="G0",
        line_color="#7b2cbf",
        fillcolor="rgba(123,44,191,0.2)"
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Radar Comparativo de Indicadores",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        height=500
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ============================================================
# ABA 5: SAZONALIDADE
# ============================================================
with tabs[4]:
    st.subheader("📅 Análise de Sazonalidade Mensal")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### ⚡ APE - Sazonalidade")
        st.plotly_chart(grafico_sazonalidade(df_mensal_ape), use_container_width=True)
    with col2:
        st.markdown("##### 🔋 G0 - Sazonalidade")
        st.plotly_chart(grafico_sazonalidade(df_mensal_g0), use_container_width=True)

    st.markdown("---")

    # Comparativo sazonal
    fig_saz = go.Figure()
    fig_saz.add_trace(go.Scatter(
        x=df_mensal_ape["Mês"], y=df_mensal_ape["Economia (R$)"],
        mode="lines+markers", name="Economia APE",
        line=dict(color="#00d4ff", width=3), fill="tonexty"
    ))
    fig_saz.add_trace(go.Scatter(
        x=df_mensal_g0["Mês"], y=df_mensal_g0["Economia (R$)"],
        mode="lines+markers", name="Economia G0",
        line=dict(color="#7b2cbf", width=3), fill="tonexty"
    ))
    fig_saz.update_layout(
        title="Comparativo de Economia Mensal",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16,20,50,0.5)",
        font=dict(color="#e0e0e0"),
        xaxis_title="Mês",
        yaxis_title="Economia (R$)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        hovermode="x unified"
    )
    st.plotly_chart(fig_saz, use_container_width=True)

    # Tabela consolidada sazonal
    df_saz_comp = pd.DataFrame({
        "Mês": df_mensal_ape["Mês"],
        "Consumo (MWh)": df_mensal_ape["Consumo (MWh)"],
        "Economia APE (R$)": df_mensal_ape["Economia (R$)"],
        "Economia G0 (R$)": df_mensal_g0["Economia (R$)"],
        "Diferença (R$)": df_mensal_ape["Economia (R$)"] - df_mensal_g0["Economia (R$)"],
        "Melhor Opção": ["APE" if a > g else "G0" for a, g in zip(df_mensal_ape["Economia (R$)"], df_mensal_g0["Economia (R$)"])]
    })
    st.dataframe(df_saz_comp, use_container_width=True, hide_index=True)

# ============================================================
# ABA 6: FLUXO DE CAIXA
# ============================================================
with tabs[5]:
    st.subheader("💵 Análise de Fluxo de Caixa (20 anos)")

    st.plotly_chart(
        grafico_payback(payback_ape["fluxos"], payback_g0["fluxos"],
                       payback_ape["payback_simples"], payback_g0["payback_simples"]),
        use_container_width=True
    )

    st.markdown("---")

    # Tabela de fluxo de caixa
    anos_fc = list(range(0, 21))
    fluxo_ape = payback_ape["fluxos"]
    fluxo_g0 = payback_g0["fluxos"]

    df_fc = pd.DataFrame({
        "Ano": anos_fc,
        "Fluxo APE (R$)": [format_currency(v) for v in fluxo_ape],
        "Acumulado APE (R$)": [format_currency(sum(fluxo_ape[:i+1])) for i in range(len(fluxo_ape))],
        "Fluxo G0 (R$)": [format_currency(v) for v in fluxo_g0],
        "Acumulado G0 (R$)": [format_currency(sum(fluxo_g0[:i+1])) for i in range(len(fluxo_g0))]
    })

    st.dataframe(df_fc, use_container_width=True, hide_index=True)

    # Cards de payback
    st.markdown("---")
    st.subheader("⏱️ Indicadores de Retorno")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        create_metric_card("Payback APE", f"{payback_ape['payback_simples']:.1f} anos", "Simples", "neutral", "⏱️")
    with col2:
        create_metric_card("Payback G0", f"{payback_g0['payback_simples']:.1f} anos", "Simples", "neutral", "⏱️")
    with col3:
        create_metric_card("VPL APE", format_currency(payback_ape["vpl"]), "15 anos | 10% a.a.", "positive" if payback_ape["vpl"] > 0 else "negative", "📊")
    with col4:
        create_metric_card("VPL G0", format_currency(payback_g0["vpl"]), "15 anos | 10% a.a.", "positive" if payback_g0["vpl"] > 0 else "negative", "📊")

    col1, col2 = st.columns(2)
    with col1:
        create_metric_card("TIR APE", f"{payback_ape['tir']:.1f}% a.a.", "Taxa Interna de Retorno", "positive" if payback_ape["tir"] > 10 else "neutral", "📈")
    with col2:
        create_metric_card("TIR G0", f"{payback_g0['tir']:.1f}% a.a.", "Taxa Interna de Retorno", "positive" if payback_g0["tir"] > 10 else "neutral", "📈")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #8892b0; font-size: 0.8rem;">
    <p>⚡ Memória de Massa | Dashboard Técnico-Comercial | Mercado Livre de Energia</p>
    <p>Dados atualizados em tempo real conforme parâmetros da sidebar</p>
</div>
""", unsafe_allow_html=True)
