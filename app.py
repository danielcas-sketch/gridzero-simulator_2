import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GridZero Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS PROFISSIONAL
# =========================================================

st.markdown("""
<style>

/* Fundo geral */
.stApp { background-color: #f4f6fb; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #1f2937;
    font-weight: 600;
}

/* Container principal */
.block-container {
    padding-top: 4rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

/* Esconde o header padrão do Streamlit que sobrepõe o conteúdo */
header[data-testid="stHeader"] {
    background-color: rgba(244, 246, 251, 0.8);
    backdrop-filter: blur(6px);
}

/* Botão primário (Rodando Replay / Pausar) */
section[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    height: 42px;
}
section[data-testid="stSidebar"] button[kind="primary"]:hover {
    background-color: #1d4ed8;
}

/* Botão secundário (Reiniciar Replay) */
section[data-testid="stSidebar"] button[kind="secondary"] {
    background-color: #ffffff;
    color: #374151;
    border-radius: 10px;
    border: 1px solid #d1d5db;
    font-weight: 500;
    height: 42px;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background-color: #f3f4f6;
    border-color: #9ca3af;
}

/* Cards KPI do topo */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    height: 130px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.kpi-value {
    font-size: 30px;
    font-weight: 700;
    line-height: 1.1;
    margin-top: 4px;
}
.kpi-spark {
    margin-top: 4px;
    height: 30px;
}

/* Card de Replay (timestamp) */
.replay-card {
    background: white;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.replay-clock { font-size: 14px; color: #6b7280; }
.replay-time {
    font-size: 26px;
    font-weight: 700;
    color: #1f2937;
    margin-top: 4px;
}
.replay-sub {
    font-size: 12px;
    color: #9ca3af;
    margin-top: 6px;
}

/* Card de Status */
.status-card {
    background: white;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.status-label { font-size: 13px; font-weight: 600; color: #6b7280; }
.status-main {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 6px;
}
.status-icon { font-size: 28px; }
.status-text { font-size: 22px; font-weight: 700; }
.status-sub { font-size: 13px; color: #6b7280; margin-top: 4px; }

/* Título de seção */
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #1f2937;
    margin: 14px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Summary boxes */
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
.summary-title { font-size: 14px; font-weight: 600; }
.summary-value { font-size: 28px; font-weight: 700; margin-top: 8px; line-height: 1.1; }
.summary-sub { font-size: 12px; color: #6b7280; margin-top: 4px; }

/* Cards de arquivos carregados */
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

/* Dataframe */
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
    """Gera SVG simples de sparkline a partir de uma lista de valores."""
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

    svg = f'''
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
    return svg


def kpi_card_html(title, value, color, sparkline_html=""):
    """Gera HTML de um card KPI com sparkline."""
    return f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-title" style="color:{color}">{title}</div>
            <div class="kpi-value" style="color:{color}">{value}</div>
        </div>
        <div class="kpi-spark">{sparkline_html}</div>
    </div>
    """


def summary_box_html(title, value, color, cls, sub=""):
    """Gera HTML de um card de resumo."""
    return f"""
    <div class="summary-box {cls}">
        <div class="summary-title" style="color:{color}">{title}</div>
        <div class="summary-value" style="color:{color}">{value}</div>
        <div class="summary-sub">{sub}</div>
    </div>
    """


@st.cache_data(show_spinner=False)
def carregar_e_processar(gen_bytes, load_bytes):
    """Carrega CSVs, calcula GridZero e insere pontos de cruzamento.
    Tudo cacheado: só roda novamente se os bytes dos arquivos mudarem.
    Vetorizado com numpy para ser rápido mesmo com 10k+ pontos.
    """
    import io

    gen_df = pd.read_csv(io.BytesIO(gen_bytes))
    load_df = pd.read_csv(io.BytesIO(load_bytes))

    gen_df.columns = ["DataHora", "Geracao"]
    load_df.columns = ["DataHora", "Carga"]

    gen_df["DataHora"] = pd.to_datetime(gen_df["DataHora"])
    load_df["DataHora"] = pd.to_datetime(load_df["DataHora"])

    df = pd.merge(gen_df, load_df, on="DataHora").sort_values("DataHora").reset_index(drop=True)

    # ---------- GridZero (vetorizado) ----------
    df["Geracao_Limitada"] = np.minimum(df["Geracao"], df["Carga"])
    df["Geracao_Cortada"] = df["Geracao"] - df["Geracao_Limitada"]
    df["Energia_Light"] = df["Carga"] - df["Geracao_Limitada"]
    df["Energia_Light_Visual"] = df["Energia_Light"] - df["Geracao_Cortada"]

    # ---------- Detecção vetorizada de cruzamentos ----------
    geracao = df["Geracao"].values
    carga = df["Carga"].values
    tempo = df["DataHora"].values
    diff = geracao - carga  # > 0 = corte ativo

    # Pares (i, i+1) onde os sinais se invertem
    sign_change = (diff[:-1] * diff[1:]) < 0
    cross_indices = np.where(sign_change)[0]

    # Calcula tempo e valor do cruzamento para cada par detectado
    cross_records = []
    for i in cross_indices:
        da, db = diff[i], diff[i + 1]
        frac = da / (da - db)
        t_a = tempo[i].astype("int64")
        t_b = tempo[i + 1].astype("int64")
        t_cross = np.int64(t_a + (t_b - t_a) * frac).astype("datetime64[ns]")
        carga_cross = carga[i] + (carga[i + 1] - carga[i]) * frac
        cross_records.append({
            "DataHora": t_cross,
            "Carga": carga_cross,
            "Geracao": carga_cross,
            "Geracao_Limitada": carga_cross,
            "Geracao_Cortada": 0.0,
            "Energia_Light": 0.0,
            "Energia_Light_Visual": 0.0,
            "_is_cross": True,
        })

    df["_is_cross"] = False

    if cross_records:
        df_cross = pd.DataFrame(cross_records)
        df_full = pd.concat([df, df_cross], ignore_index=True)
        df_full = df_full.sort_values("DataHora").reset_index(drop=True)
    else:
        df_full = df.copy()

    # ---------- Coluna visual da Geração Cortada (vetorizada) ----------
    # Aparece quando há corte; nos pontos de cruzamento "encosta" na Carga.
    visual = np.where(
        df_full["Geracao_Cortada"].values > 0,
        df_full["Geracao"].values,
        np.nan
    )
    # Marca os pontos de cruzamento com o valor da Carga para conectar
    # visualmente a linha laranja com a linha azul.
    cross_mask = df_full["_is_cross"].values
    visual = np.where(cross_mask, df_full["Carga"].values, visual)
    df_full["Geracao_Cortada_Visual"] = visual

    return df_full


def format_filesize(num_bytes):
    """Formata tamanho de arquivo em KB ou MB."""
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.1f} MB"


