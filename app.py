import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="GridZero Replay Simulator",
    layout="wide"
)

st.title("⚡ GridZero Replay Simulator")
st.markdown(
    """
Simulador GridZero utilizando dados REAIS de:
- geração fotovoltaica
- consumo da carga

Faça upload dos CSVs e reproduza a operação da planta.
"""
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Controles")

run_simulation = st.sidebar.toggle(
    "▶ Rodando Replay",
    value=False
)

speed = st.sidebar.slider(
    "Velocidade Replay",
    0.1,
    2.0,
    0.5,
    0.1
)

# ============================================================
# UPLOADS
# ============================================================

st.subheader("Upload dos Arquivos CSV")

col1, col2 = st.columns(2)

with col1:

    generation_file = st.file_uploader(
        "CSV de Geração FV",
        type=["csv"]
    )

with col2:

    load_file = st.file_uploader(
        "CSV de Consumo/Carga",
        type=["csv"]
    )

# ============================================================
# MODELO CSV
# ============================================================

with st.expander("📄 Modelo esperado dos CSVs"):

    st.code(
        """
DataHora,Potencia
2026-01-01 00:00,0
2026-01-01 01:00,0
2026-01-01 02:00,0
2026-01-01 12:00,3200
        """
    )

# ============================================================
# PROCESSAMENTO
# ============================================================

if generation_file and load_file:

    # ========================================================
    # LEITURA CSV
    # ========================================================

    gen_df = pd.read_csv(generation_file)
    load_df = pd.read_csv(load_file)

    # ========================================================
    # RENOMEIA COLUNAS
    # ========================================================

    gen_df.columns = ["DataHora", "Geracao"]
    load_df.columns = ["DataHora", "Carga"]

    # ========================================================
    # DATETIME
    # ========================================================

    gen_df["DataHora"] = pd.to_datetime(
        gen_df["DataHora"]
    )

    load_df["DataHora"] = pd.to_datetime(
        load_df["DataHora"]
    )

    # ========================================================
    # MERGE
    # ========================================================

    df = pd.merge(
        gen_df,
        load_df,
        on="DataHora"
    )

    # ========================================================
    # GRID
    # ========================================================

    df["Rede"] = (
        df["Carga"]
        - df["Geracao"]
    )

    # ========================================================
    # EXPORTAÇÃO
    # ========================================================

    df["Exportando"] = (
        df["Rede"] < 0
    )

    # ========================================================
    # SESSION STATE
    # ========================================================

    if "index" not in st.session_state:

        st.session_state.index = 0

    # ========================================================
    # RESET
    # ========================================================

    if st.button("🔄 Reiniciar Replay"):

        st.session_state.index = 0

    # ========================================================
    # PLAYBACK
    # ========================================================

    current_index = st.session_state.index

    if current_index >= len(df):

        current_index = len(df) - 1

    replay_df = df.iloc[:current_index + 1]

    current = df.iloc[current_index]

    # ========================================================
    # KPIs
    # ========================================================

    st.subheader(
        f"🕒 {current['DataHora']}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Carga",
            f"{current['Carga']:.0f} kW"
        )

    with col2:

        st.metric(
            "Geração FV",
            f"{current['Geracao']:.0f} kW"
        )

    with col3:

        st.metric(
            "Potência Rede",
            f"{current['Rede']:.0f} kW"
        )

    with col4:

        if current["Exportando"]:

            st.error("EXPORTANDO")

        else:

            st.success("GRIDZERO")

    # ========================================================
    # GRÁFICO
    # ========================================================

    st.subheader("Fluxo de Potência")

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Carga"],

        mode='lines',

        line=dict(
            shape='spline',
            smoothing=1.2
        ),

        name='Carga'

    ))

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Geracao"],

        mode='lines',

        line=dict(
            shape='spline',
            smoothing=1.2
        ),

        name='Geração FV'

    ))

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Rede"],

        mode='lines',

        line=dict(
            shape='spline',
            smoothing=1.2
        ),

        name='Rede'

    ))

    # ========================================================
    # EXPORTAÇÃO DESTACADA
    # ========================================================

    export_df = replay_df[
        replay_df["Rede"] < 0
    ]

    fig.add_trace(go.Scatter(

        x=export_df["DataHora"],
        y=export_df["Rede"],

        mode='markers',

        marker=dict(
            size=8,
            color='red'
        ),

        name='Exportação'

    ))

    # ========================================================
    # LINHA ZERO DESTACADA
    # ========================================================

    fig.update_layout(

        height=600,

        shapes=[

            dict(

                type="line",

                x0=replay_df["DataHora"].min(),
                x1=replay_df["DataHora"].max(),

                y0=0,
                y1=0,

                line=dict(
                    color="black",
                    width=4
                )

            )

        ],

        xaxis=dict(

            title="Tempo",

            rangeslider=dict(
                visible=True
            ),

            type="date"
        ),

        yaxis_title="Potência (kW)",

        hovermode="x unified"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    st.subheader("Resumo Operacional")

    total_export = abs(
        replay_df[
            replay_df["Rede"] < 0
        ]["Rede"].sum()
    )

    max_export = replay_df["Rede"].min()

    total_import = replay_df[
        replay_df["Rede"] > 0
    ]["Rede"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Energia Exportada",
            f"{total_export:.0f} kWh"
        )

    with col2:

        st.metric(
            "Máx Exportação",
            f"{max_export:.0f} kW"
        )

    with col3:

        st.metric(
            "Energia Importada",
            f"{total_import:.0f} kWh"
        )

    # ========================================================
    # TABELA
    # ========================================================

    st.subheader("Dados Operacionais")

    st.dataframe(
        replay_df.tail(50),
        use_container_width=True
    )

    # ========================================================
    # AUTO PLAY
    # ========================================================

    if run_simulation:

        if st.session_state.index < len(df) - 1:

            st.session_state.index += 1

            time.sleep(speed)

            st.rerun()

else:

    st.info(
        "Faça upload dos dois arquivos CSV para iniciar o replay."
    )
