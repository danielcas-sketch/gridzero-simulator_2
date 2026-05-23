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


def kpi_card_html(title, value, color, sub="", sparkline_html=""):
    """Card KPI com sub-texto opcional e sparkline."""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-title" style="color:{color}">{title}</div>
            <div class="kpi-value" style="color:{color}">{value}</div>
            {sub_html}
        </div>
        <div class="kpi-spark">{sparkline_html}</div>
    </div>
    """


def summary_box_html(title, value, color, cls, sub=""):
    return f"""
    <div class="summary-box {cls}">
        <div class="summary-title" style="color:{color}">{title}</div>
        <div class="summary-value" style="color:{color}">{value}</div>
        <div class="summary-sub">{sub}</div>
    </div>
    """


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


def classificar_fator_cobertura(pct):
    """Retorna (cor, icone, texto_diagnostico) para o Fator de Cobertura."""
    if pct < 25:
        return ("#dc2626", "⚠️", "Fração pequena — típico de indústrias 24/7 ou perfil noturno")
    elif pct < 30:
        return ("#f97316", "⚡", "Cobertura baixa — maior parte da energia vem da concessionária")
    elif pct < 45:
        return ("#ca8a04", "🔶", "Padrão comum — residências e perfis mistos com picos fora do sol")
    elif pct < 50:
        return ("#65a30d", "🔷", "Boa cobertura — próximo do teto típico do Grid Zero")
    elif pct <= 65:
        return ("#16a34a", "✅", "Excelente — típico de comércios e indústrias de turno único")
    else:
        return ("#7c3aed", "🔬", "Acima do teto físico — revise os dados de carga")


def classificar_taxa_desperdicio(pct):
    """Retorna (cor, icone, texto_diagnostico) para a Taxa de Desperdício."""
    if pct < 10:
        return ("#16a34a", "✅", "Excelente — usina muito bem dimensionada")
    elif pct <= 20:
        return ("#65a30d", "🔷", "Aceitável — curtailment dentro da faixa econômica viável")
    elif pct <= 30:
        return ("#ca8a04", "🔶", "Atenção — payback pode ser prejudicado")
    elif pct <= 40:
        return ("#f97316", "⚡", "Alerta — LCOE elevado, viabilidade comprometida")
    else:
        return ("#dc2626", "⚠️", "Crítico — capacidade instalada gerando pouca economia")


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


@st.cache_data(show_spinner=False)
def estatisticas_totais(df_hash_key):
    """Estatísticas do CSV inteiro — usadas nos cards inferiores fixos.
    Recebe um hash key pra invalidar cache quando os dados mudam,
    e pega o df de session_state.
    """
    df = st.session_state.df_processado
    df_real = df[~df["DataHora"].isin([])]  # placeholder, df inteiro

    total_import = df_real[df_real["Energia_Light"] > 0]["Energia_Light"].sum()
    energia_cortada = df_real["Geracao_Cortada"].sum()
    max_corte = df_real["Geracao_Cortada"].max() if len(df_real) else 0
    horas_corte = (df_real["Geracao_Cortada"] > 0).sum()
    horas_originais = len(df_real[df_real["DataHora"].dt.minute == 0]) if "DataHora" in df_real.columns else len(df_real)

    return {
        "total_import": total_import,
        "energia_cortada": energia_cortada,
        "max_corte": max_corte,
        "horas_corte": horas_corte,
        "horas_originais": horas_originais,
    }


# =========================================================
# SESSION STATE
# =========================================================

if "index" not in st.session_state:
    st.session_state.index = 0
if "run_simulation" not in st.session_state:
    st.session_state.run_simulation = False
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Intervalo"  # default: já mostra intervalo inteiro
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
    # Pausa por segurança ao entrar no modo
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
# SIDEBAR — só upload de arquivos
# =========================================================

with st.sidebar:
    st.markdown("## Arquivos")

    generation_file = st.file_uploader(
        "geracao.csv",
        type=["csv"],
        key="up_gen"
    )
    load_file = st.file_uploader(
        "consumo.csv",
        type=["csv"],
        key="up_load"
    )

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

    # Guardar no session_state para acesso global
    st.session_state.df_processado = df

    # Limites do dataset
    data_min = df["DataHora"].min().date()
    data_max = df["DataHora"].max().date()

    # Inicializar intervalo no primeiro carregamento
    if st.session_state.intervalo_inicio is None:
        st.session_state.intervalo_inicio = data_min
    if st.session_state.intervalo_fim is None:
        st.session_state.intervalo_fim = data_max

    # =====================================================
    # ESTATÍSTICAS GLOBAIS (CSV INTEIRO) — para cards fixos
    # =====================================================
    # Filtra apenas os pontos originais (sem os de cruzamento que têm minuto != 0)
    df_originais = df[df["DataHora"].dt.minute == 0].copy() if len(df) > 0 else df

    total_import_full = df_originais[df_originais["Energia_Light"] > 0]["Energia_Light"].sum()
    energia_cortada_full = df_originais["Geracao_Cortada"].sum()
    energia_aproveitada_full = df_originais["Geracao_Limitada"].sum()
    energia_geravel_full = df_originais["Geracao"].sum()
    energia_consumida_full = df_originais["Carga"].sum()
    max_corte_full = df_originais["Geracao_Cortada"].max() if len(df_originais) else 0
    horas_corte_full = (df_originais["Geracao_Cortada"] > 0).sum()
    total_horas_full = len(df_originais)

    # Fator de Cobertura: quanto do consumo total foi suprido pela geração solar
    if energia_consumida_full > 0:
        fator_cobertura_full = (energia_aproveitada_full / energia_consumida_full) * 100
    else:
        fator_cobertura_full = 0

    # Taxa de Desperdício: energia cortada / energia gerável (inverso da simultaneidade)
    if energia_geravel_full > 0:
        taxa_desperdicio_full = (energia_cortada_full / energia_geravel_full) * 100
    else:
        taxa_desperdicio_full = 0

    # Índice de Simultaneidade: quanto da geração potencial foi efetivamente aproveitada.
    # 100% = usina perfeitamente dimensionada (tudo que gerou foi consumido)
    # < 60% = usina superdimensionada (muito curtailment, ociosidade alta)
    if energia_geravel_full > 0:
        simultaneidade_full = (energia_aproveitada_full / energia_geravel_full) * 100
    else:
        simultaneidade_full = 0

    # =====================================================
    # GARANTIR LIMITES DO ÍNDICE
    # =====================================================
    if st.session_state.index >= len(df):
        st.session_state.index = len(df) - 1
    if st.session_state.index < 0:
        st.session_state.index = 0

    # =====================================================
    # SELEÇÃO DO DATAFRAME E DADOS DOS KPIs CONFORME MODO
    # =====================================================
    modo = st.session_state.view_mode

    if modo == "Replay":
        # Modo Replay: avança hora a hora
        current_index = st.session_state.index
        chart_df = df.iloc[: current_index + 1]
        current = df.iloc[current_index]

        # KPIs do topo: valor instantâneo
        kpi_data = {
            "header_titulo": current["DataHora"].strftime("%d/%m/%Y %H:%M"),
            "header_sub": "Ponto atual do replay",
            "carga": (f"{fmt_int(current['Carga'])} kW", "Instantâneo"),
            "limitada": (f"{fmt_int(current['Geracao_Limitada'])} kW", "Instantâneo"),
            "cortada": (f"{fmt_int(current['Geracao_Cortada'])} kW", "Instantâneo"),
            "light": (f"{fmt_int(current['Energia_Light'])} kW", "Instantâneo"),
            "status_ativo": current["Geracao_Cortada"] > 0,
        }
        # Sparklines com os últimos 40 pontos
        spark_source = chart_df
    else:
        # Modo Intervalo: filtra pelo período selecionado
        d_ini = pd.to_datetime(st.session_state.intervalo_inicio)
        d_fim = pd.to_datetime(st.session_state.intervalo_fim) + pd.Timedelta(days=1)
        chart_df = df[(df["DataHora"] >= d_ini) & (df["DataHora"] < d_fim)]

        # Para estatísticas, usar só pontos originais dentro do intervalo
        intervalo_originais = chart_df[chart_df["DataHora"].dt.minute == 0]

        carga_total_kwh = intervalo_originais["Carga"].sum()
        limitada_total_kwh = intervalo_originais["Geracao_Limitada"].sum()
        cortada_total_kwh = intervalo_originais["Geracao_Cortada"].sum()
        geravel_total_kwh = intervalo_originais["Geracao"].sum()
        light_total_kwh = intervalo_originais[intervalo_originais["Energia_Light"] > 0]["Energia_Light"].sum()

        horas_ativo = (intervalo_originais["Geracao_Cortada"] > 0).sum()
        total_horas = len(intervalo_originais)

        # Simultaneidade do intervalo
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
    # HEADER — Card de período + KPIs + Status
    # =====================================================
    # =====================================================
    # HEADER — Cards conforme modo
    # =====================================================

    if modo == "Replay":
        # Modo Replay: uma única linha com 6 cards
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
        # Modo Intervalo: duas linhas de cards com labels separadores

        # ── Label do período ──
        st.markdown(
            f"""
            <div style="font-size:14px; font-weight:600; color:#374151; margin-bottom:4px;">
                🕒 Período selecionado: <span style="color:#2563eb;">{kpi_data['header_titulo']}</span>
                <span style="font-size:12px; color:#6b7280; font-weight:400;"> — {kpi_data['header_sub']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ── Linha 1: Energia ──
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

        # ── Linha 2: Indicadores ──
        st.markdown(
            '<div style="font-size:13px; font-weight:600; color:#6b7280; margin:14px 0 6px 0;">'
            '📊 Indicadores de Desempenho</div>',
            unsafe_allow_html=True
        )

        cols_linha2 = st.columns([1, 1, 1])

        # Simultaneidade
        simul = kpi_data["simultaneidade"]
        if simul >= 80:
            sim_color, sim_icon, sim_text = "#16a34a", "🛡️", "Bem dimensionada"
        elif simul >= 60:
            sim_color, sim_icon, sim_text = "#ca8a04", "⚡", "Dimensionamento intermediário"
        else:
            sim_color, sim_icon, sim_text = "#dc2626", "⚠️", "Superdimensionada"

        with cols_linha2[0]:
            st.markdown(
                kpi_card_html(
                    "Simultaneidade",
                    f"{simul:.1f}%",
                    sim_color,
                    f"{sim_icon} {sim_text}",
                    ""
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
                    ""
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
                    ""
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

    # Toggle de modo
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

    # Controles específicos do modo
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
        # Modo Intervalo
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
            st.button(
                "1 dia",
                use_container_width=True,
                key="btn_1d",
                on_click=lambda: aplicar_atalho_intervalo(1, df)
            )
        with ctrl_cols[3]:
            st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
            st.button(
                "7 dias",
                use_container_width=True,
                key="btn_7d",
                on_click=lambda: aplicar_atalho_intervalo(7, df)
            )
        with ctrl_cols[4]:
            st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
            st.button(
                "30 dias",
                use_container_width=True,
                key="btn_30d",
                on_click=lambda: aplicar_atalho_intervalo(30, df)
            )
        with ctrl_cols[5]:
            st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
            st.button(
                "Tudo",
                use_container_width=True,
                key="btn_all",
                on_click=lambda: aplicar_atalho_intervalo(None, df)
            )

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

    # ── Linha 1: Valores de energia ──
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

    # ── Linha 2: Indicadores percentuais ──
    st.markdown(
        '<div style="font-size:13px; font-weight:600; color:#6b7280; margin:14px 0 6px 0;">'
        '📊 Indicadores de Desempenho</div>',
        unsafe_allow_html=True
    )

    # Classificações qualitativas
    fc_color, fc_icon, fc_label = classificar_fator_cobertura(fator_cobertura_full)
    td_color, td_icon, td_label = classificar_taxa_desperdicio(taxa_desperdicio_full)

    if simultaneidade_full >= 80:
        simul_class = "summary-green"
        simul_color = "#16a34a"
        simul_label = "Usina bem dimensionada"
    elif simultaneidade_full >= 60:
        simul_class = "summary-yellow"
        simul_color = "#ca8a04"
        simul_label = "Dimensionamento intermediário"
    else:
        simul_class = "summary-red"
        simul_color = "#dc2626"
        simul_label = "Usina superdimensionada"

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            summary_box_html(
                "Simultaneidade",
                f"{simultaneidade_full:.1f}%",
                simul_color, simul_class,
                f"🛡️ {simul_label}"
            ),
            unsafe_allow_html=True
        )
    with s2:
        st.markdown(
            summary_box_html(
                "Fator de Cobertura",
                f"{fator_cobertura_full:.1f}%",
                fc_color, "summary-green",
                f"{fc_icon} {fc_label}"
            ),
            unsafe_allow_html=True
        )
    with s3:
        st.markdown(
            summary_box_html(
                "Taxa de Desperdício",
                f"{taxa_desperdicio_full:.1f}%",
                td_color, "summary-orange",
                f"{td_icon} {td_label}"
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

    # Usa apenas pontos originais (minutos zerados, sem cruzamentos artificiais)
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