# =========================================================
# SESSION STATE INIT
# =========================================================

if "index" not in st.session_state:
    st.session_state.index = 0
if "run_simulation" not in st.session_state:
    st.session_state.run_simulation = True


# =========================================================
# CALLBACKS (atualizam estado SEM forçar rerun manual)
# =========================================================

def toggle_play():
    st.session_state.run_simulation = not st.session_state.run_simulation

def reset_replay():
    st.session_state.index = 0


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## Controles")

    # Botão de play/pause via callback (sem st.rerun manual)
    if st.session_state.run_simulation:
        st.button(
            "⏸  Pausar Replay",
            type="primary",
            use_container_width=True,
            key="btn_toggle",
            on_click=toggle_play
        )
    else:
        st.button(
            "▶  Rodando Replay",
            type="primary",
            use_container_width=True,
            key="btn_toggle",
            on_click=toggle_play
        )

    st.markdown("**Velocidade Replay**")
    speed = st.slider(
        "Velocidade",
        0.1, 2.0, 0.5, 0.1,
        label_visibility="collapsed"
    )
    st.markdown(
        f"<div style='display:flex; justify-content:space-between; "
        f"font-size:12px; color:#6b7280; margin-top:-8px;'>"
        f"<span>0.1x</span><span style='font-weight:600; color:#2563eb;'>{speed}x</span><span>2.0x</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("")

    st.button(
        "↻  Reiniciar Replay",
        type="secondary",
        use_container_width=True,
        key="btn_reset",
        on_click=reset_replay
    )

    st.markdown("---")
    st.markdown("### Intervalo dos dados")

    start_date = st.date_input("Início:", key="dt_inicio")
    end_date = st.date_input("Fim:", key="dt_fim")

    st.markdown("---")
    st.markdown("### Arquivos carregados")

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


# =========================================================
# PROCESSAMENTO PRINCIPAL
# =========================================================

if generation_file and load_file:

    # Carregamento e processamento cacheado.
    # Só recalcula se os bytes dos arquivos mudarem.
    df = carregar_e_processar(
        generation_file.getvalue(),
        load_file.getvalue()
    )

    # ---------------- Replay state ----------------
    if st.session_state.index >= len(df):
        st.session_state.index = len(df) - 1
    if st.session_state.index < 0:
        st.session_state.index = 0

    current_index = st.session_state.index
    replay_df = df.iloc[: current_index + 1]
    current = df.iloc[current_index]

    # =====================================================
    # HEADER — Replay card + KPIs + Status
    # =====================================================

    cols = st.columns([1.6, 1.3, 1.3, 1.3, 1.3, 1.3])

    with cols[0]:
        ts = current["DataHora"]
        st.markdown(
            f"""
            <div class="replay-card">
                <div class="replay-clock">🕒</div>
                <div class="replay-time">{ts.strftime("%d/%m/%Y %H:%M")}</div>
                <div class="replay-sub">Ponto atual do replay</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    def spark_data(col, n=40):
        return replay_df[col].tail(n).tolist()

    with cols[1]:
        spark = sparkline_svg(spark_data("Carga"), "#2563eb")
        st.markdown(
            kpi_card_html(
                "Carga Atual",
                f"{current['Carga']:,.0f} kW".replace(",", "."),
                "#2563eb",
                spark
            ),
            unsafe_allow_html=True
        )

    with cols[2]:
        spark = sparkline_svg(spark_data("Geracao_Limitada"), "#16a34a")
        st.markdown(
            kpi_card_html(
                "Geração Limitada",
                f"{current['Geracao_Limitada']:,.0f} kW".replace(",", "."),
                "#16a34a",
                spark
            ),
            unsafe_allow_html=True
        )

    with cols[3]:
        spark = sparkline_svg(spark_data("Geracao_Cortada"), "#f97316")
        st.markdown(
            kpi_card_html(
                "Geração Cortada",
                f"{current['Geracao_Cortada']:,.0f} kW".replace(",", "."),
                "#f97316",
                spark
            ),
            unsafe_allow_html=True
        )

    with cols[4]:
        spark = sparkline_svg(spark_data("Energia_Light"), "#9333ea")
        st.markdown(
            kpi_card_html(
                "Energia da Light",
                f"{current['Energia_Light']:,.0f} kW".replace(",", "."),
                "#9333ea",
                spark
            ),
            unsafe_allow_html=True
        )

    with cols[5]:
        if current["Geracao_Cortada"] > 0:
            status_text = "GridZero Ativo"
            status_sub = "Sem exportação"
            status_color = "#16a34a"
            status_icon = "🛡️"
        else:
            status_text = "Normal"
            status_sub = "Sem limitação"
            status_color = "#64748b"
            status_icon = "✓"

        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Status</div>
                <div class="status-main">
                    <div class="status-icon">{status_icon}</div>
                    <div class="status-text" style="color:{status_color}">{status_text}</div>
                </div>
                <div class="status-sub">{status_sub}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # GRÁFICO COM RANGESLIDER
    # =====================================================

    st.markdown(
        '<div class="section-title">📈 Fluxo de Potência</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    # Carga (Consumo) — linha de referência azul
    fig.add_trace(go.Scatter(
        x=replay_df["DataHora"], y=replay_df["Carga"],
        name="Carga (Consumo)",
        mode="lines",
        line=dict(color="#2563eb", width=2.5, shape="spline", smoothing=1.2)
    ))

    # Geração Cortada — só aparece quando há corte real (Geração > Carga).
    # A área entre essa curva e a Carga (trace anterior) é preenchida em laranja,
    # representando visualmente o que o GridZero está cortando.
    fig.add_trace(go.Scatter(
        x=replay_df["DataHora"], y=replay_df["Geracao_Cortada_Visual"],
        name="Geração Cortada",
        mode="lines",
        line=dict(color="#f97316", width=2.5, dash="dash", shape="spline", smoothing=1.2),
        fill="tonexty",
        fillcolor="rgba(249, 115, 22, 0.20)",
        connectgaps=False
    ))

    # Geração Limitada — o que efetivamente foi gerado pelos inversores
    fig.add_trace(go.Scatter(
        x=replay_df["DataHora"], y=replay_df["Geracao_Limitada"],
        name="Geração Limitada",
        mode="lines",
        line=dict(color="#16a34a", width=2.5, shape="spline", smoothing=1.2)
    ))

    # Energia da Light (versão visual com valores negativos quando há corte)
    fig.add_trace(go.Scatter(
        x=replay_df["DataHora"], y=replay_df["Energia_Light_Visual"],
        name="Energia Consumida da Light",
        mode="lines",
        line=dict(color="#9333ea", width=2.5, shape="spline", smoothing=1.2)
    ))

    fig.add_hline(y=0, line_width=2.5, line_color="black")

    fig.update_layout(
        height=560,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0)",
            font=dict(size=12)
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        xaxis=dict(
            title="",
            gridcolor="#f1f5f9",
            showgrid=True,
            rangeslider=dict(
                visible=True,
                thickness=0.08,
                bgcolor="#f8fafc",
                bordercolor="#e5e7eb",
                borderwidth=1
            ),
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all", label="Tudo")
                ],
                bgcolor="#f1f5f9",
                activecolor="#2563eb",
                font=dict(size=12),
                x=0,
                y=1.12
            )
        ),
        yaxis=dict(
            title="Potência (kW)",
            gridcolor="#e5e7eb",
            zeroline=False
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # =====================================================
    # CARDS DE RESUMO
    # =====================================================

    total_import = replay_df[replay_df["Energia_Light"] > 0]["Energia_Light"].sum()
    energia_cortada = replay_df["Geracao_Cortada"].sum()
    max_corte = replay_df["Geracao_Cortada"].max() if len(replay_df) else 0
    horas_corte = len(replay_df[replay_df["Geracao_Cortada"] > 0])

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(
            summary_box_html(
                "Energia Importada (Light)",
                f"{total_import:,.0f} kWh".replace(",", "."),
                "#2563eb", "summary-blue",
                "Total no período selecionado"
            ),
            unsafe_allow_html=True
        )
    with s2:
        st.markdown(
            summary_box_html(
                "Energia Exportação (Evitada)",
                f"{energia_cortada:,.0f} kWh".replace(",", "."),
                "#dc2626", "summary-red",
                "Total cortada pelo GridZero"
            ),
            unsafe_allow_html=True
        )
    with s3:
        st.markdown(
            summary_box_html(
                "Máxima Exportação Evitada",
                f"{max_corte:,.0f} kW".replace(",", "."),
                "#16a34a", "summary-green",
                "Pico de geração cortada"
            ),
            unsafe_allow_html=True
        )
    with s4:
        pct = (horas_corte / len(replay_df) * 100) if len(replay_df) else 0
        st.markdown(
            summary_box_html(
                "Horas com Corte (GridZero Ativo)",
                f"{horas_corte:,.0f} h".replace(",", "."),
                "#9333ea", "summary-yellow",
                f"{pct:.1f}% do período"
            ),
            unsafe_allow_html=True
        )

    # =====================================================
    # TABELA
    # =====================================================

    st.markdown(
        '<div class="section-title">📋 Dados Operacionais '
        '<span style="font-size:13px; font-weight:400; color:#6b7280;">'
        '(últimos registros exibidos)</span></div>',
        unsafe_allow_html=True
    )

    tabela = replay_df.copy()
    tabela["Status"] = tabela["Geracao_Cortada"].apply(
        lambda x: "GridZero Ativo" if x > 0 else "Importando"
    )
    tabela = tabela[[
        "DataHora", "Carga", "Geracao_Limitada",
        "Geracao_Cortada", "Energia_Light", "Status"
    ]].rename(columns={
        "Carga": "Carga (kW)",
        "Geracao_Limitada": "Geração Limitada (kW)",
        "Geracao_Cortada": "Geração Cortada (kW)",
        "Energia_Light": "Energia Consumida da Light (kW)"
    })

    st.dataframe(
        tabela.tail(20).iloc[::-1],
        use_container_width=True,
        height=320,
        hide_index=True
    )

    # =====================================================
    # AUTO PLAY — só dispara rerun quando estiver em modo play
    # Quando pausado: o código NÃO chega aqui em modo de loop,
    # então a UI fica congelada no último estado renderizado.
    # =====================================================

    if st.session_state.run_simulation and st.session_state.index < len(df) - 1:
        time.sleep(speed)
        st.session_state.index += 1
        st.rerun()

else:
    st.info("📂 Faça o upload dos arquivos **geracao.csv** e **consumo.csv** na barra lateral para iniciar o replay.")
