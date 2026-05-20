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

st.markdown("""
Simulador de operação GridZero utilizando:
- Curva real de geração FV
- Curva real de carga
- Replay temporal
- Visualização de corte de geração
""")

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

    st.code("""
DataHora,Potencia
2026-01-01 00:00,0
2026-01-01 01:00,0
2026-01-01 12:00,3200
""")

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
    # GERAÇÃO LIMITADA
    # ========================================================

    df["Geracao_Limitada"] = df[
        ["Geracao", "Carga"]
    ].min(axis=1)

    # ========================================================
    # GERAÇÃO CORTADA
    # ========================================================

    df["Geracao_Cortada"] = df["Geracao"]

    # ========================================================
    # ENERGIA CONSUMIDA DA LIGHT
    # ========================================================

    df["Energia_Light"] = (
        df["Carga"]
        - df["Geracao_Limitada"]
    )

    # ========================================================
    # EXPORTAÇÃO
    # ========================================================

    df["Exportando"] = (
        df["Energia_Light"] < 0
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
            "Geração Limitada",
            f"{current['Geracao_Limitada']:.0f} kW"
        )

    with col3:

        st.metric(
            "Geração Cortada",
            f"{(current['Geracao_Cortada'] - current['Geracao_Limitada']):.0f} kW"
        )

    with col4:

        st.metric(
            "Energia da Light",
            f"{current['Energia_Light']:.0f} kW"
        )

    # ========================================================
    # STATUS
    # ========================================================

    if current["Exportando"]:

        st.error("⚠ EXPORTANDO")

    else:

        st.success("✅ GRIDZERO")

    # ========================================================
    # GRÁFICO
    # ========================================================

    st.subheader("Fluxo de Potência")

    fig = go.Figure()

    # ========================================================
    # CARGA
    # ========================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Carga"],

        mode='lines',

        name='Carga',

        line=dict(
            color='#0066ff',
            width=3,
            shape='spline',
            smoothing=1.1
        )

    ))

    # ========================================================
    # GERAÇÃO LIMITADA
    # ========================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Geracao_Limitada"],

        mode='lines',

        name='Geração Limitada',

        line=dict(
            color='#18a558',
            width=3,
            shape='spline',
            smoothing=1.1
        )

    ))

    # ========================================================
    # GERAÇÃO CORTADA
    # ========================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Geracao_Cortada"],

        mode='lines',

        name='Geração Cortada',

        line=dict(
            color='#ff9900',
            width=3,
            dash='dash',
            shape='spline',
            smoothing=1.1
        )

    ))

    # ========================================================
    # ENERGIA CONSUMIDA DA LIGHT
    # ========================================================

    fig.add_trace(go.Scatter(

        x=replay_df["DataHora"],
        y=replay_df["Energia_Light"],

        mode='lines',

        name='Energia Consumida da Light',

        line=dict(
            color='#9933ff',
            width=3,
            shape='spline',
            smoothing=1.1
        )

    ))

    # ========================================================
    # LINHA ZERO DESTACADA
    # ========================================================

    fig.add_hline(

        y=0,

        line_width=4,

        line_color="black",

        opacity=0.9

    )

    # ========================================================
    # LAYOUT
    # ========================================================

    fig.update_layout(

        height=650,

        hovermode="x unified",

        plot_bgcolor="white",

        paper_bgcolor="white",

        xaxis=dict(

            title="Tempo",

            rangeslider=dict(
                visible=True
            ),

            showgrid=True,

            gridcolor='rgba(200,200,200,0.3)'
        ),

        yaxis=dict(

            title="Potência (kW)",

            zeroline=False,

            showgrid=True,

            gridcolor='rgba(200,200,200,0.3)'
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )

    )

    # ========================================================
    # EXIBE
    # ========================================================

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    st.subheader("Resumo Operacional")

    total_import = replay_df[
        replay_df["Energia_Light"] > 0
    ]["Energia_Light"].sum()

    total_cut = (
        replay_df["Geracao_Cortada"]
        - replay_df["Geracao_Limitada"]
    ).sum()

    max_cut = (
        replay_df["Geracao_Cortada"]
        - replay_df["Geracao_Limitada"]
    ).max()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Energia Consumida da Light",
            f"{total_import:.0f} kWh"
        )

    with col2:

        st.metric(
            "Energia Cortada",
            f"{total_cut:.0f} kWh"
        )

    with col3:

        st.metric(
            "Máximo Corte",
            f"{max_cut:.0f} kW"
        )

    # ========================================================
    # TABELA
    # ========================================================

    st.subheader("Dados Operacionais")

    st.dataframe(

        replay_df[
            [
                "DataHora",
                "Carga",
                "Geracao_Limitada",
                "Geracao_Cortada",
                "Energia_Light"
            ]
        ].tail(50),

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
