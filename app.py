import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import io

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GridZero Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp { background-color: #f4f6fb; }

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #1f2937;
    font-weight: 600;
}

.block-container {
    padding-top: 4rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

header[data-testid="stHeader"] {
    background-color: rgba(244, 246, 251, 0.8);
    backdrop-filter: blur(6px);
}

/* Botões primários */
button[kind="primary"] {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    height: 42px;
}
button[kind="primary"]:hover { background-color: #1d4ed8; }

button[kind="secondary"] {
    background-color: #ffffff;
    color: #374151;
    border-radius: 10px;
    border: 1px solid #d1d5db;
    font-weight: 500;
    height: 42px;
}
button[kind="secondary"]:hover {
    background-color: #f3f4f6;
    border-color: #9ca3af;
}

/* KPI cards */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    height: 160px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-title { font-size: 13px; font-weight: 600; letter-spacing: 0.02em; }
.kpi-value {
    font-size: 22px;
    font-weight: 700;
    line-height: 1.15;
    margin-top: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-sub {
    font-size: 11px;
    color: #6b7280;
    margin-top: 4px;
    line-height: 1.3;
}
.kpi-spark { margin-top: 4px; height: 28px; }

.replay-card {
    background: white;
    border-radius: 16px;
    padding: 14px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.replay-clock { font-size: 14px; color: #6b7280; }
.replay-time { font-size: 19px; font-weight: 700; color: #1f2937; margin-top: 4px; line-height: 1.2; }
.replay-sub { font-size: 12px; color: #9ca3af; margin-top: 6px; }

.status-card {
    background: white;
    border-radius: 16px;
    padding: 14px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.status-label { font-size: 13px; font-weight: 600; color: #6b7280; }
.status-main { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.status-icon { font-size: 26px; }
.status-text { font-size: 20px; font-weight: 700; }
.status-sub { font-size: 13px; color: #6b7280; margin-top: 4px; }

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #1f2937;
    margin: 14px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Mode toggle no topo do gráfico */
.mode-bar {
    background: white;
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    display: inline-flex;
    gap: 4px;
    margin-bottom: 8px;
}

/* Controles no topo do gráfico */
.controls-box {
    background: #ffffff;
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 10px;
}

/* Summary boxes (fixos no rodapé) */
.summary-box {
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.summary-blue { background: #eff6ff; }
.summary-red { background: #fef2f2; }
.summary-green { background: #f0fdf4; }
.summary-yellow { background: #fefce8; }
.summary-orange { background: #fff7ed; }
.summary-title { font-size: 14px; font-weight: 600; }
.summary-value { font-size: 28px; font-weight: 700; margin-top: 8px; line-height: 1.1; }
.summary-sub { font-size: 12px; color: #6b7280; margin-top: 4px; }

/* Descrição explicativa que fica logo abaixo do título dos indicadores */
.indicator-desc {
    font-size: 11px;
    color: #6b7280;
    margin-top: 4px;
    line-height: 1.35;
    font-weight: 400;
}

/* Abas de navegação principal (Análise Operacional vs Financeira) */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: white;
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 18px;
}
.stTabs [data-baseweb="tab"] {
    height: 44px;
    padding: 0 22px;
    border-radius: 8px;
    background-color: transparent;
    color: #6b7280;
    font-weight: 600;
    font-size: 14px;
    border: none;
    transition: all 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #f3f4f6;
    color: #1f2937;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #2563eb;
    color: white;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

/* Cards financeiros (Payback, TIR, VPL) */
.fin-card {
    background: white;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    border-left: 4px solid #2563eb;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.fin-card-title { font-size: 13px; font-weight: 600; color: #6b7280; letter-spacing: 0.02em; }
.fin-card-value {
    font-size: 30px;
    font-weight: 700;
    line-height: 1.1;
    margin-top: 4px;
    color: #1f2937;
}
.fin-card-sub { font-size: 11px; color: #9ca3af; margin-top: 4px; line-height: 1.3; }

.fin-card.viable { border-left-color: #16a34a; }
.fin-card.viable .fin-card-value { color: #16a34a; }
.fin-card.warning { border-left-color: #ca8a04; }
.fin-card.warning .fin-card-value { color: #ca8a04; }
.fin-card.unviable { border-left-color: #dc2626; }
.fin-card.unviable .fin-card-value { color: #dc2626; }

/* Cabeçalho da seção financeira com destaque */
.fin-section-header {
    background: linear-gradient(90deg, #f0f9ff 0%, #ffffff 100%);
    border-left: 4px solid #2563eb;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 20px 0 14px 0;
}
.fin-section-header h2 {
    font-size: 20px;
    font-weight: 700;
    color: #1f2937;
    margin: 0;
}
.fin-section-header p {
    font-size: 13px;
    color: #6b7280;
    margin: 4px 0 0 0;
}

/* Expander de premissas — estilo consistente */
[data-testid="stExpander"] {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #1f2937 !important;
}

/* Subtítulos dos grupos de premissas */
.premissa-group-title {
    font-size: 13px;
    font-weight: 700;
    color: #2563eb;
    margin: 10px 0 8px 0;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.file-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.file-icon { font-size: 20px; }
.file-info { flex: 1; }
.file-name { font-size: 13px; font-weight: 600; color: #1f2937; }
.file-size { font-size: 11px; color: #6b7280; }
.file-check { color: #16a34a; font-size: 16px; }

/* Labels do file uploader e date input em cor escura */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label p,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stDateInput"] label,
[data-testid="stDateInput"] label p {
    color: #1f2937 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label p {
    font-weight: 600 !important;
    font-size: 14px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    color: #374151 !important;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

_SPARK_COUNTER = [0]

def sparkline_svg(values, color, width=180, height=30):
    """SVG simples de sparkline."""
    if values is None or len(values) < 2:
        return ""
    vals = [v for v in values if pd.notna(v)]
    if len(vals) < 2:
        return ""
    vmin, vmax = min(vals), max(vals)
    span = vmax - vmin if vmax > vmin else 1
    n = len(vals)
    points = []
    for i, v in enumerate(vals):
        x = (i / (n - 1)) * width
        y = height - ((v - vmin) / span) * height
        points.append(f"{x:.1f},{y:.1f}")
    path = "M " + " L ".join(points)
    area_points = (
        f"M 0,{height} L "
        + " L ".join(points)
        + f" L {width},{height} Z"
    )
    _SPARK_COUNTER[0] += 1
    grad_id = f"grad-{_SPARK_COUNTER[0]}"
    return f'''
    <svg width="100%" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="{grad_id}" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
            </linearGradient>
        </defs>
        <path d="{area_points}" fill="url(#{grad_id})"/>
        <path d="{path}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
    </svg>
    '''


def kpi_card_html(title, value, color, sub="", sparkline_html="", description=""):
    """Card KPI com sub-texto opcional, descrição explicativa opcional (logo
    abaixo do título) e sparkline.
    """
    desc_html = f'<div class="indicator-desc">{description}</div>' if description else ""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card">'
        f'<div>'
        f'<div class="kpi-title" style="color:{color}">{title}</div>'
        f'{desc_html}'
        f'<div class="kpi-value" style="color:{color}">{value}</div>'
        f'{sub_html}'
        f'</div>'
        f'<div class="kpi-spark">{sparkline_html}</div>'
        f'</div>'
    )


def summary_box_html(title, value, color, cls, sub="", description=""):
    """Card de resumo com descrição opcional logo abaixo do título."""
    desc_html = f'<div class="indicator-desc">{description}</div>' if description else ""
    return (
        f'<div class="summary-box {cls}">'
        f'<div class="summary-title" style="color:{color}">{title}</div>'
        f'{desc_html}'
        f'<div class="summary-value" style="color:{color}">{value}</div>'
        f'<div class="summary-sub">{sub}</div>'
        f'</div>'
    )


def format_filesize(num_bytes):
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.1f} MB"


def fmt_int(v):
    """Formata número com separador de milhar (pt-BR)."""
    return f"{v:,.0f}".replace(",", ".")


def fmt_energia(v_kwh):
    """Formata energia escolhendo kWh ou MWh automaticamente.
    Acima de 10.000 kWh (10 MWh), passa para MWh com 2 casas decimais.
    """
    if abs(v_kwh) >= 10_000:
        v_mwh = v_kwh / 1000
        return f"{v_mwh:,.2f} MWh".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{fmt_int(v_kwh)} kWh"


def fmt_reais(v, com_simbolo=True):
    """Formata valor em reais (pt-BR). Acima de 1 milhão usa 'mi', acima de 1 bilhão 'bi'."""
    if pd.isna(v) or v is None:
        return "—"
    prefixo = "R$ " if com_simbolo else ""
    abs_v = abs(v)
    sinal = "-" if v < 0 else ""
    if abs_v >= 1_000_000_000:
        valor = f"{abs_v / 1_000_000_000:,.2f} bi".replace(",", "X").replace(".", ",").replace("X", ".")
    elif abs_v >= 1_000_000:
        valor = f"{abs_v / 1_000_000:,.2f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        valor = f"{abs_v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{prefixo}{sinal}{valor}"


def fmt_reais_exato(v):
    """Formata em reais com casas decimais exatas, sem abreviação (para tabelas)."""
    if pd.isna(v) or v is None:
        return "—"
    sinal = "-" if v < 0 else ""
    abs_v = abs(v)
    s = f"{abs_v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {sinal}{s}"


def fmt_pct(v, casas=1):
    """Formata percentual (pt-BR)."""
    if pd.isna(v) or v is None:
        return "—"
    return f"{v * 100:.{casas}f}%".replace(".", ",")


def fin_card_html(titulo, valor, sub="", classe=""):
    """Card financeiro com borda colorida lateral (viable/warning/unviable)."""
    return (
        f'<div class="fin-card {classe}">'
        f'<div>'
        f'<div class="fin-card-title">{titulo}</div>'
        f'<div class="fin-card-value">{valor}</div>'
        f'</div>'
        f'<div class="fin-card-sub">{sub}</div>'
        f'</div>'
    )


def estimar_capacidade_kwp(df_originais):
    """Estima a capacidade instalada da UFV pelo pico de geração observado
    no CSV, com pequena margem para considerar perdas e variabilidade.
    """
    pico = df_originais["Geracao"].max() if len(df_originais) else 0
    # Pico de geração típico é ~80-85% da capacidade nominal
    return pico / 0.85 if pico > 0 else 0


def classificar_fator_cobertura(pct):
    """Retorna (cor, icone, texto_diagnostico) para o Fator de Cobertura.
    Mede a redução na conta de energia do cliente.
    """
    if pct >= 50:
        return ("#16a34a", "✅", "Excelente — Redução máxima possível sem uso de baterias.")
    elif pct >= 30:
        return ("#ca8a04", "🔶", "Padrão comum — Bom suprimento diurno, típico de perfis mistos.")
    else:
        return ("#dc2626", "⚠️", "Baixo impacto — Consumo predominante à noite ou usina pequena.")


def classificar_taxa_desperdicio(pct):
    """Retorna (cor, icone, texto_diagnostico) para a Taxa de Desperdício.
    Mede a energia jogada fora (curtailment).
    """
    if pct < 15:
        return ("#16a34a", "✅", "Eficiente — Perdas mínimas, cenário ideal para um Payback rápido.")
    elif pct <= 30:
        return ("#ca8a04", "🔶", "Moderado — Nível de corte dentro da normalidade para Grid Zero.")
    else:
        return ("#dc2626", "⚠️", "Crítico — Alta perda de energia, o que prejudica o retorno financeiro.")


# Textos descritivos dos indicadores (compartilhados entre header e cards fixos)
DESC_SIMULTANEIDADE = (
    "É a porcentagem de toda a energia gerada pela usina "
    "que é consumida instantaneamente no local."
)
DESC_FATOR_COBERTURA = (
    "É a porcentagem de todo o consumo de energia do local "
    "que é suprida diretamente pela usina solar."
)
DESC_TAXA_DESPERDICIO = (
    "É a porcentagem da energia que a usina era capaz de gerar, "
    "mas precisou ser descartada por falta de consumo."
)


# =========================================================
# FUNÇÕES DE ANÁLISE FINANCEIRA
# =========================================================

def calcular_fluxo_caixa(premissas, geracao_anual_kwh):
    """Calcula o fluxo de caixa anual de 30 anos para uma usina GridZero.

    Replicado do modelo da planilha (aba 'Análise Financeira G0'):
    - Geração degradada anualmente
    - Faturamento crescente conforme ajuste de tarifa
    - Despesas crescentes conforme inflação
    - Substituição de inversores no ano definido
    - Resultado líquido e saldo acumulado

    Retorna um DataFrame com colunas: Ano, Geracao_kWh, Preco_kWh, Faturamento,
    OeM, Arrendamento, Rateio_GA, Demanda_Adicional, Seguro, Inversores,
    Despesas_Op, Financiamento, Resultado_Liquido, Saldo_Acumulado.
    """
    vida_util = int(premissas['vida_util'])
    capex = premissas['capex_total']
    capacidade_kwp = premissas['capacidade_kwp']
    preco_inicial = premissas['preco_energia']
    ajuste_preco = premissas['ajuste_preco']
    inflacao = premissas['inflacao']
    degradacao = premissas['degradacao']
    custo_om_por_kwp = premissas['custo_om_por_kwp']
    custo_arr_por_kwp = premissas['custo_arr_por_kwp']
    custo_ga_por_kwp = premissas['custo_ga_por_kwp']
    seguro_pct = premissas['seguro_pct']
    demanda_extra_anual = premissas['demanda_extra_anual']
    custo_inversores_pct = premissas['custo_inversores_pct']
    ano_substituicao = int(premissas['ano_substituicao'])
    juros_aa = premissas['juros_aa']
    prazo_financiamento = int(premissas['prazo_financiamento'])

    # Ano 0: entrada (CAPEX) e financiamento se houver
    parcela_anual_financiamento = 0
    if prazo_financiamento > 0 and juros_aa > 0:
        # PMT mensal × 12: parcela anual de financiamento
        juros_am = (1 + juros_aa) ** (1/12) - 1
        n_meses = prazo_financiamento * 12
        if juros_am > 0:
            pmt_mensal = capex * (juros_am * (1 + juros_am) ** n_meses) / ((1 + juros_am) ** n_meses - 1)
            parcela_anual_financiamento = -pmt_mensal * 12
        else:
            parcela_anual_financiamento = -capex / prazo_financiamento

    linhas = []

    # Ano 0: investimento inicial (sem geração, sem receita)
    linhas.append({
        'Ano': 0,
        'Geracao_kWh': 0,
        'Preco_kWh': preco_inicial,
        'Faturamento': 0,
        'OeM': 0,
        'Arrendamento': 0,
        'Rateio_GA': 0,
        'Demanda_Adicional': 0,
        'Seguro': 0,
        'Inversores': 0,
        'Despesas_Op': 0,
        'Financiamento': 0,
        'Investimento': -capex,
        'Resultado_Liquido': -capex,
    })

    # Anos 1 a vida_util
    for ano in range(1, vida_util + 1):
        # Geração com degradação
        ger = geracao_anual_kwh * ((1 - degradacao) ** (ano - 1))
        # Tarifa com ajuste anual
        preco = preco_inicial * ((1 + ajuste_preco) ** ano)
        faturamento = ger * preco

        # Despesas (crescem com inflação a partir do ano 1)
        fator_inflacao = (1 + inflacao) ** (ano - 1)
        om = -custo_om_por_kwp * capacidade_kwp * fator_inflacao
        arr = -custo_arr_por_kwp * capacidade_kwp * fator_inflacao
        ga = -custo_ga_por_kwp * capacidade_kwp * fator_inflacao
        dem = -demanda_extra_anual * fator_inflacao
        seg = -capex * seguro_pct  # seguro NÃO infla na planilha

        # Inversores: substituição no ano configurado (múltiplos de ano_substituicao)
        inv = 0
        if ano_substituicao > 0 and ano % ano_substituicao == 0 and ano < vida_util:
            inv = -capex * custo_inversores_pct

        despesas_op = om + arr + ga + dem + seg + inv

        # Financiamento: apenas durante o prazo
        fin = parcela_anual_financiamento if ano <= prazo_financiamento else 0

        resultado_liquido = faturamento + despesas_op + fin

        linhas.append({
            'Ano': ano,
            'Geracao_kWh': ger,
            'Preco_kWh': preco,
            'Faturamento': faturamento,
            'OeM': om,
            'Arrendamento': arr,
            'Rateio_GA': ga,
            'Demanda_Adicional': dem,
            'Seguro': seg,
            'Inversores': inv,
            'Despesas_Op': despesas_op,
            'Financiamento': fin,
            'Investimento': 0,
            'Resultado_Liquido': resultado_liquido,
        })

    fluxo = pd.DataFrame(linhas)
    fluxo['Saldo_Acumulado'] = fluxo['Resultado_Liquido'].cumsum()
    return fluxo


def calcular_indicadores_financeiros(fluxo, tma):
    """Calcula Payback simples, TIR, VPL e VPL/kW a partir do fluxo de caixa."""

    # Payback simples: ano em que o saldo acumulado cruza zero
    saldo = fluxo['Saldo_Acumulado'].values
    payback_anos = None
    for i in range(1, len(saldo)):
        if saldo[i - 1] < 0 and saldo[i] >= 0:
            # Interpolação linear dentro do ano
            frac = -saldo[i - 1] / (saldo[i] - saldo[i - 1])
            payback_anos = (i - 1) + frac
            break

    # VPL (Valor Presente Líquido)
    fluxos_anuais = fluxo['Resultado_Liquido'].values
    vpl = sum(fl / ((1 + tma) ** n) for n, fl in enumerate(fluxos_anuais))

    # TIR (Taxa Interna de Retorno) — método de bissecção
    def npv(rate, flows):
        if rate <= -1:
            return float('inf')
        return sum(f / ((1 + rate) ** n) for n, f in enumerate(flows))

    tir = None
    # Bissecção entre -0.99 e 5.0 (range razoável para projetos solares)
    low, high = -0.99, 5.0
    try:
        npv_low = npv(low, fluxos_anuais)
        npv_high = npv(high, fluxos_anuais)
        if npv_low * npv_high < 0:
            for _ in range(100):
                mid = (low + high) / 2
                npv_mid = npv(mid, fluxos_anuais)
                if abs(npv_mid) < 1:
                    tir = mid
                    break
                if npv_mid * npv_low < 0:
                    high = mid
                else:
                    low = mid
                    npv_low = npv_mid
            if tir is None:
                tir = (low + high) / 2
    except (OverflowError, ZeroDivisionError):
        tir = None

    return {
        'payback_anos': payback_anos,
        'tir': tir,
        'vpl': vpl,
    }


def calcular_lcoe(fluxo, capex, tma):
    """Custo Nivelado de Energia (LCOE): R$/kWh equivalente do solar.

    Replica a fórmula da planilha MELI/Prologis:
        LCOE = CAPEX / Σ(Geração ao longo da vida útil)

    Esta é uma versão simplificada que considera apenas o CAPEX dividido
    pela energia total entregue, sem descontar OPEX nem aplicar TMA.
    É o "custo bruto" da energia solar do projeto, útil para comparar
    diretamente com a tarifa atual da rede.
    """
    geracao_total = fluxo['Geracao_kWh'].sum()
    if geracao_total > 0:
        return capex / geracao_total
    return 0


@st.cache_data(show_spinner=False)
def carregar_e_processar(gen_bytes, load_bytes):
    """Carrega CSVs, calcula GridZero e insere pontos de cruzamento.
    Cacheado: só roda quando os bytes mudarem.
    """
    gen_df = pd.read_csv(io.BytesIO(gen_bytes))
    load_df = pd.read_csv(io.BytesIO(load_bytes))

    gen_df.columns = ["DataHora", "Geracao"]
    load_df.columns = ["DataHora", "Carga"]

    gen_df["DataHora"] = pd.to_datetime(gen_df["DataHora"])
    load_df["DataHora"] = pd.to_datetime(load_df["DataHora"])

    df = pd.merge(gen_df, load_df, on="DataHora").sort_values("DataHora").reset_index(drop=True)

    df["Geracao_Limitada"] = df[["Geracao", "Carga"]].min(axis=1)
    df["Geracao_Cortada"] = df["Geracao"] - df["Geracao_Limitada"]
    df["Energia_Light"] = df["Carga"] - df["Geracao_Limitada"]
    df["Energia_Light_Visual"] = df["Energia_Light"] - df["Geracao_Cortada"]

    rows = []
    n = len(df)
    for i in range(n):
        rows.append(df.iloc[i].to_dict())
        if i < n - 1:
            a = df.iloc[i]
            b = df.iloc[i + 1]
            diff_a = a["Geracao"] - a["Carga"]
            diff_b = b["Geracao"] - b["Carga"]
            if diff_a * diff_b < 0:
                frac = diff_a / (diff_a - diff_b)
                t_cross = a["DataHora"] + (b["DataHora"] - a["DataHora"]) * frac
                carga_cross = a["Carga"] + (b["Carga"] - a["Carga"]) * frac
                rows.append({
                    "DataHora": t_cross,
                    "Carga": carga_cross,
                    "Geracao": carga_cross,
                    "Geracao_Limitada": carga_cross,
                    "Geracao_Cortada": 0.0,
                    "Energia_Light": 0.0,
                    "Energia_Light_Visual": 0.0,
                })
    out = pd.DataFrame(rows).reset_index(drop=True)
    out["Geracao_Cortada_Visual"] = out.apply(
        lambda row: row["Geracao"] if row["Geracao_Cortada"] > 0 else None,
        axis=1
    )
    for idx in range(len(out)):
        if pd.isna(out.loc[idx, "Geracao_Cortada_Visual"]):
            prev_corte = idx > 0 and pd.notna(out.loc[idx - 1, "Geracao_Cortada_Visual"])
            next_corte = idx < len(out) - 1 and pd.notna(out.loc[idx + 1, "Geracao_Cortada_Visual"])
            if prev_corte or next_corte:
                out.loc[idx, "Geracao_Cortada_Visual"] = out.loc[idx, "Carga"]
    return out


# =========================================================
# SESSION STATE
# =========================================================

if "index" not in st.session_state:
    st.session_state.index = 0
if "run_simulation" not in st.session_state:
    st.session_state.run_simulation = False
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Intervalo"
if "intervalo_inicio" not in st.session_state:
    st.session_state.intervalo_inicio = None
if "intervalo_fim" not in st.session_state:
    st.session_state.intervalo_fim = None


# =========================================================
# CALLBACKS
# =========================================================

def toggle_play():
    st.session_state.run_simulation = not st.session_state.run_simulation

def reset_replay():
    st.session_state.index = 0

def set_mode_replay():
    st.session_state.view_mode = "Replay"
    st.session_state.run_simulation = False

def set_mode_intervalo():
    st.session_state.view_mode = "Intervalo"
    st.session_state.run_simulation = False

def aplicar_atalho_intervalo(dias, df):
    """Define o intervalo como os últimos N dias do dataset (ou tudo)."""
    if dias is None:
        st.session_state.intervalo_inicio = df["DataHora"].min().date()
        st.session_state.intervalo_fim = df["DataHora"].max().date()
    else:
        fim = df["DataHora"].max().date()
        inicio = fim - pd.Timedelta(days=dias)
        st.session_state.intervalo_inicio = max(inicio, df["DataHora"].min().date())
        st.session_state.intervalo_fim = fim


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## Arquivos")

    generation_file = st.file_uploader("geracao.csv", type=["csv"], key="up_gen")
    load_file = st.file_uploader("consumo.csv", type=["csv"], key="up_load")

    if generation_file is not None:
        st.markdown(
            f"""
            <div class="file-card">
                <div class="file-icon">📄</div>
                <div class="file-info">
                    <div class="file-name">{generation_file.name}</div>
                    <div class="file-size">{format_filesize(generation_file.size)}</div>
                </div>
                <div class="file-check">✓</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    if load_file is not None:
        st.markdown(
            f"""
            <div class="file-card">
                <div class="file-icon">📄</div>
                <div class="file-info">
                    <div class="file-name">{load_file.name}</div>
                    <div class="file-size">{format_filesize(load_file.size)}</div>
                </div>
                <div class="file-check">✓</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(
        "<div style='color:#6b7280; font-size:13px;'>"
        "Os controles de replay e seleção de intervalo "
        "ficam no topo do gráfico."
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# PROCESSAMENTO PRINCIPAL
# =========================================================

if generation_file and load_file:

    df = carregar_e_processar(
        generation_file.getvalue(),
        load_file.getvalue()
    )

    st.session_state.df_processado = df

    data_min = df["DataHora"].min().date()
    data_max = df["DataHora"].max().date()

    if st.session_state.intervalo_inicio is None:
        st.session_state.intervalo_inicio = data_min
    if st.session_state.intervalo_fim is None:
        st.session_state.intervalo_fim = data_max

    # =====================================================
    # ESTATÍSTICAS GLOBAIS (CSV INTEIRO)
    # =====================================================
    df_originais = df[df["DataHora"].dt.minute == 0].copy() if len(df) > 0 else df

    total_import_full = df_originais[df_originais["Energia_Light"] > 0]["Energia_Light"].sum()
    energia_cortada_full = df_originais["Geracao_Cortada"].sum()
    energia_aproveitada_full = df_originais["Geracao_Limitada"].sum()
    energia_geravel_full = df_originais["Geracao"].sum()
    energia_consumida_full = df_originais["Carga"].sum()
    max_corte_full = df_originais["Geracao_Cortada"].max() if len(df_originais) else 0
    horas_corte_full = (df_originais["Geracao_Cortada"] > 0).sum()
    total_horas_full = len(df_originais)

    if energia_consumida_full > 0:
        fator_cobertura_full = (energia_aproveitada_full / energia_consumida_full) * 100
    else:
        fator_cobertura_full = 0

    if energia_geravel_full > 0:
        taxa_desperdicio_full = (energia_cortada_full / energia_geravel_full) * 100
        simultaneidade_full = (energia_aproveitada_full / energia_geravel_full) * 100
    else:
        taxa_desperdicio_full = 0
        simultaneidade_full = 0

    if st.session_state.index >= len(df):
        st.session_state.index = len(df) - 1
    if st.session_state.index < 0:
        st.session_state.index = 0

    # =====================================================
    # MODO ATUAL E DADOS DOS KPIs
    # =====================================================
    modo = st.session_state.view_mode

    if modo == "Replay":
        current_index = st.session_state.index
        chart_df = df.iloc[: current_index + 1]
        current = df.iloc[current_index]

        kpi_data = {
            "header_titulo": current["DataHora"].strftime("%d/%m/%Y %H:%M"),
            "header_sub": "Ponto atual do replay",
            "carga": (f"{fmt_int(current['Carga'])} kW", "Instantâneo"),
            "limitada": (f"{fmt_int(current['Geracao_Limitada'])} kW", "Instantâneo"),
            "cortada": (f"{fmt_int(current['Geracao_Cortada'])} kW", "Instantâneo"),
            "light": (f"{fmt_int(current['Energia_Light'])} kW", "Instantâneo"),
            "status_ativo": current["Geracao_Cortada"] > 0,
        }
        spark_source = chart_df
    else:
        d_ini = pd.to_datetime(st.session_state.intervalo_inicio)
        d_fim = pd.to_datetime(st.session_state.intervalo_fim) + pd.Timedelta(days=1)
        chart_df = df[(df["DataHora"] >= d_ini) & (df["DataHora"] < d_fim)]

        intervalo_originais = chart_df[chart_df["DataHora"].dt.minute == 0]

        carga_total_kwh = intervalo_originais["Carga"].sum()
        limitada_total_kwh = intervalo_originais["Geracao_Limitada"].sum()
        cortada_total_kwh = intervalo_originais["Geracao_Cortada"].sum()
        geravel_total_kwh = intervalo_originais["Geracao"].sum()
        light_total_kwh = intervalo_originais[intervalo_originais["Energia_Light"] > 0]["Energia_Light"].sum()

        horas_ativo = (intervalo_originais["Geracao_Cortada"] > 0).sum()
        total_horas = len(intervalo_originais)

        if geravel_total_kwh > 0:
            simultaneidade_intervalo = (limitada_total_kwh / geravel_total_kwh) * 100
            taxa_desperdicio_intervalo = (cortada_total_kwh / geravel_total_kwh) * 100
        else:
            simultaneidade_intervalo = 0
            taxa_desperdicio_intervalo = 0

        if carga_total_kwh > 0:
            fator_cobertura_intervalo = (limitada_total_kwh / carga_total_kwh) * 100
        else:
            fator_cobertura_intervalo = 0

        kpi_data = {
            "header_titulo": (
                f"{st.session_state.intervalo_inicio.strftime('%d/%m/%Y')} – "
                f"{st.session_state.intervalo_fim.strftime('%d/%m/%Y')}"
            ),
            "header_sub": f"Período selecionado ({total_horas} h)",
            "carga": (fmt_energia(carga_total_kwh), "Energia consumida no período"),
            "limitada": (fmt_energia(limitada_total_kwh), "Energia fornecida pela UFV"),
            "cortada": (fmt_energia(cortada_total_kwh), "Energia cortada pelo GridZero"),
            "light": (fmt_energia(light_total_kwh), "Energia consumida da rede"),
            "status_ativo": horas_ativo > 0,
            "horas_ativo": horas_ativo,
            "total_horas": total_horas,
            "simultaneidade": simultaneidade_intervalo,
            "fator_cobertura": fator_cobertura_intervalo,
            "taxa_desperdicio": taxa_desperdicio_intervalo,
        }
        spark_source = chart_df

    # =====================================================
    # NAVEGAÇÃO EM ABAS
    # =====================================================
    tab_operacional, tab_financeira, tab_simulacao = st.tabs([
        "📊  Análise Operacional",
        "💰  Análise Financeira",
        "🔌  Simulação GridZero"
    ])

    with tab_operacional:
        # =====================================================
        # HEADER — Cards conforme modo
        # =====================================================

        if modo == "Replay":
            cols = st.columns([1.7, 1.3, 1.3, 1.3, 1.3, 1.3])

            with cols[0]:
                st.markdown(
                    f"""
                    <div class="replay-card">
                        <div class="replay-clock">🕒</div>
                        <div class="replay-time">{kpi_data['header_titulo']}</div>
                        <div class="replay-sub">{kpi_data['header_sub']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            def spark_data(col, n=40):
                return spark_source[col].tail(n).tolist()

            cards_config = [
                ("Carga", "carga", "#2563eb", "Carga"),
                ("Energia Aproveitada", "limitada", "#16a34a", "Geracao_Limitada"),
                ("Geração Cortada", "cortada", "#f97316", "Geracao_Cortada"),
                ("Energia da Rede", "light", "#9333ea", "Energia_Light"),
            ]

            for i, (titulo, key, cor, col_dados) in enumerate(cards_config):
                with cols[i + 1]:
                    spark = sparkline_svg(spark_data(col_dados), cor)
                    valor, sub = kpi_data[key]
                    st.markdown(
                        kpi_card_html(titulo, valor, cor, sub, spark),
                        unsafe_allow_html=True
                    )

            with cols[5]:
                if kpi_data["status_ativo"]:
                    status_text, status_sub, status_color, status_icon = (
                        "GridZero Ativo", "Sem exportação", "#16a34a", "🛡️"
                    )
                else:
                    status_text, status_sub, status_color, status_icon = (
                        "Normal", "Sem limitação", "#64748b", "✓"
                    )
                status_label = "Status"

                st.markdown(
                    f"""
                    <div class="status-card">
                        <div class="status-label">{status_label}</div>
                        <div class="status-main">
                            <div class="status-icon">{status_icon}</div>
                            <div class="status-text" style="color:{status_color}">{status_text}</div>
                        </div>
                        <div class="status-sub">{status_sub}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:
            # Modo Intervalo: duas linhas

            st.markdown(
                f"""
                <div style="font-size:14px; font-weight:600; color:#374151; margin-bottom:4px;">
                    🕒 Período selecionado: <span style="color:#2563eb;">{kpi_data['header_titulo']}</span>
                    <span style="font-size:12px; color:#6b7280; font-weight:400;"> — {kpi_data['header_sub']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Linha 1: Energia
            st.markdown(
                '<div style="font-size:13px; font-weight:600; color:#6b7280; margin:10px 0 6px 0;">'
                '⚡ Energia (kWh / MWh)</div>',
                unsafe_allow_html=True
            )

            cols_linha1 = st.columns([1, 1, 1, 1])

            def spark_data(col, n=40):
                return spark_source[col].tail(n).tolist()

            cards_config_linha1 = [
                ("Carga", "carga", "#2563eb", "Carga"),
                ("Energia Aproveitada", "limitada", "#16a34a", "Geracao_Limitada"),
                ("Geração Cortada", "cortada", "#f97316", "Geracao_Cortada"),
                ("Energia da Rede", "light", "#9333ea", "Energia_Light"),
            ]

            for i, (titulo, key, cor, col_dados) in enumerate(cards_config_linha1):
                with cols_linha1[i]:
                    spark = sparkline_svg(spark_data(col_dados), cor)
                    valor, sub = kpi_data[key]
                    st.markdown(
                        kpi_card_html(titulo, valor, cor, sub, spark),
                        unsafe_allow_html=True
                    )

            # Linha 2: Indicadores
            st.markdown(
                '<div style="font-size:13px; font-weight:600; color:#6b7280; margin:14px 0 6px 0;">'
                '📊 Indicadores de Desempenho</div>',
                unsafe_allow_html=True
            )

            cols_linha2 = st.columns([1, 1, 1])

            # Simultaneidade
            simul = kpi_data["simultaneidade"]
            if simul >= 80:
                sim_color, sim_icon, sim_text = "#16a34a", "✅", "Excelente — Máximo aproveitamento da capacidade de geração."
            elif simul >= 60:
                sim_color, sim_icon, sim_text = "#ca8a04", "🔶", "Adequado — Bom equilíbrio de uso da usina durante o dia."
            else:
                sim_color, sim_icon, sim_text = "#dc2626", "⚠️", "Superdimensionado — Boa parte da capacidade do inversor está ociosa."

            with cols_linha2[0]:
                st.markdown(
                    kpi_card_html(
                        "Simultaneidade",
                        f"{simul:.1f}%",
                        sim_color,
                        f"{sim_icon} {sim_text}",
                        "",
                        DESC_SIMULTANEIDADE
                    ),
                    unsafe_allow_html=True
                )

            # Fator de Cobertura
            fc = kpi_data["fator_cobertura"]
            fc_color, fc_icon, fc_text = classificar_fator_cobertura(fc)
            with cols_linha2[1]:
                st.markdown(
                    kpi_card_html(
                        "Fator de Cobertura",
                        f"{fc:.1f}%",
                        fc_color,
                        f"{fc_icon} {fc_text}",
                        "",
                        DESC_FATOR_COBERTURA
                    ),
                    unsafe_allow_html=True
                )

            # Taxa de Desperdício
            td = kpi_data["taxa_desperdicio"]
            td_color, td_icon, td_text = classificar_taxa_desperdicio(td)
            with cols_linha2[2]:
                st.markdown(
                    kpi_card_html(
                        "Taxa de Desperdício",
                        f"{td:.1f}%",
                        td_color,
                        f"{td_icon} {td_text}",
                        "",
                        DESC_TAXA_DESPERDICIO
                    ),
                    unsafe_allow_html=True
                )

        # =====================================================
        # SEÇÃO DO GRÁFICO — Toggle de modo + Controles
        # =====================================================

        st.markdown(
            '<div class="section-title">📈 Fluxo de Potência</div>',
            unsafe_allow_html=True
        )

        mode_col1, mode_col2, mode_spacer = st.columns([1.2, 1.5, 6])
        with mode_col1:
            st.button(
                "▶ Replay ao vivo",
                type="primary" if modo == "Replay" else "secondary",
                use_container_width=True,
                key="btn_mode_replay",
                on_click=set_mode_replay
            )
        with mode_col2:
            st.button(
                "📅 Visualizar intervalo",
                type="primary" if modo == "Intervalo" else "secondary",
                use_container_width=True,
                key="btn_mode_intervalo",
                on_click=set_mode_intervalo
            )

        if modo == "Replay":
            ctrl_cols = st.columns([1.2, 1.0, 2.0, 3.0])
            with ctrl_cols[0]:
                label = "⏸ Pausar" if st.session_state.run_simulation else "▶ Rodar"
                st.button(
                    label,
                    type="primary",
                    use_container_width=True,
                    key="btn_toggle_play",
                    on_click=toggle_play
                )
            with ctrl_cols[1]:
                st.button(
                    "↻ Reiniciar",
                    type="secondary",
                    use_container_width=True,
                    key="btn_reset_replay",
                    on_click=reset_replay
                )
            with ctrl_cols[2]:
                speed = st.slider(
                    "Velocidade (s/passo)",
                    0.05, 2.0, 0.3, 0.05,
                    key="slider_speed"
                )
            with ctrl_cols[3]:
                progresso = (st.session_state.index + 1) / len(df) * 100
                st.markdown(
                    f"<div style='padding-top:10px; color:#6b7280; font-size:13px;'>"
                    f"Progresso: <b style='color:#1f2937'>{st.session_state.index + 1}</b>"
                    f" / {len(df)} pontos ({progresso:.1f}%)"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            ctrl_cols = st.columns([1.5, 1.5, 0.8, 0.8, 0.8, 0.8])
            with ctrl_cols[0]:
                st.date_input(
                    "Início",
                    value=st.session_state.intervalo_inicio,
                    min_value=data_min,
                    max_value=data_max,
                    key="dt_intervalo_inicio_widget",
                    on_change=lambda: st.session_state.update(
                        intervalo_inicio=st.session_state.dt_intervalo_inicio_widget
                    )
                )
            with ctrl_cols[1]:
                st.date_input(
                    "Fim",
                    value=st.session_state.intervalo_fim,
                    min_value=data_min,
                    max_value=data_max,
                    key="dt_intervalo_fim_widget",
                    on_change=lambda: st.session_state.update(
                        intervalo_fim=st.session_state.dt_intervalo_fim_widget
                    )
                )
            with ctrl_cols[2]:
                st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
                st.button("1 dia", use_container_width=True, key="btn_1d",
                          on_click=lambda: aplicar_atalho_intervalo(1, df))
            with ctrl_cols[3]:
                st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
                st.button("7 dias", use_container_width=True, key="btn_7d",
                          on_click=lambda: aplicar_atalho_intervalo(7, df))
            with ctrl_cols[4]:
                st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
                st.button("30 dias", use_container_width=True, key="btn_30d",
                          on_click=lambda: aplicar_atalho_intervalo(30, df))
            with ctrl_cols[5]:
                st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
                st.button("Tudo", use_container_width=True, key="btn_all",
                          on_click=lambda: aplicar_atalho_intervalo(None, df))

        # =====================================================
        # GRÁFICO
        # =====================================================

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=chart_df["DataHora"], y=chart_df["Carga"],
            name="Carga (Consumo)",
            mode="lines",
            line=dict(color="#2563eb", width=2.5, shape="spline", smoothing=1.2)
        ))

        fig.add_trace(go.Scatter(
            x=chart_df["DataHora"], y=chart_df["Geracao_Cortada_Visual"],
            name="Geração Cortada",
            mode="lines",
            line=dict(color="#f97316", width=2.5, dash="dash", shape="spline", smoothing=1.2),
            fill="tonexty",
            fillcolor="rgba(249, 115, 22, 0.20)",
            connectgaps=False
        ))

        fig.add_trace(go.Scatter(
            x=chart_df["DataHora"], y=chart_df["Geracao_Limitada"],
            name="Energia Aproveitada",
            mode="lines",
            line=dict(color="#16a34a", width=2.5, shape="spline", smoothing=1.2)
        ))

        fig.add_trace(go.Scatter(
            x=chart_df["DataHora"], y=chart_df["Energia_Light_Visual"],
            name="Energia da Rede",
            mode="lines",
            line=dict(color="#9333ea", width=2.5, shape="spline", smoothing=1.2)
        ))

        fig.add_hline(y=0, line_width=2.5, line_color="black")

        fig.update_layout(
            height=520,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            hovermode="x unified",
            font=dict(family="Arial, sans-serif", size=12, color="#1f2937"),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="center", x=0.5,
                bgcolor="rgba(255,255,255,0)",
                font=dict(size=12, color="#1f2937")
            ),
            margin=dict(l=10, r=10, t=60, b=10),
            xaxis=dict(
                title="",
                gridcolor="#cbd5e1",
                showgrid=True,
                tickfont=dict(color="#374151", size=11),
                linecolor="#9ca3af",
                rangeslider=dict(
                    visible=True,
                    thickness=0.08,
                    bgcolor="#f8fafc",
                    bordercolor="#9ca3af",
                    borderwidth=1
                )
            ),
            yaxis=dict(
                title=dict(
                    text="Potência (kW)",
                    font=dict(color="#1f2937", size=13)
                ),
                gridcolor="#cbd5e1",
                tickfont=dict(color="#374151", size=11),
                linecolor="#9ca3af",
                zeroline=False
            )
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # =====================================================
        # CARDS DE RESUMO TOTAL — sempre do CSV inteiro
        # =====================================================

        st.markdown(
            '<div class="section-title">📊 Resultado da Simulação '
            '<span style="font-size:13px; font-weight:400; color:#6b7280;">'
            '(total do período carregado)</span></div>',
            unsafe_allow_html=True
        )

        # Linha 1: Valores de energia
        st.markdown(
            '<div style="font-size:13px; font-weight:600; color:#6b7280; margin-bottom:6px;">'
            '⚡ Energia (kWh / MWh)</div>',
            unsafe_allow_html=True
        )

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(
                summary_box_html(
                    "Energia Importada (Light)",
                    fmt_energia(total_import_full),
                    "#2563eb", "summary-blue",
                    "Total de energia consumida da concessionária"
                ),
                unsafe_allow_html=True
            )
        with r2:
            st.markdown(
                summary_box_html(
                    "Energia Aproveitada",
                    fmt_energia(energia_aproveitada_full),
                    "#16a34a", "summary-green",
                    "Energia fornecida pela UFV efetivamente consumida"
                ),
                unsafe_allow_html=True
            )
        with r3:
            st.markdown(
                summary_box_html(
                    "Energia Cortada",
                    fmt_energia(energia_cortada_full),
                    "#dc2626", "summary-red",
                    "Energia desperdiçada pelo GridZero"
                ),
                unsafe_allow_html=True
            )

        # Linha 2: Indicadores percentuais
        st.markdown(
            '<div style="font-size:13px; font-weight:600; color:#6b7280; margin:14px 0 6px 0;">'
            '📊 Indicadores de Desempenho</div>',
            unsafe_allow_html=True
        )

        fc_color, fc_icon, fc_label = classificar_fator_cobertura(fator_cobertura_full)
        td_color, td_icon, td_label = classificar_taxa_desperdicio(taxa_desperdicio_full)

        if simultaneidade_full >= 80:
            simul_class = "summary-green"
            simul_color = "#16a34a"
            simul_icon = "✅"
            simul_label = "Excelente — Máximo aproveitamento da capacidade de geração."
        elif simultaneidade_full >= 60:
            simul_class = "summary-yellow"
            simul_color = "#ca8a04"
            simul_icon = "🔶"
            simul_label = "Adequado — Bom equilíbrio de uso da usina durante o dia."
        else:
            simul_class = "summary-red"
            simul_color = "#dc2626"
            simul_icon = "⚠️"
            simul_label = "Superdimensionado — Boa parte da capacidade do inversor está ociosa."

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(
                summary_box_html(
                    "Simultaneidade",
                    f"{simultaneidade_full:.1f}%",
                    simul_color, simul_class,
                    f"{simul_icon} {simul_label}",
                    DESC_SIMULTANEIDADE
                ),
                unsafe_allow_html=True
            )
        with s2:
            st.markdown(
                summary_box_html(
                    "Fator de Cobertura",
                    f"{fator_cobertura_full:.1f}%",
                    fc_color, "summary-green",
                    f"{fc_icon} {fc_label}",
                    DESC_FATOR_COBERTURA
                ),
                unsafe_allow_html=True
            )
        with s3:
            st.markdown(
                summary_box_html(
                    "Taxa de Desperdício",
                    f"{taxa_desperdicio_full:.1f}%",
                    td_color, "summary-orange",
                    f"{td_icon} {td_label}",
                    DESC_TAXA_DESPERDICIO
                ),
                unsafe_allow_html=True
            )

        # =====================================================
        # TABELA
        # =====================================================

        st.markdown(
            '<div class="section-title">📋 Dados Operacionais '
            '<span style="font-size:13px; font-weight:400; color:#6b7280;">'
            '(últimos registros do que está sendo exibido)</span></div>',
            unsafe_allow_html=True
        )

        tabela_src = chart_df[chart_df["DataHora"].dt.minute == 0].copy()
        tabela_src["Status"] = tabela_src["Geracao_Cortada"].apply(
            lambda x: "GridZero Ativo" if x > 0 else "Importando"
        )
        tabela_src = tabela_src[[
            "DataHora", "Carga", "Geracao_Limitada",
            "Geracao_Cortada", "Energia_Light", "Status"
        ]].rename(columns={
            "Carga": "Carga (kW)",
            "Geracao_Limitada": "Energia Aproveitada (kW)",
            "Geracao_Cortada": "Geração Cortada (kW)",
            "Energia_Light": "Energia da Rede (kW)"
        })

        st.dataframe(
            tabela_src.tail(20).iloc[::-1],
            use_container_width=True,
            height=320,
            hide_index=True
        )

    with tab_financeira:
        # =====================================================
        # 💰 ANÁLISE FINANCEIRA (GridZero)
        # =====================================================

        st.markdown(
            '<div class="section-title">💰 Análise Financeira '
            '<span style="font-size:13px; font-weight:400; color:#6b7280;">'
            '(viabilidade econômica do projeto em modalidade GridZero)</span></div>',
            unsafe_allow_html=True
        )

        # --- Dimensionar geração anual (estima ano cheio a partir do CSV) ---
        # Pega só pontos originais e calcula soma anualizada
        horas_no_csv = total_horas_full
        if horas_no_csv > 0:
            # Energia anual GridZero = total aproveitado projetado para 1 ano
            geracao_anual_default = energia_aproveitada_full * (8760 / horas_no_csv)
        else:
            geracao_anual_default = 2_525_864  # fallback MELI

        # --- Painel de premissas (expansível) ---
        with st.expander("⚙️ Premissas do Projeto (clique para ajustar)", expanded=False):
            st.markdown(
                '<div style="font-size:12px; color:#6b7280; margin-bottom:10px;">'
                'Valores baseados no projeto MELI/Prologis Dutra II. Ajuste conforme necessário.'
                '</div>',
                unsafe_allow_html=True
            )

            # SISTEMA
            st.markdown("**🔧 Sistema**")
            sys_col1, sys_col2, sys_col3, sys_col4 = st.columns(4)
            with sys_col1:
                capacidade_kwp = st.number_input(
                    "Potência (kWp)",
                    min_value=0.0, value=6315.84, step=10.0, format="%.2f",
                    key="prem_kwp"
                )
            with sys_col2:
                custo_kwp = st.number_input(
                    "Custo (R$/kWp)",
                    min_value=0.0, value=4400.0, step=100.0, format="%.2f",
                    key="prem_custo_kwp"
                )
            with sys_col3:
                vida_util = st.number_input(
                    "Vida útil (anos)",
                    min_value=10, max_value=40, value=30, step=1,
                    key="prem_vida"
                )
            with sys_col4:
                degradacao = st.number_input(
                    "Degradação (% a.a.)",
                    min_value=0.0, max_value=2.0, value=0.35, step=0.05, format="%.2f",
                    key="prem_degradacao"
                ) / 100

            capex_total = capacidade_kwp * custo_kwp
            st.markdown(
                f'<div style="font-size:13px; color:#374151; margin-top:-4px;">'
                f'💵 <b>CAPEX total</b>: {fmt_energia(capex_total).replace(" kWh","").replace(" MWh","")} '
                f'(R$ {capex_total:,.0f})</div>'.replace(",", "."),
                unsafe_allow_html=True
            )

            # GERAÇÃO E TARIFA
            st.markdown("**⚡ Geração e Tarifa**")
            ger_col1, ger_col2, ger_col3 = st.columns(3)
            with ger_col1:
                geracao_anual_kwh = st.number_input(
                    "Geração anual líquida (kWh)",
                    min_value=0.0, value=float(geracao_anual_default), step=1000.0, format="%.0f",
                    help="Estimativa anual a partir do CSV (energia aproveitada projetada para 8.760 h).",
                    key="prem_ger_anual"
                )
            with ger_col2:
                preco_energia = st.number_input(
                    "Preço energia (R$/kWh)",
                    min_value=0.0, value=0.5317, step=0.01, format="%.4f",
                    key="prem_preco"
                )
            with ger_col3:
                ajuste_preco = st.number_input(
                    "Ajuste tarifa (% a.a.)",
                    min_value=0.0, max_value=20.0, value=8.0, step=0.5, format="%.2f",
                    key="prem_ajuste"
                ) / 100

            # DESPESAS OPERACIONAIS
            st.markdown("**🏗️ Despesas Operacionais (anuais)**")
            des_col1, des_col2, des_col3, des_col4 = st.columns(4)
            with des_col1:
                custo_om_por_kwp = st.number_input(
                    "O&M (R$/kWp/ano)",
                    min_value=0.0, value=60.0, step=5.0, format="%.2f",
                    key="prem_om"
                )
            with des_col2:
                custo_arr_por_kwp = st.number_input(
                    "Arrendamento (R$/kWp/ano)",
                    min_value=0.0, value=22.0, step=1.0, format="%.2f",
                    key="prem_arr"
                )
            with des_col3:
                custo_ga_por_kwp = st.number_input(
                    "Rateio G&A (R$/kWp/ano)",
                    min_value=0.0, value=11.0, step=1.0, format="%.2f",
                    key="prem_ga"
                )
            with des_col4:
                seguro_pct = st.number_input(
                    "Seguro (% CAPEX/ano)",
                    min_value=0.0, max_value=5.0, value=0.30, step=0.05, format="%.2f",
                    key="prem_seguro"
                ) / 100

            dem_col1, dem_col2, dem_col3 = st.columns(3)
            with dem_col1:
                demanda_extra_anual = st.number_input(
                    "Demanda adicional (R$/ano)",
                    min_value=0.0, value=353106.0, step=1000.0, format="%.0f",
                    help="Custo adicional de demanda contratada quando a usina exige mais demanda do que o cliente já tem.",
                    key="prem_demanda"
                )
            with dem_col2:
                custo_inversores_pct = st.number_input(
                    "Substituição inversores (% CAPEX)",
                    min_value=0.0, max_value=50.0, value=10.0, step=1.0, format="%.1f",
                    key="prem_inv_pct"
                ) / 100
            with dem_col3:
                ano_substituicao = st.number_input(
                    "Ano de substituição inversores",
                    min_value=0, max_value=30, value=13, step=1,
                    help="0 = nunca substituir.",
                    key="prem_ano_inv"
                )

            # FINANCEIRO
            st.markdown("**📈 Premissas Financeiras**")
            fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
            with fin_col1:
                tma = st.number_input(
                    "TMA (% a.a.)",
                    min_value=0.0, max_value=30.0, value=10.5, step=0.5, format="%.2f",
                    key="prem_tma"
                ) / 100
            with fin_col2:
                inflacao = st.number_input(
                    "Inflação (% a.a.)",
                    min_value=0.0, max_value=20.0, value=6.0, step=0.5, format="%.2f",
                    key="prem_inflacao"
                ) / 100
            with fin_col3:
                juros_aa = st.number_input(
                    "Juros financiamento (% a.a.)",
                    min_value=0.0, max_value=30.0, value=0.0, step=0.5, format="%.2f",
                    help="Zero se não houver financiamento.",
                    key="prem_juros"
                ) / 100
            with fin_col4:
                prazo_financiamento = st.number_input(
                    "Prazo financiamento (anos)",
                    min_value=0, max_value=30, value=0, step=1,
                    key="prem_prazo"
                )

        # --- Calcular fluxo e indicadores ---
        premissas = {
            'vida_util': vida_util,
            'capex_total': capex_total,
            'capacidade_kwp': capacidade_kwp,
            'preco_energia': preco_energia,
            'ajuste_preco': ajuste_preco,
            'inflacao': inflacao,
            'degradacao': degradacao,
            'custo_om_por_kwp': custo_om_por_kwp,
            'custo_arr_por_kwp': custo_arr_por_kwp,
            'custo_ga_por_kwp': custo_ga_por_kwp,
            'seguro_pct': seguro_pct,
            'demanda_extra_anual': demanda_extra_anual,
            'custo_inversores_pct': custo_inversores_pct,
            'ano_substituicao': ano_substituicao,
            'juros_aa': juros_aa,
            'prazo_financiamento': prazo_financiamento,
        }
        fluxo_caixa = calcular_fluxo_caixa(premissas, geracao_anual_kwh)
        indicadores = calcular_indicadores_financeiros(fluxo_caixa, tma)
        lcoe = calcular_lcoe(fluxo_caixa, capex_total, tma)

        # --- Cards de resultado financeiro ---
        st.markdown(
            '<div style="font-size:13px; font-weight:600; color:#6b7280; margin:14px 0 6px 0;">'
            '📊 Indicadores Financeiros</div>',
            unsafe_allow_html=True
        )

        fin1, fin2, fin3, fin4 = st.columns(4)

        with fin1:
            payback = indicadores['payback_anos']
            if payback is None:
                payback_text = f"> {vida_util} anos"
                pb_color, pb_class, pb_diag = "#dc2626", "summary-red", "⚠️ Investimento não se paga na vida útil."
            elif payback < 8:
                payback_text = f"{payback:.1f} anos"
                pb_color, pb_class, pb_diag = "#16a34a", "summary-green", "✅ Excelente — Retorno rápido."
            elif payback < 15:
                payback_text = f"{payback:.1f} anos"
                pb_color, pb_class, pb_diag = "#ca8a04", "summary-yellow", "🔶 Moderado — Retorno em prazo típico."
            else:
                payback_text = f"{payback:.1f} anos"
                pb_color, pb_class, pb_diag = "#dc2626", "summary-red", "⚠️ Longo — Retorno demorado."
            st.markdown(
                summary_box_html(
                    "Payback Simples",
                    payback_text,
                    pb_color, pb_class,
                    pb_diag,
                    "Tempo para o saldo acumulado cruzar zero."
                ),
                unsafe_allow_html=True
            )

        with fin2:
            tir = indicadores['tir']
            if tir is None:
                tir_text = "—"
                tir_color, tir_class, tir_diag = "#64748b", "summary-red", "Não foi possível calcular."
            else:
                tir_text = f"{tir*100:.2f}%"
                if tir >= tma:
                    tir_color, tir_class = "#16a34a", "summary-green"
                    tir_diag = f"✅ Acima da TMA ({tma*100:.1f}%)."
                elif tir >= tma * 0.7:
                    tir_color, tir_class = "#ca8a04", "summary-yellow"
                    tir_diag = f"🔶 Próximo da TMA ({tma*100:.1f}%)."
                else:
                    tir_color, tir_class = "#dc2626", "summary-red"
                    tir_diag = f"⚠️ Abaixo da TMA ({tma*100:.1f}%)."
            st.markdown(
                summary_box_html(
                    "TIR",
                    tir_text,
                    tir_color, tir_class,
                    tir_diag,
                    "Taxa interna de retorno do projeto."
                ),
                unsafe_allow_html=True
            )

        with fin3:
            vpl = indicadores['vpl']
            if vpl >= 0:
                vpl_color, vpl_class, vpl_diag = "#16a34a", "summary-green", "✅ Projeto cria valor."
            else:
                vpl_color, vpl_class, vpl_diag = "#dc2626", "summary-red", "⚠️ Projeto destrói valor."
            vpl_text = fmt_energia(vpl).replace(" kWh", "").replace(" MWh", "")
            # Adicionar prefixo R$
            if abs(vpl) >= 10_000:
                vpl_text_disp = f"R$ {vpl/1_000_000:,.2f} M".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                vpl_text_disp = f"R$ {fmt_int(vpl)}"
            st.markdown(
                summary_box_html(
                    "VPL",
                    vpl_text_disp,
                    vpl_color, vpl_class,
                    vpl_diag,
                    f"Valor presente líquido a TMA de {tma*100:.1f}%."
                ),
                unsafe_allow_html=True
            )

        with fin4:
            if preco_energia > 0:
                economia_pct = (1 - lcoe / preco_energia) * 100
            else:
                economia_pct = 0
            if lcoe < preco_energia * 0.6:
                lcoe_color, lcoe_class, lcoe_diag = "#16a34a", "summary-green", f"✅ {economia_pct:.0f}% mais barato que a tarifa atual."
            elif lcoe < preco_energia:
                lcoe_color, lcoe_class, lcoe_diag = "#ca8a04", "summary-yellow", f"🔶 {economia_pct:.0f}% mais barato que a tarifa atual."
            else:
                lcoe_color, lcoe_class, lcoe_diag = "#dc2626", "summary-red", "⚠️ Mais caro que a tarifa atual."
            st.markdown(
                summary_box_html(
                    "LCOE Solar",
                    f"R$ {lcoe:.4f}/kWh".replace(".", ","),
                    lcoe_color, lcoe_class,
                    lcoe_diag,
                    f"Custo nivelado da energia solar vs R$ {preco_energia:.4f}/kWh da rede.".replace(".", ",")
                ),
                unsafe_allow_html=True
            )

        # --- Gráfico de Payback (saldo acumulado ao longo do tempo) ---
        st.markdown(
            '<div style="font-size:13px; font-weight:600; color:#6b7280; margin:18px 0 6px 0;">'
            '📈 Curva de Payback — Saldo Acumulado</div>',
            unsafe_allow_html=True
        )

        fig_pb = go.Figure()

        # Linha do saldo acumulado
        cores_saldo = [
            "#dc2626" if s < 0 else "#16a34a"
            for s in fluxo_caixa['Saldo_Acumulado']
        ]

        fig_pb.add_trace(go.Scatter(
            x=fluxo_caixa['Ano'],
            y=fluxo_caixa['Saldo_Acumulado'],
            mode='lines+markers',
            name='Saldo Acumulado',
            line=dict(color='#2563eb', width=3),
            marker=dict(size=6, color=cores_saldo, line=dict(width=1, color='#1f2937')),
            fill='tozeroy',
            fillcolor='rgba(37, 99, 235, 0.08)',
            hovertemplate='Ano %{x}<br>Saldo: R$ %{y:,.0f}<extra></extra>'
        ))

        # Linha zero de referência
        fig_pb.add_hline(y=0, line_width=2, line_color='#1f2937', line_dash='solid')

        # Marcação do payback se houver
        if indicadores['payback_anos'] is not None:
            fig_pb.add_vline(
                x=indicadores['payback_anos'],
                line_width=2,
                line_color='#16a34a',
                line_dash='dash',
                annotation_text=f"Payback: {indicadores['payback_anos']:.1f} anos",
                annotation_position="top right",
                annotation_font=dict(color='#16a34a', size=13)
            )

        fig_pb.update_layout(
            height=400,
            template='plotly_white',
            paper_bgcolor='white',
            plot_bgcolor='white',
            hovermode='x unified',
            font=dict(family='Arial, sans-serif', size=12, color='#1f2937'),
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(
                title=dict(text='Ano', font=dict(color='#1f2937', size=13)),
                gridcolor='#cbd5e1',
                tickfont=dict(color='#374151', size=11),
                linecolor='#9ca3af',
                dtick=2
            ),
            yaxis=dict(
                title=dict(text='Saldo Acumulado (R$)', font=dict(color='#1f2937', size=13)),
                gridcolor='#cbd5e1',
                tickfont=dict(color='#374151', size=11),
                linecolor='#9ca3af',
                zeroline=False,
                tickformat=',.0f'
            )
        )

        st.plotly_chart(fig_pb, use_container_width=True, config={'displayModeBar': False})

        # --- Tabela de Fluxo de Caixa Anual ---
        st.markdown(
            '<div style="font-size:13px; font-weight:600; color:#6b7280; margin:18px 0 6px 0;">'
            '📋 Fluxo de Caixa Anual</div>',
            unsafe_allow_html=True
        )

        tabela_fluxo = fluxo_caixa[[
            'Ano', 'Geracao_kWh', 'Faturamento', 'Despesas_Op',
            'Resultado_Liquido', 'Saldo_Acumulado'
        ]].copy()
        tabela_fluxo.columns = [
            'Ano', 'Geração (kWh)', 'Faturamento (R$)', 'Despesas Op. (R$)',
            'Resultado Líquido (R$)', 'Saldo Acumulado (R$)'
        ]

        # Formatar valores numéricos
        def fmt_brl(v):
            if pd.isna(v) or v == 0:
                return "—"
            return f"R$ {v:,.0f}".replace(",", ".")

        tabela_fluxo_disp = tabela_fluxo.copy()
        tabela_fluxo_disp['Geração (kWh)'] = tabela_fluxo_disp['Geração (kWh)'].apply(
            lambda v: f"{v:,.0f}".replace(",", ".") if v > 0 else "—"
        )
        for col in ['Faturamento (R$)', 'Despesas Op. (R$)', 'Resultado Líquido (R$)', 'Saldo Acumulado (R$)']:
            tabela_fluxo_disp[col] = tabela_fluxo_disp[col].apply(fmt_brl)

        st.dataframe(
            tabela_fluxo_disp,
            use_container_width=True,
            height=420,
            hide_index=True
        )

    with tab_simulacao:
        # =====================================================
        # 🔌 SIMULAÇÃO GRIDZERO E PROTEÇÃO
        # =====================================================

        st.markdown(
            '<div class="fin-section-header">'
            '<h2>🔌 Simulação Visual GridZero e Proteção</h2>'
            '<p>Ajuste os valores de <b>Geração</b> e <b>Consumo</b> e veja em tempo real '
            'como o sistema GridZero se comporta. O diagrama mostra o fluxo de energia, '
            'os equipamentos DEIF em ação e as camadas de proteção atuantes.</p>'
            '</div>',
            unsafe_allow_html=True
        )

        # Layout: 2/3 diagrama, 1/3 painel de controle
        col_diagrama, col_controle = st.columns([2.2, 1])

        with col_controle:
            st.markdown(
                '<div class="premissa-group-title">🎛️ Controles</div>',
                unsafe_allow_html=True
            )

            sim_geracao = st.slider(
                "Geração da UFV (kW)",
                min_value=0,
                max_value=6000,
                value=3500,
                step=100,
                help="Potência instantânea sendo gerada pelos 24 inversores SE100K"
            )

            sim_consumo = st.slider(
                "Consumo do Mercado Livre (kW)",
                min_value=0,
                max_value=4000,
                value=2000,
                step=100,
                help="Potência instantânea consumida pelo galpão Prologis Dutra II"
            )

            st.markdown("---")

            # Classificação do cenário
            corte_kw = max(0, sim_geracao - sim_consumo)
            geracao_efetiva = min(sim_geracao, sim_consumo)
            energia_rede = max(0, sim_consumo - sim_geracao)

            if sim_geracao == 0:
                cenario_nome = "Sem Geração Solar"
                cenario_cor = "#64748b"
                cenario_icone = "🌙"
                cenario_desc = "Apenas a rede da Light atende a carga."
            elif sim_geracao <= sim_consumo:
                cenario_nome = "Operação Normal"
                cenario_cor = "#16a34a"
                cenario_icone = "✅"
                cenario_desc = "A geração é totalmente consumida. GridZero em standby."
            else:
                cenario_nome = "GridZero Ativo"
                cenario_cor = "#f97316"
                cenario_icone = "🛡️"
                cenario_desc = f"Excesso de {corte_kw} kW está sendo cortado pelo controle."

            # Card de cenário
            st.markdown(
                f"""<div style="background:white; border-left:4px solid {cenario_cor};
                border-radius:10px; padding:14px 16px; box-shadow:0 1px 4px rgba(0,0,0,0.05);
                margin-bottom:12px;">
                <div style="font-size:11px; color:#6b7280; font-weight:600; letter-spacing:0.04em;
                text-transform:uppercase;">Cenário Detectado</div>
                <div style="font-size:18px; font-weight:700; color:{cenario_cor}; margin-top:4px;">
                {cenario_icone} {cenario_nome}</div>
                <div style="font-size:12px; color:#374151; margin-top:6px; line-height:1.4;">
                {cenario_desc}</div></div>""",
                unsafe_allow_html=True
            )

            # KPIs instantâneos
            st.markdown(
                '<div class="premissa-group-title" style="margin-top:14px;">⚡ KPIs Instantâneos</div>',
                unsafe_allow_html=True
            )

            def mini_kpi(label, valor, cor):
                return f"""<div style="background:white; border-radius:8px; padding:10px 12px;
                margin-bottom:6px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:12px; color:#6b7280; font-weight:500;">{label}</span>
                    <span style="font-size:16px; font-weight:700; color:{cor};">{valor}</span>
                </div></div>"""

            st.markdown(
                mini_kpi("Consumo do cliente", f"{sim_consumo:,} kW".replace(",", "."), "#2563eb"),
                unsafe_allow_html=True
            )
            st.markdown(
                mini_kpi("Geração entregue", f"{geracao_efetiva:,} kW".replace(",", "."), "#16a34a"),
                unsafe_allow_html=True
            )
            st.markdown(
                mini_kpi("Geração cortada", f"{corte_kw:,} kW".replace(",", "."), "#f97316"),
                unsafe_allow_html=True
            )
            st.markdown(
                mini_kpi("Energia da Rede", f"{energia_rede:,} kW".replace(",", "."), "#9333ea"),
                unsafe_allow_html=True
            )

            # Estado das camadas de proteção
            st.markdown(
                '<div class="premissa-group-title" style="margin-top:14px;">🛡️ Camadas de Proteção</div>',
                unsafe_allow_html=True
            )

            # Camada 0: controle DEIF (ativa quando há geração)
            # Camada 1: ANSI 32 do AGC-150 (standby — só atua em falha de controle)
            # Camada 2: Relé auxiliar (standby)
            # Camada 3: 7SR1004 no PMT (standby)
            c0_ativo = sim_geracao > 0
            c0_cor = "#16a34a" if c0_ativo else "#9ca3af"
            c0_status = "ATIVO" if c0_ativo else "standby"

            def camada_row(num, nome, descricao, status, cor):
                bg_cor = "#f0fdf4" if cor == "#16a34a" else "#f9fafb"
                return f"""<div style="background:{bg_cor}; border-left:3px solid {cor};
                border-radius:6px; padding:8px 10px; margin-bottom:5px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:12px; font-weight:700; color:#1f2937;">Camada {num}</span>
                        <span style="font-size:11px; color:#6b7280; margin-left:4px;">— {nome}</span>
                    </div>
                    <span style="font-size:10px; font-weight:700; color:{cor}; letter-spacing:0.05em;">
                    {status}</span>
                </div>
                <div style="font-size:10px; color:#6b7280; margin-top:2px; line-height:1.3;">{descricao}</div>
                </div>"""

            st.markdown(camada_row(
                "0", "Controle DEIF (laço fechado)",
                "AGC-150 lê potência e envia setpoint aos ASCs",
                c0_status, c0_cor
            ), unsafe_allow_html=True)

            st.markdown(camada_row(
                "1", "ANSI 32 do AGC-150",
                "Atua nos disjuntores BT em 2–3 s",
                "standby", "#9ca3af"
            ), unsafe_allow_html=True)

            st.markdown(camada_row(
                "2", "Relé auxiliar ANSI 32",
                "Atua nos disjuntores BT em 5–7 s",
                "standby", "#9ca3af"
            ), unsafe_allow_html=True)

            st.markdown(camada_row(
                "3", "Siemens 7SR1004 (MT)",
                "Abre disjuntor de MT do PMT em 8–10 s",
                "standby", "#9ca3af"
            ), unsafe_allow_html=True)

        with col_diagrama:
            # =====================================================
            # SVG DO DIAGRAMA
            # =====================================================

            # Parâmetros visuais baseados no cenário
            gridzero_ativo = cenario_nome == "GridZero Ativo"

            # Cor da linha de "corte" — laranja se houver corte, transparente se não
            cor_corte = "#f97316" if corte_kw > 0 else "#cbd5e1"

            # Espessura das setas proporcional ao fluxo (mín 2, máx 8)
            def espessura(potencia_kw, max_potencia=6000):
                if potencia_kw <= 0:
                    return 1
                return 2 + min(6, (potencia_kw / max_potencia) * 6)

            esp_consumo = espessura(sim_consumo)
            esp_geracao = espessura(geracao_efetiva)
            esp_rede = espessura(energia_rede)
            esp_corte = espessura(corte_kw)

            # Cores e estados
            cor_seta_rede = "#9333ea" if energia_rede > 0 else "#cbd5e1"
            cor_seta_solar = "#16a34a" if geracao_efetiva > 0 else "#cbd5e1"
            cor_agc_ativo = "#16a34a" if c0_ativo else "#9ca3af"

            # Opacidade dos inversores conforme corte
            # Se há corte, mostra que estão "limitados" (semi-transparente no topo)
            opacidade_inv = 1.0
            if gridzero_ativo and sim_geracao > 0:
                # Quão limitados estão os inversores
                pct_geracao = geracao_efetiva / sim_geracao if sim_geracao > 0 else 0
                opacidade_inv = max(0.4, pct_geracao)

            svg = f"""
<svg viewBox="0 0 1200 1000" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:auto; background:#fafbfc; border-radius:14px;">
  <defs>
    <marker id="arrow-rede" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{cor_seta_rede}"/>
    </marker>
    <marker id="arrow-solar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{cor_seta_solar}"/>
    </marker>
    <marker id="arrow-control" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{cor_agc_ativo}"/>
    </marker>
    <style>
      .box-titulo {{ font: 600 12px Arial; fill: #1f2937; }}
      .box-sub {{ font: 11px Arial; fill: #6b7280; }}
      .label-fluxo {{ font: 700 11px Arial; }}
      .label-comm {{ font: italic 10px Arial; fill: #6b7280; }}
      .cabo-comando {{ stroke: #92400e; stroke-width: 3; fill: none; opacity: 0.85; }}
    </style>
  </defs>

  <text x="600" y="22" text-anchor="middle" font-family="Arial" font-size="14" font-weight="700" fill="#1f2937">
    Arquitetura GridZero — Prologis Dutra II
  </text>

  <!-- 1. REDE LIGHT -->
  <rect x="520" y="40" width="160" height="40" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
  <text x="600" y="58" text-anchor="middle" class="box-titulo">⚡ REDE LIGHT</text>
  <text x="600" y="73" text-anchor="middle" class="box-sub">13,8 kV — 60 Hz</text>

  <line x1="600" y1="80" x2="600" y2="110" stroke="{cor_seta_rede}" stroke-width="{esp_rede}" marker-end="url(#arrow-rede)"/>
  <text x="615" y="98" class="label-fluxo" fill="{cor_seta_rede}">{energia_rede:,} kW</text>

  <!-- 2. CABINE PRIMÁRIA -->
  <rect x="495" y="115" width="210" height="48" rx="8" fill="#ffffff" stroke="#374151" stroke-width="1.5"/>
  <text x="600" y="133" text-anchor="middle" class="box-titulo">🏢 Cabine Primária Light</text>
  <text x="600" y="150" text-anchor="middle" class="box-sub">Relé Siemens 7SR1002 (50/51/50N/51N)</text>

  <line x1="600" y1="163" x2="600" y2="195" stroke="{cor_seta_rede}" stroke-width="{esp_rede}" marker-end="url(#arrow-rede)"/>

  <!-- 3. PMT-02-G200 -->
  <rect x="370" y="200" width="460" height="160" rx="10" fill="#fefce8" stroke="#ca8a04" stroke-width="2" stroke-dasharray="4,3"/>
  <text x="600" y="220" text-anchor="middle" font-family="Arial" font-size="13" font-weight="700" fill="#854d0e">
    🏭 PMT-02-G200 (Sala de PMT — Mercado Livre)
  </text>

  <rect x="555" y="234" width="90" height="32" rx="6" fill="white" stroke="#dc2626" stroke-width="1.5"/>
  <text x="600" y="248" text-anchor="middle" font-family="Arial" font-size="10" font-weight="700" fill="#dc2626">DJ-MT 13,8 kV</text>
  <text x="600" y="260" text-anchor="middle" font-family="Arial" font-size="9" fill="#6b7280">Fechado</text>

  <rect x="390" y="285" width="180" height="58" rx="8" fill="white" stroke="#9ca3af" stroke-width="1.5"/>
  <text x="480" y="302" text-anchor="middle" class="box-titulo">⚙️ Relé Siemens 7SR1004</text>
  <text x="480" y="318" text-anchor="middle" class="box-sub">ANSI 32 + 67</text>
  <text x="480" y="332" text-anchor="middle" font-family="Arial" font-size="10" font-weight="600" fill="#9ca3af">CAMADA 3 — standby</text>

  <rect x="630" y="285" width="180" height="58" rx="8" fill="white" stroke="{cor_agc_ativo}" stroke-width="2"/>
  <text x="720" y="302" text-anchor="middle" class="box-titulo">🧠 DEIF AGC-150 MAINS</text>
  <text x="720" y="318" text-anchor="middle" class="box-sub">TCs/TPs + ANSI 32</text>
  <text x="720" y="332" text-anchor="middle" font-family="Arial" font-size="10" font-weight="700" fill="{cor_agc_ativo}">CAMADA 0 — {c0_status}</text>

  <!-- Cabo de comando 7SR1004 → DJ-MT (Camada 3 atua no DJ-MT) -->
  <path d="M 480 285 Q 480 270 555 250" class="cabo-comando"/>

  <!-- Saída do PMT vai pro barramento MT -->
  <line x1="600" y1="360" x2="600" y2="395" stroke="{cor_seta_rede if energia_rede > 0 else '#cbd5e1'}" stroke-width="{max(esp_rede, esp_consumo)}" marker-end="url(#arrow-rede)"/>

  <!-- BARRAMENTO MT (13,8 kV) -->
  <line x1="120" y1="395" x2="1080" y2="395" stroke="#1f2937" stroke-width="3"/>
  <line x1="220" y1="395" x2="220" y2="420" stroke="#1f2937" stroke-width="2"/>
  <line x1="600" y1="395" x2="600" y2="420" stroke="#1f2937" stroke-width="2"/>
  <line x1="980" y1="395" x2="980" y2="420" stroke="#1f2937" stroke-width="2"/>

  <!-- ============== RAMO 1: TR-05 (centro x=220) ============== -->
  <rect x="150" y="425" width="140" height="50" rx="6" fill="#f0f9ff" stroke="#0284c7" stroke-width="1.5"/>
  <text x="220" y="443" text-anchor="middle" class="box-titulo">TR-05-G200</text>
  <text x="220" y="459" text-anchor="middle" class="box-sub">500 kVA — 13,8/0,38 kV</text>
  <text x="220" y="471" text-anchor="middle" font-family="Arial" font-size="9" fill="#6b7280">4 inversores</text>

  <!-- Saída do trafo até barramento BT -->
  <line x1="220" y1="475" x2="220" y2="525" stroke="#1f2937" stroke-width="2"/>
  <!-- Barramento BT horizontal -->
  <line x1="160" y1="525" x2="280" y2="525" stroke="#1f2937" stroke-width="2.5"/>

  <!-- DJ BT UFV (esquerda) - atua -->
  <line x1="170" y1="525" x2="170" y2="555" stroke="#1f2937" stroke-width="2"/>
  <rect x="130" y="555" width="80" height="28" rx="6" fill="white" stroke="#dc2626" stroke-width="1.8"/>
  <text x="170" y="568" text-anchor="middle" font-family="Arial" font-size="10" font-style="italic" font-weight="700" fill="#dc2626">DJ BT - UFV</text>
  <text x="170" y="579" text-anchor="middle" font-family="Arial" font-size="8" fill="#6b7280">Fechado</text>

  <!-- DJ BT Carga (direita) - representação apenas -->
  <line x1="270" y1="525" x2="270" y2="555" stroke="#1f2937" stroke-width="2"/>
  <rect x="230" y="555" width="80" height="28" rx="6" fill="white" stroke="#374151" stroke-width="1.2"/>
  <text x="270" y="568" text-anchor="middle" font-family="Arial" font-size="10" font-style="italic" fill="#374151">DJ BT</text>
  <text x="270" y="579" text-anchor="middle" font-family="Arial" font-size="9" font-style="italic" fill="#374151">CARGA</text>

  <!-- Inversores TR-05 (abaixo do DJ BT UFV) -->
  <line x1="170" y1="583" x2="170" y2="610" stroke="#1f2937" stroke-width="2"/>
  <rect x="115" y="610" width="110" height="50" rx="6" fill="#fff7ed" stroke="#f97316" stroke-width="1.5" opacity="{opacidade_inv}"/>
  <text x="170" y="628" text-anchor="middle" class="box-titulo" opacity="{opacidade_inv}">☀️ 4× SE100K</text>
  <text x="170" y="643" text-anchor="middle" class="box-sub" opacity="{opacidade_inv}">SolarEdge</text>
  <text x="170" y="655" text-anchor="middle" font-family="Arial" font-size="9" font-weight="600" fill="#f97316" opacity="{opacidade_inv}">{int(geracao_efetiva * 0.125):,} kW</text>

  <!-- Carga TR-05 (abaixo do DJ BT Carga) -->
  <line x1="270" y1="583" x2="270" y2="610" stroke="#1f2937" stroke-width="2"/>
  <rect x="220" y="610" width="100" height="50" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
  <text x="270" y="633" text-anchor="middle" class="box-titulo" fill="#1d4ed8">🏢 CARGA</text>
  <text x="270" y="649" text-anchor="middle" class="box-sub">TR-05</text>

  <!-- ASC-150 #1 -->
  <rect x="115" y="725" width="110" height="42" rx="6" fill="white" stroke="{cor_agc_ativo}" stroke-width="1.5"/>
  <text x="170" y="741" text-anchor="middle" class="box-titulo">DEIF ASC-150 #1</text>
  <text x="170" y="755" text-anchor="middle" class="box-sub">Solar Plant Ctrl.</text>

  <!-- Modbus ASC#1 ↔ Inversores -->
  <line x1="170" y1="725" x2="170" y2="660" stroke="{cor_agc_ativo}" stroke-width="1.2" stroke-dasharray="2,2"/>
  <text x="178" y="700" font-family="Arial" font-size="8" fill="{cor_agc_ativo}">Modbus</text>

  <!-- CABO DE COMANDO ASC#1 → DJ BT UFV #1 -->
  <path d="M 115 730 Q 70 700 70 555 Q 70 540 130 555" class="cabo-comando"/>

  <!-- ============== RAMO 2: TR-07 (centro x=600) ============== -->
  <rect x="530" y="425" width="140" height="50" rx="6" fill="#f0f9ff" stroke="#0284c7" stroke-width="1.5"/>
  <text x="600" y="443" text-anchor="middle" class="box-titulo">TR-07-CAG</text>
  <text x="600" y="459" text-anchor="middle" class="box-sub">2.000 kVA — 13,8/0,38 kV</text>
  <text x="600" y="471" text-anchor="middle" font-family="Arial" font-size="9" fill="#6b7280">16 inversores</text>

  <line x1="600" y1="475" x2="600" y2="525" stroke="#1f2937" stroke-width="2"/>
  <line x1="540" y1="525" x2="660" y2="525" stroke="#1f2937" stroke-width="2.5"/>

  <line x1="550" y1="525" x2="550" y2="555" stroke="#1f2937" stroke-width="2"/>
  <rect x="510" y="555" width="80" height="28" rx="6" fill="white" stroke="#dc2626" stroke-width="1.8"/>
  <text x="550" y="568" text-anchor="middle" font-family="Arial" font-size="10" font-style="italic" font-weight="700" fill="#dc2626">DJ BT - UFV</text>
  <text x="550" y="579" text-anchor="middle" font-family="Arial" font-size="8" fill="#6b7280">Fechado</text>

  <line x1="650" y1="525" x2="650" y2="555" stroke="#1f2937" stroke-width="2"/>
  <rect x="610" y="555" width="80" height="28" rx="6" fill="white" stroke="#374151" stroke-width="1.2"/>
  <text x="650" y="568" text-anchor="middle" font-family="Arial" font-size="10" font-style="italic" fill="#374151">DJ BT</text>
  <text x="650" y="579" text-anchor="middle" font-family="Arial" font-size="9" font-style="italic" fill="#374151">CARGA</text>

  <line x1="550" y1="583" x2="550" y2="610" stroke="#1f2937" stroke-width="2"/>
  <rect x="495" y="610" width="110" height="50" rx="6" fill="#fff7ed" stroke="#f97316" stroke-width="1.5" opacity="{opacidade_inv}"/>
  <text x="550" y="628" text-anchor="middle" class="box-titulo" opacity="{opacidade_inv}">☀️ 16× SE100K</text>
  <text x="550" y="643" text-anchor="middle" class="box-sub" opacity="{opacidade_inv}">SolarEdge</text>
  <text x="550" y="655" text-anchor="middle" font-family="Arial" font-size="9" font-weight="600" fill="#f97316" opacity="{opacidade_inv}">{int(geracao_efetiva * 0.667):,} kW</text>

  <line x1="650" y1="583" x2="650" y2="610" stroke="#1f2937" stroke-width="2"/>
  <rect x="600" y="610" width="100" height="50" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
  <text x="650" y="633" text-anchor="middle" class="box-titulo" fill="#1d4ed8">🏢 CARGA</text>
  <text x="650" y="649" text-anchor="middle" class="box-sub">TR-07</text>

  <rect x="495" y="725" width="110" height="42" rx="6" fill="white" stroke="{cor_agc_ativo}" stroke-width="1.5"/>
  <text x="550" y="741" text-anchor="middle" class="box-titulo">DEIF ASC-150 #2</text>
  <text x="550" y="755" text-anchor="middle" class="box-sub">Solar Plant Ctrl.</text>

  <line x1="550" y1="725" x2="550" y2="660" stroke="{cor_agc_ativo}" stroke-width="1.2" stroke-dasharray="2,2"/>
  <text x="558" y="700" font-family="Arial" font-size="8" fill="{cor_agc_ativo}">Modbus</text>

  <!-- CABO DE COMANDO ASC#2 → DJ BT UFV #2 -->
  <path d="M 495 730 Q 460 700 460 555 Q 460 540 510 555" class="cabo-comando"/>

  <!-- ============== RAMO 3: TR-08 (centro x=980) ============== -->
  <rect x="910" y="425" width="140" height="50" rx="6" fill="#f0f9ff" stroke="#0284c7" stroke-width="1.5"/>
  <text x="980" y="443" text-anchor="middle" class="box-titulo">TR-08-G200</text>
  <text x="980" y="459" text-anchor="middle" class="box-sub">750 kVA — 13,8/0,38 kV</text>
  <text x="980" y="471" text-anchor="middle" font-family="Arial" font-size="9" fill="#6b7280">4 inversores</text>

  <line x1="980" y1="475" x2="980" y2="525" stroke="#1f2937" stroke-width="2"/>
  <line x1="920" y1="525" x2="1040" y2="525" stroke="#1f2937" stroke-width="2.5"/>

  <line x1="930" y1="525" x2="930" y2="555" stroke="#1f2937" stroke-width="2"/>
  <rect x="890" y="555" width="80" height="28" rx="6" fill="white" stroke="#dc2626" stroke-width="1.8"/>
  <text x="930" y="568" text-anchor="middle" font-family="Arial" font-size="10" font-style="italic" font-weight="700" fill="#dc2626">DJ BT - UFV</text>
  <text x="930" y="579" text-anchor="middle" font-family="Arial" font-size="8" fill="#6b7280">Fechado</text>

  <line x1="1030" y1="525" x2="1030" y2="555" stroke="#1f2937" stroke-width="2"/>
  <rect x="990" y="555" width="80" height="28" rx="6" fill="white" stroke="#374151" stroke-width="1.2"/>
  <text x="1030" y="568" text-anchor="middle" font-family="Arial" font-size="10" font-style="italic" fill="#374151">DJ BT</text>
  <text x="1030" y="579" text-anchor="middle" font-family="Arial" font-size="9" font-style="italic" fill="#374151">CARGA</text>

  <line x1="930" y1="583" x2="930" y2="610" stroke="#1f2937" stroke-width="2"/>
  <rect x="875" y="610" width="110" height="50" rx="6" fill="#fff7ed" stroke="#f97316" stroke-width="1.5" opacity="{opacidade_inv}"/>
  <text x="930" y="628" text-anchor="middle" class="box-titulo" opacity="{opacidade_inv}">☀️ 4× SE100K</text>
  <text x="930" y="643" text-anchor="middle" class="box-sub" opacity="{opacidade_inv}">SolarEdge</text>
  <text x="930" y="655" text-anchor="middle" font-family="Arial" font-size="9" font-weight="600" fill="#f97316" opacity="{opacidade_inv}">{int(geracao_efetiva * 0.208):,} kW</text>

  <line x1="1030" y1="583" x2="1030" y2="610" stroke="#1f2937" stroke-width="2"/>
  <rect x="980" y="610" width="100" height="50" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
  <text x="1030" y="633" text-anchor="middle" class="box-titulo" fill="#1d4ed8">🏢 CARGA</text>
  <text x="1030" y="649" text-anchor="middle" class="box-sub">TR-08</text>

  <rect x="875" y="725" width="110" height="42" rx="6" fill="white" stroke="{cor_agc_ativo}" stroke-width="1.5"/>
  <text x="930" y="741" text-anchor="middle" class="box-titulo">DEIF ASC-150 #3</text>
  <text x="930" y="755" text-anchor="middle" class="box-sub">Solar Plant Ctrl.</text>

  <line x1="930" y1="725" x2="930" y2="660" stroke="{cor_agc_ativo}" stroke-width="1.2" stroke-dasharray="2,2"/>
  <text x="938" y="700" font-family="Arial" font-size="8" fill="{cor_agc_ativo}">Modbus</text>

  <!-- CABO DE COMANDO ASC#3 → DJ BT UFV #3 -->
  <path d="M 875 730 Q 840 700 840 555 Q 840 540 890 555" class="cabo-comando"/>

  <!-- ============== COMUNICAÇÃO DEIF (fibra) ============== -->
  <!-- Bus inferior conectando os 3 ASCs -->
  <line x1="170" y1="800" x2="930" y2="800" stroke="{cor_agc_ativo}" stroke-width="1.8" stroke-dasharray="4,3" opacity="0.85"/>
  <line x1="170" y1="767" x2="170" y2="800" stroke="{cor_agc_ativo}" stroke-width="1.8" stroke-dasharray="4,3" opacity="0.85"/>
  <line x1="550" y1="767" x2="550" y2="800" stroke="{cor_agc_ativo}" stroke-width="1.8" stroke-dasharray="4,3" opacity="0.85"/>
  <line x1="930" y1="767" x2="930" y2="800" stroke="{cor_agc_ativo}" stroke-width="1.8" stroke-dasharray="4,3" opacity="0.85"/>

  <!-- AGC → bus de comunicação -->
  <path d="M 720 343 Q 720 700 550 800" stroke="{cor_agc_ativo}" stroke-width="1.8" stroke-dasharray="4,3" fill="none" opacity="0.85"/>
  <text x="730" y="700" class="label-comm" fill="{cor_agc_ativo}">📡 Fibra óptica DEIF (setpoint)</text>

  <!-- Setas de fluxo solar → barramento BT -->
  <line x1="150" y1="610" x2="150" y2="535" stroke="{cor_seta_solar}" stroke-width="{esp_geracao}" marker-start="url(#arrow-solar)" opacity="{0.9 if geracao_efetiva > 0 else 0.2}"/>
  <line x1="530" y1="610" x2="530" y2="535" stroke="{cor_seta_solar}" stroke-width="{esp_geracao}" marker-start="url(#arrow-solar)" opacity="{0.9 if geracao_efetiva > 0 else 0.2}"/>
  <line x1="910" y1="610" x2="910" y2="535" stroke="{cor_seta_solar}" stroke-width="{esp_geracao}" marker-start="url(#arrow-solar)" opacity="{0.9 if geracao_efetiva > 0 else 0.2}"/>

  <!-- LEGENDA -->
  <g transform="translate(40, 860)">
    <rect x="0" y="0" width="14" height="3" fill="#9333ea"/>
    <text x="20" y="4" font-family="Arial" font-size="10" fill="#374151">Rede Light → Carga</text>
    <rect x="180" y="0" width="14" height="3" fill="#16a34a"/>
    <text x="200" y="4" font-family="Arial" font-size="10" fill="#374151">Solar → Carga</text>
    <line x1="320" y1="2" x2="334" y2="2" stroke="{cor_agc_ativo}" stroke-width="2" stroke-dasharray="3,2"/>
    <text x="342" y="4" font-family="Arial" font-size="10" fill="#374151">Comunicação DEIF</text>
    <line x1="490" y1="2" x2="504" y2="2" stroke="#92400e" stroke-width="3"/>
    <text x="512" y="4" font-family="Arial" font-size="10" fill="#374151">Cabo de comando (trip)</text>
    <rect x="700" y="-3" width="10" height="10" rx="2" fill="white" stroke="#dc2626" stroke-width="1"/>
    <text x="715" y="4" font-family="Arial" font-size="10" fill="#374151">Disjuntor</text>
  </g>

  {f'<g><rect x="480" y="890" width="240" height="26" rx="13" fill="white" stroke="#f97316" stroke-width="2"/><text x="600" y="908" text-anchor="middle" font-family="Arial" font-size="11" font-weight="700" fill="#c2410c">⚠️ Corte ativo: {corte_kw:,} kW desperdiçados</text></g>' if corte_kw > 0 else ''}
</svg>
            """

            # Renderiza o SVG via components.html para evitar que o markdown
            # interprete linhas indentadas como bloco de código.
            # O wrapper HTML aplica um padding leve e remove margins do iframe.
            html_wrapper = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin: 0; padding: 0; background: transparent; }}
  svg {{ display: block; width: 100%; height: auto; }}
</style>
</head>
<body>
{svg}
</body>
</html>
"""
            components.html(html_wrapper, height=1000, scrolling=False)

        # Cards informativos abaixo do diagrama
        st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.markdown(
                f"""<div style="background:#eff6ff; border-radius:10px; padding:14px 16px;
                border-left:4px solid #2563eb;">
                <div style="font-size:12px; color:#6b7280; font-weight:600;">Modo Atual</div>
                <div style="font-size:16px; color:#1d4ed8; font-weight:700; margin-top:4px;">
                {cenario_icone} {cenario_nome}</div>
                <div style="font-size:12px; color:#374151; margin-top:6px; line-height:1.4;">
                {cenario_desc}</div>
                </div>""",
                unsafe_allow_html=True
            )

        with info_col2:
            if gridzero_ativo:
                pct_uso = (geracao_efetiva / sim_geracao * 100) if sim_geracao > 0 else 0
                msg = f"Inversores entregando <b>{pct_uso:.1f}%</b> da capacidade. AGC-150 reduziu o setpoint via Modbus broadcast."
                cor_box = "#fff7ed"
                cor_bar = "#f97316"
                titulo = "🛡️ GridZero em ação"
            elif sim_geracao > 0:
                msg = "Inversores entregando <b>100%</b> da capacidade. AGC-150 monitora mas não precisa atuar."
                cor_box = "#f0fdf4"
                cor_bar = "#16a34a"
                titulo = "✅ Sem necessidade de corte"
            else:
                msg = "Sem geração solar. Apenas a rede da Light alimenta a carga."
                cor_box = "#f9fafb"
                cor_bar = "#9ca3af"
                titulo = "🌙 Sem geração"

            st.markdown(
                f"""<div style="background:{cor_box}; border-radius:10px; padding:14px 16px;
                border-left:4px solid {cor_bar};">
                <div style="font-size:12px; color:#6b7280; font-weight:600;">Comportamento dos Inversores</div>
                <div style="font-size:14px; color:#1f2937; font-weight:700; margin-top:4px;">{titulo}</div>
                <div style="font-size:12px; color:#374151; margin-top:6px; line-height:1.4;">{msg}</div>
                </div>""",
                unsafe_allow_html=True
            )

        with info_col3:
            if gridzero_ativo:
                msg = (
                    f"O AGC-150 detectou potencial exportação de <b>{corte_kw} kW</b>. "
                    f"Comando enviado em &lt;500 ms aos 3 ASC-150 via fibra óptica. "
                    f"Reação dos inversores: &lt;1 s."
                )
                cor_box = "#fffbeb"
                cor_bar = "#ca8a04"
                titulo = "⚡ Controle Atuando"
            else:
                msg = (
                    "Sistema em monitoramento. Camadas 1, 2 e 3 permanecem em standby — "
                    "só atuam se o controle do AGC-150 falhar em interromper exportação."
                )
                cor_box = "#f9fafb"
                cor_bar = "#9ca3af"
                titulo = "💤 Proteções em standby"

            st.markdown(
                f"""<div style="background:{cor_box}; border-radius:10px; padding:14px 16px;
                border-left:4px solid {cor_bar};">
                <div style="font-size:12px; color:#6b7280; font-weight:600;">Cadeia de Controle</div>
                <div style="font-size:14px; color:#1f2937; font-weight:700; margin-top:4px;">{titulo}</div>
                <div style="font-size:12px; color:#374151; margin-top:6px; line-height:1.4;">{msg}</div>
                </div>""",
                unsafe_allow_html=True
            )

        # Nota sobre futuras expansões
        st.markdown(
            """<div style="background:#f0f9ff; border:1px dashed #93c5fd; border-radius:10px;
            padding:12px 16px; margin-top:18px;">
            <div style="font-size:12px; color:#1e40af; font-weight:600;">📌 Próximas evoluções desta tela</div>
            <div style="font-size:12px; color:#374151; margin-top:4px; line-height:1.5;">
            • Animação play/pause com sequência temporal (medição → decisão → comando → reação)<br>
            • Cenário de <b>Falha de comunicação</b> AGC↔ASC com atuação da Camada 1 nos disjuntores BT<br>
            • Cenário de <b>Exportação sustentada</b> com atuação das Camadas 2 e 3 em sequência<br>
            • Indicadores temporais (tempo desde a detecção, status de cada camada ao longo do tempo)
            </div></div>""",
            unsafe_allow_html=True
        )

    # =====================================================
    # AUTO PLAY — somente no modo Replay
    # =====================================================

    if (
        modo == "Replay"
        and st.session_state.run_simulation
        and st.session_state.index < len(df) - 1
    ):
        time.sleep(speed)
        st.session_state.index += 1
        st.rerun()

else:
    st.info(
        "📂 Faça o upload dos arquivos **geracao.csv** e **consumo.csv** "
        "na barra lateral para iniciar."
    )
