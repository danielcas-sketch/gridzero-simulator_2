import streamlit as st
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
    tab_operacional, tab_financeira = st.tabs([
        "📊  Análise Operacional",
        "💰  Análise Financeira"
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
