import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

/* =====================================================
FUNDO
===================================================== */

.stApp {
    background-color: #f4f6fb;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {
    background-color: #f0f2f6;
    border-right: 1px solid #dfe3eb;
}

/* =====================================================
REMOVE ESPAÇAMENTO
===================================================== */

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

/* =====================================================
CARDS
===================================================== */

.kpi-card {
    background: white;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    height: 120px;
    position: relative;
    overflow: hidden;
}

.kpi-title {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 42px;
    font-weight: 700;
    line-height: 1;
}

.kpi-sub {
    font-size: 13px;
    color: #7b8190;
    margin-top: 8px;
}

.status-ok {
    color: #16a34a;
}

.status-export {
    color: #dc2626;
}

/* =====================================================
TÍTULOS
===================================================== */

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
}

/* =====================================================
CAIXAS RESUMO
===================================================== */

.summary-box {
    background: white;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* =====================================================
TABELA
===================================================== */

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## Controles")

    run_simulation = st.toggle(
        "▶ Rodando Replay",
        value=True
    )

    speed = st.slider(
        "Velocidade Replay",
        0.1,
        2.0,
        0.5,
        0.1
    )

    st.markdown("---")

    st.markdown("### Intervalo dos dados")

    start_date = st.date_input(
        "Início"
    )

    end_date = st.date_input(
        "Fim"
    )

    st.markdown("---")

    st.markdown("### Zoom rápido")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.button("24h")

    with c2:
        st.button("7 dias")

    with c3:
        st.button("30 dias")

    with c4:
        st.button("1 ano")

    st.markdown("---")

    generation_file = st.file_uploader(
        "geracao.csv",
        type=["csv"]
    )

    load_file = st.file_uploader(
        "consumo.csv",
        type=["csv"]
    )

# =========================================================
# HEADER
# =========================================================

top1, top2 = st.columns([1.2, 6])

with top1:

    st.markdown("""
    <div class="kpi-card"
    style="height:120px; display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;">

    <div style="
    font-size:42px;
    font-weight:700;
    ">
    🕒
    </div>

    <div style="
    font-size:20px;
    font-weight:700;
    margin-top:10px;
    ">
    Replay
    </div>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PROCESSAMENTO
# =========================================================

if generation_file and load_file:

    # =====================================================
    # LOAD CSV
    # =====================================================

    gen_df = pd.read_csv(generation_file)
    load_df = pd.read_csv(load_file)

    gen_df.columns = ["DataHora", "Geracao"]
    load_df.columns = ["DataHora", "Carga"]

    gen_df["DataHora"] = pd.to_datetime(
        gen_df["DataHora"]
    )

    load_df["DataHora"] = pd.to_datetime(
        load_df["DataHora"]
    )

    df = pd.merge(
        gen_df,
        load_df,
        on="DataHora"
    )

    # =====================================================
    # GRIDZERO
    # =====================================================

    df["Geracao_Limitada"] = df[
        ["Geracao", "Carga"]
    ].min(axis=1)

    df["Geracao_Cortada"] = (
        df["Geracao"]
        - df["Geracao_Limitada"]
    )

    df["Energia_Light"] = (
        df["Carga"]
        - df["Geracao_Limitada"]
    )

    # =====================================================
    # SESSION
    # =====================================================

    if "index" not in st.session_state:
        st.session_state.index = 0

    current_index = st.session_state.index

    if current_index >= len(df):
        current_index = len(df) - 1

    replay_df = df.iloc[:current_index + 1]

    current = df.iloc[current_index]

    # =====================================================
    # TOP KPIs
    # =====================================================

    with top2:

        c1, c2, c3, c4, c5 = st.columns(5)

        def kpi_card(
            coluna,
            titulo,
            valor,
            cor,
            subtitulo=""
        ):

            with coluna:

                st.markdown(f"""
                <div class="kpi-card">

                    <div class="kpi-title"
                    style="color:{cor}">
                    {titulo}
                    </div>

                    <div class="kpi-value"
                    style="color:{cor}">
                    {valor}
                    </div>

                    <div class="kpi-sub">
                    {subtitulo}
                    </div>

                </div>
                """, unsafe_allow_html=True)

        kpi_card(
            c1,
            "Carga Atual",
            f"{current['Carga']:.0f} kW",
            "#2563eb"
        )

        kpi_card(
            c2,
            "Geração Limitada",
            f"{current['Geracao_Limitada']:.0f} kW",
            "#16a34a"
        )

        kpi_card(
            c3,
            "Geração Cortada",
            f"{current['Geracao_Cortada']:.0f} kW",
            "#f97316"
        )

        kpi_card(
            c4,
            "Energia da Light",
            f"{current['Energia_Light']:.0f} kW",
            "#9333ea"
        )

        # =================================================
        # STATUS
        # =================================================

        if current["Geracao_Cortada"] > 0:

            status = "GridZero Ativo"
            sub = "Sem exportação"
            cor = "#16a34a"

        else:

            status = "Normal"
            sub = "Sem limitação"
            cor = "#64748b"

        kpi_card(
            c5,
            "Status",
            status,
            cor,
            sub
        )

    # =====================================================
    # GRÁFICO
    # =====================================================

    st.markdown("""
    <div class="section-title">
    Fluxo de Potência
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()

    # =====================================================
    # CARGA
    # =====================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Carga"],

        name="Carga",

        mode="lines",

        line=dict(
            color="#2563eb",
            width=3,
            shape="spline",
            smoothing=1.2
        )

    ))

    # =====================================================
    # GERAÇÃO LIMITADA
    # =====================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Geracao_Limitada"],

        name="Geração Limitada",

        mode="lines",

        line=dict(
            color="#16a34a",
            width=3,
            shape="spline",
            smoothing=1.2
        )

    ))

    # =====================================================
    # GERAÇÃO CORTADA
    # =====================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Geracao_Cortada"],

        name="Geração Cortada",

        mode="lines",

        line=dict(
            color="#f97316",
            width=3,
            dash="dash",
            shape="spline",
            smoothing=1.2
        )

    ))

    # =====================================================
    # ENERGIA LIGHT
    # =====================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Energia_Light"],

        name="Energia Consumida da Light",

        mode="lines",

        line=dict(
            color="#9333ea",
            width=3,
            shape="spline",
            smoothing=1.2
        )

    ))

    # =====================================================
    # LINHA ZERO
    # =====================================================

    fig.add_hline(

        y=0,

        line_width=4,

        line_color="black"

    )

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        height=600,

        template="plotly_white",

        paper_bgcolor="white",

        plot_bgcolor="white",

        hovermode="x unified",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),

        xaxis=dict(
            title="Tempo",
            rangeslider=dict(
                visible=False
            )
        ),

        yaxis=dict(
            title="Potência (kW)",
            gridcolor="#e5e7eb"
        )

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # RESUMO
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    total_import = replay_df[
        replay_df["Energia_Light"] > 0
    ]["Energia_Light"].sum()

    energia_cortada = replay_df[
        "Geracao_Cortada"
    ].sum()

    max_corte = replay_df[
        "Geracao_Cortada"
    ].max()

    horas_corte = len(
        replay_df[
            replay_df["Geracao_Cortada"] > 0
        ]
    )

    def summary(
        coluna,
        titulo,
        valor,
        cor,
        sub=""
    ):

        with coluna:

            st.markdown(f"""
            <div class="summary-box">

                <div style="
                font-size:16px;
                font-weight:600;
                color:{cor};
                ">
                {titulo}
                </div>

                <div style="
                font-size:42px;
                font-weight:700;
                color:{cor};
                margin-top:10px;
                ">
                {valor}
                </div>

                <div style="
                font-size:14px;
                color:#7b8190;
                margin-top:5px;
                ">
                {sub}
                </div>

            </div>
            """, unsafe_allow_html=True)

    summary(
        c1,
        "Energia Importada da Light",
        f"{total_import:.0f} kWh",
        "#2563eb",
        "Total no período"
    )

    summary(
        c2,
        "Energia que seria Exportada",
        f"{energia_cortada:.0f} kWh",
        "#dc2626",
        "Evitada pelo GridZero"
    )

    summary(
        c3,
        "Máxima Geração Cortada",
        f"{max_corte:.0f} kW",
        "#16a34a",
        "Pico de corte"
    )

    summary(
        c4,
        "Horas com Corte",
        f"{horas_corte:.0f} h",
        "#9333ea",
        "GridZero ativo"
    )

    # =====================================================
    # TABELA
    # =====================================================

    st.markdown("""
    <br>
    <div class="section-title">
    Dados Operacionais
    </div>
    """, unsafe_allow_html=True)

    tabela = replay_df.copy()

    tabela = tabela.rename(columns={
        "Geracao_Limitada": "Geração Limitada (kW)",
        "Geracao_Cortada": "Geração Cortada (kW)",
        "Energia_Light": "Energia Consumida da Light (kW)",
        "Carga": "Carga (kW)"
    })

    st.dataframe(
        tabela.tail(20),
        use_container_width=True,
        height=320
    )

    # =====================================================
    # AUTO PLAY
    # =====================================================

    if run_simulation:

        if st.session_state.index < len(df) - 1:

            st.session_state.index += 1

            time.sleep(speed)

            st.rerun()

else:

    st.info(
        "Faça upload dos arquivos CSV."
    )
