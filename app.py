import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# =========================================================
# CONFIG PAGE
# =========================================================

st.set_page_config(
    page_title="GridZero Simulator",
    layout="wide"
)

# =========================================================
# CSS CUSTOM
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 1rem;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

.metric-title {
    font-size: 15px;
    font-weight: 600;
    color: #555;
}

.metric-value {
    font-size: 38px;
    font-weight: 700;
}

.metric-sub {
    font-size: 13px;
    color: #888;
}

.sidebar .sidebar-content {
    background-color: #f1f3f6;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.title("⚡ GridZero Replay Simulator")

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("Controles")

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

    st.divider()

    generation_file = st.file_uploader(
        "CSV Geração",
        type=["csv"]
    )

    load_file = st.file_uploader(
        "CSV Carga",
        type=["csv"]
    )

    st.divider()

    if st.button("🔄 Reiniciar Replay"):

        st.session_state.index = 0

# =========================================================
# CSV MODEL
# =========================================================

with st.expander("📄 Modelo CSV"):

    st.code("""
DataHora,Potencia
2026-01-01 00:00,0
2026-01-01 01:00,0
2026-01-01 12:00,3200
""")

# =========================================================
# PROCESS
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

    # =====================================================
    # MERGE
    # =====================================================

    df = pd.merge(
        gen_df,
        load_df,
        on="DataHora"
    )

    # =====================================================
    # GRIDZERO LOGIC
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
    # STATUS
    # =====================================================

    df["Exportando"] = (
        df["Energia_Light"] < 0
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
    # TOP KPIS
    # =====================================================

    st.subheader(
        f"🕒 {current['DataHora']}"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    # =====================================================
    # CARD FUNCTION
    # =====================================================

    def card(
        coluna,
        titulo,
        valor,
        cor,
        subtitulo=""
    ):

        with coluna:

            st.markdown(f"""
            <div class="card">

                <div class="metric-title"
                style="color:{cor}">
                {titulo}
                </div>

                <div class="metric-value"
                style="color:{cor}">
                {valor}
                </div>

                <div class="metric-sub">
                {subtitulo}
                </div>

            </div>
            """, unsafe_allow_html=True)

    # =====================================================
    # CARDS
    # =====================================================

    card(
        col1,
        "Carga Atual",
        f"{current['Carga']:.0f} kW",
        "#2563eb"
    )

    card(
        col2,
        "Geração Limitada",
        f"{current['Geracao_Limitada']:.0f} kW",
        "#16a34a"
    )

    card(
        col3,
        "Geração Cortada",
        f"{current['Geracao_Cortada']:.0f} kW",
        "#f97316"
    )

    card(
        col4,
        "Energia da Light",
        f"{current['Energia_Light']:.0f} kW",
        "#9333ea"
    )

    # =====================================================
    # STATUS
    # =====================================================

    if current["Exportando"]:

        status_text = "EXPORTANDO"
        status_color = "#dc2626"

    elif current["Geracao_Cortada"] > 0:

        status_text = "GridZero Ativo"
        status_color = "#16a34a"

    else:

        status_text = "Sem Limitação"
        status_color = "#666"

    card(
        col5,
        "Status",
        status_text,
        status_color
    )

    # =====================================================
    # GRAPH
    # =====================================================

    st.subheader("Fluxo de Potência")

    fig = go.Figure()

    # =====================================================
    # CARGA
    # =====================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Carga"],

        mode='lines',

        line=dict(
            color="#2563eb",
            width=3,
            shape='spline',
            smoothing=1.2
        ),

        name='Carga'

    ))

    # =====================================================
    # GERAÇÃO LIMITADA
    # =====================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Geracao_Limitada"],

        mode='lines',

        line=dict(
            color="#16a34a",
            width=3,
            shape='spline',
            smoothing=1.2
        ),

        name='Geração Limitada'

    ))

    # =====================================================
    # GERAÇÃO CORTADA
    # =====================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Geracao_Cortada"],

        mode='lines',

        line=dict(
            color="#f97316",
            width=3,
            dash='dash',
            shape='spline',
            smoothing=1.2
        ),

        name='Geração Cortada'

    ))

    # =====================================================
    # ENERGIA LIGHT
    # =====================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Energia_Light"],

        mode='lines',

        line=dict(
            color="#9333ea",
            width=3,
            shape='spline',
            smoothing=1.2
        ),

        name='Energia Consumida da Light'

    ))

    # =====================================================
    # EXPORTAÇÃO
    # =====================================================

    export_df = replay_df[
        replay_df["Energia_Light"] < 0
    ]

    fig.add_trace(go.Scatter(

        x=export_df["DataHora"],
        y=export_df["Energia_Light"],

        mode='markers',

        marker=dict(
            size=8,
            color='red'
        ),

        name='Exportação'

    ))

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        template="plotly_white",

        height=600,

        paper_bgcolor="white",

        plot_bgcolor="white",

        hovermode="x unified",

        font=dict(
            family="Arial",
            size=14
        ),

        xaxis=dict(

            title="Tempo",

            rangeslider=dict(
                visible=True
            ),

            type="date"

        ),

        yaxis_title="Potência (kW)",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )

    )

    # =====================================================
    # ZERO LINE
    # =====================================================

    fig.add_hline(

        y=0,

        line_width=4,

        line_color="black"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # STATS
    # =====================================================

    st.subheader("Resumo Operacional")

    total_export = replay_df[
        replay_df["Energia_Light"] < 0
    ]["Energia_Light"].abs().sum()

    total_import = replay_df[
        replay_df["Energia_Light"] > 0
    ]["Energia_Light"].sum()

    max_cut = replay_df[
        "Geracao_Cortada"
    ].max()

    hours_cut = len(
        replay_df[
            replay_df["Geracao_Cortada"] > 0
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    card(
        col1,
        "Energia Importada",
        f"{total_import:.0f} kWh",
        "#2563eb"
    )

    card(
        col2,
        "Energia Evitada",
        f"{total_export:.0f} kWh",
        "#dc2626"
    )

    card(
        col3,
        "Máx Geração Cortada",
        f"{max_cut:.0f} kW",
        "#16a34a"
    )

    card(
        col4,
        "Horas com Corte",
        f"{hours_cut:.0f} h",
        "#9333ea"
    )

    # =====================================================
    # TABLE
    # =====================================================

    st.subheader("Dados Operacionais")

    st.dataframe(

        replay_df.tail(50),

        use_container_width=True,

        height=300

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
