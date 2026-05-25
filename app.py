
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador GridZero - Prologis", layout="wide")

# ------------------------------------------------------------
# Simulador conceitual GridZero
# Convenção de potência no ponto de medição:
#   P_mains > 0  => importação da rede Light para o cliente
#   P_mains = 0  => grid zero ideal
#   P_mains < 0  => exportação para a rede
# ------------------------------------------------------------

def clamp(value, vmin, vmax):
    return max(vmin, min(value, vmax))


def simulate(
    consumo_kw: float,
    geracao_disp_kw: float,
    tempo_s: float,
    import_bias_kw: float,
    export_threshold_kw: float,
    controle_habilitado: bool,
    falha_controle_gridzero: bool,
    falha_com_agc_asc: bool,
    falha_com_asc_inv: bool,
    falha_camada_1: bool,
    falha_camada_2: bool,
    falha_camada_3: bool,
):
    eventos = []
    camada_atuante = "Nenhuma"
    disj_bt_aberto = False
    disj_mt_aberto = False
    controle_ativo = controle_habilitado and not falha_controle_gridzero and not falha_com_agc_asc

    # Setpoint esperado pelo GridZero: manter pequena importação.
    setpoint_gridzero_kw = clamp(consumo_kw - import_bias_kw, 0, geracao_disp_kw)

    # Resposta dinâmica do controle: simula transição de até ~3 s.
    if controle_ativo:
        delay_controle_s = 3.0
        fator = clamp(tempo_s / delay_controle_s, 0, 1)
        geracao_pre_protecao_kw = geracao_disp_kw + (setpoint_gridzero_kw - geracao_disp_kw) * fator
        eventos.append("Camada 0: controle GridZero reduzindo setpoint dos inversores.")
    else:
        geracao_pre_protecao_kw = geracao_disp_kw
        if not controle_habilitado:
            eventos.append("Controle GridZero desabilitado pelo usuário.")
        if falha_controle_gridzero:
            eventos.append("Falha simulada no controle dinâmico GridZero.")
        if falha_com_agc_asc:
            eventos.append("Falha simulada de comunicação AGC-150 MAINS → ASC-150 Solar.")

    # Falhas de comunicação também podem levar a trip/fallback independente.
    if falha_com_agc_asc and tempo_s >= 2:
        disj_bt_aberto = True
        camada_atuante = "Falha comunicação AGC-ASC"
        eventos.append("Id missing / fallback: abertura dos disjuntores BT ou comando 0% nos ASCs.")

    if falha_com_asc_inv and tempo_s >= 2:
        disj_bt_aberto = True
        camada_atuante = "Falha comunicação ASC-Inversores"
        eventos.append("Id missing local do ASC-150: abertura do disjuntor BT do grupo afetado.")

    if falha_com_asc_inv and tempo_s >= 5:
        eventos.append("Fallback SolarEdge: inversores assumem 0% por timeout Modbus.")

    # Proteção por exportação sustentada.
    p_mains_pre = consumo_kw - geracao_pre_protecao_kw
    export_pre_kw = max(0, -p_mains_pre)

    if export_pre_kw > export_threshold_kw and not disj_bt_aberto:
        eventos.append(f"Exportação detectada: {export_pre_kw:.0f} kW acima do limite de {export_threshold_kw:.0f} kW.")

        if tempo_s >= 3 and not falha_camada_1:
            disj_bt_aberto = True
            camada_atuante = "Camada 1 - ANSI 32 AGC-150"
            eventos.append("Camada 1 atuou: AGC-150 comanda ASC-150 para abrir disjuntores BT.")
        elif tempo_s >= 6 and falha_camada_1 and not falha_camada_2:
            disj_bt_aberto = True
            camada_atuante = "Camada 2 - Relé auxiliar ANSI 32"
            eventos.append("Camada 2 atuou: relé auxiliar ANSI 32 abre os disjuntores BT.")
        elif tempo_s >= 9 and falha_camada_1 and falha_camada_2 and not falha_camada_3:
            disj_mt_aberto = True
            camada_atuante = "Camada 3 - Siemens 7SR1004"
            eventos.append("Camada 3 atuou: Siemens 7SR1004 abre o disjuntor de média tensão do PMT.")
        elif tempo_s >= 9 and falha_camada_1 and falha_camada_2 and falha_camada_3:
            eventos.append("Falha crítica simulada: exportação persiste e a Camada 3 não atuou.")
        else:
            eventos.append("Proteções temporizadas aguardando seletividade.")

    # Resultado final após atuação.
    if disj_mt_aberto:
        geracao_final_kw = 0
        importacao_kw = 0
        exportacao_kw = 0
        carga_atendida_kw = 0
        status_fornecimento = "Cliente desligado: disjuntor MT aberto"
    elif disj_bt_aberto:
        geracao_final_kw = 0
        importacao_kw = consumo_kw
        exportacao_kw = 0
        carga_atendida_kw = consumo_kw
        status_fornecimento = "Usina desconectada: carga atendida pela Light"
    else:
        geracao_final_kw = geracao_pre_protecao_kw
        p_mains = consumo_kw - geracao_final_kw
        importacao_kw = max(0, p_mains)
        exportacao_kw = max(0, -p_mains)
        carga_atendida_kw = consumo_kw
        if exportacao_kw > export_threshold_kw:
            status_fornecimento = "Exportação momentânea/sustentada em análise"
        elif importacao_kw <= import_bias_kw + 5:
            status_fornecimento = "GridZero controlando próximo ao setpoint"
        else:
            status_fornecimento = "Importação normal da rede"

    return {
        "setpoint_gridzero_kw": setpoint_gridzero_kw,
        "geracao_final_kw": geracao_final_kw,
        "importacao_kw": importacao_kw,
        "exportacao_kw": exportacao_kw,
        "carga_atendida_kw": carga_atendida_kw,
        "disj_bt_aberto": disj_bt_aberto,
        "disj_mt_aberto": disj_mt_aberto,
        "camada_atuante": camada_atuante,
        "eventos": eventos,
        "status_fornecimento": status_fornecimento,
        "controle_ativo": controle_ativo,
    }


def svg_diagram(sim):
    # Cores simples.
    grid_color = "#2f6fed" if sim["importacao_kw"] > 0 else "#b0b7c3"
    export_color = "#d93025" if sim["exportacao_kw"] > 0 else "#e0e0e0"
    solar_color = "#f29900" if sim["geracao_final_kw"] > 0 else "#b0b7c3"
    comm_color = "#6f42c1" if sim["controle_ativo"] and not sim["disj_bt_aberto"] and not sim["disj_mt_aberto"] else "#b0b7c3"
    bt_state = "ABERTO" if sim["disj_bt_aberto"] else "FECHADO"
    mt_state = "ABERTO" if sim["disj_mt_aberto"] else "FECHADO"

    # Símbolos de disjuntor.
    mt_symbol = "╱" if sim["disj_mt_aberto"] else "│"
    bt_symbol = "╱" if sim["disj_bt_aberto"] else "│"

    return f"""
    <svg width="100%" height="660" viewBox="0 0 1180 660" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrowGrid" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="{grid_color}" />
        </marker>
        <marker id="arrowExport" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="{export_color}" />
        </marker>
        <marker id="arrowSolar" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="{solar_color}" />
        </marker>
        <marker id="arrowComm" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="{comm_color}" />
        </marker>
      </defs>

      <style>
        .box {{ fill: #ffffff; stroke: #2b3440; stroke-width: 1.4; rx: 10; }}
        .title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: 700; fill: #17202a; }}
        .label {{ font-family: Arial, sans-serif; font-size: 13px; fill: #17202a; }}
        .small {{ font-family: Arial, sans-serif; font-size: 11px; fill: #34495e; }}
        .metric {{ font-family: Arial, sans-serif; font-size: 18px; font-weight: 700; fill: #17202a; }}
        .danger {{ fill: #d93025; font-weight: 700; }}
        .ok {{ fill: #188038; font-weight: 700; }}
      </style>

      <!-- GRID E CABINE -->
      <rect x="500" y="20" width="180" height="55" class="box"/>
      <text x="590" y="43" text-anchor="middle" class="title">LIGHT</text>
      <text x="590" y="62" text-anchor="middle" class="small">13,8 kV / 60 Hz</text>

      <rect x="470" y="105" width="240" height="65" class="box"/>
      <text x="590" y="132" text-anchor="middle" class="title">Cabine Primária</text>
      <text x="590" y="152" text-anchor="middle" class="small">Entrada / medição concessionária</text>

      <!-- PMT -->
      <rect x="390" y="205" width="400" height="150" class="box"/>
      <text x="590" y="230" text-anchor="middle" class="title">PMT-02-G200</text>

      <rect x="420" y="250" width="135" height="70" fill="#fff7e6" stroke="#f29900" rx="8"/>
      <text x="487" y="273" text-anchor="middle" class="label">Siemens 7SR1004</text>
      <text x="487" y="292" text-anchor="middle" class="small">32 / 67 / 59 / 27 / 81</text>
      <text x="487" y="310" text-anchor="middle" class="small">Camada 3</text>

      <rect x="625" y="250" width="135" height="70" fill="#eef4ff" stroke="#2f6fed" rx="8"/>
      <text x="692" y="273" text-anchor="middle" class="label">DEIF AGC-150</text>
      <text x="692" y="292" text-anchor="middle" class="small">Mains Controller</text>
      <text x="692" y="310" text-anchor="middle" class="small">Medição + ANSI 32</text>

      <!-- Disjuntor MT -->
      <rect x="545" y="365" width="90" height="58" fill="#ffffff" stroke="#2b3440" rx="8"/>
      <text x="590" y="385" text-anchor="middle" class="label">Disj. MT</text>
      <text x="590" y="407" text-anchor="middle" class="metric">{mt_symbol}</text>
      <text x="590" y="422" text-anchor="middle" class="small">{mt_state}</text>

      <!-- Linhas de potência importação -->
      <line x1="590" y1="75" x2="590" y2="105" stroke="{grid_color}" stroke-width="5" marker-end="url(#arrowGrid)"/>
      <line x1="590" y1="170" x2="590" y2="205" stroke="{grid_color}" stroke-width="5" marker-end="url(#arrowGrid)"/>
      <line x1="590" y1="355" x2="590" y2="365" stroke="{grid_color}" stroke-width="5" marker-end="url(#arrowGrid)"/>

      <!-- Linha de exportação, sentido contrário -->
      <line x1="615" y1="205" x2="615" y2="170" stroke="{export_color}" stroke-width="5" marker-end="url(#arrowExport)"/>
      <line x1="615" y1="105" x2="615" y2="75" stroke="{export_color}" stroke-width="5" marker-end="url(#arrowExport)"/>

      <!-- Barramento BT/MT para transformadores -->
      <line x1="590" y1="423" x2="590" y2="455" stroke="{grid_color}" stroke-width="4"/>
      <line x1="250" y1="455" x2="930" y2="455" stroke="{grid_color}" stroke-width="4"/>

      <!-- Transformadores e inversores -->
      <g>
        <rect x="140" y="480" width="220" height="55" class="box"/>
        <text x="250" y="503" text-anchor="middle" class="label">TR-05-G200</text>
        <text x="250" y="522" text-anchor="middle" class="small">4 inversores SE100K</text>
        <rect x="170" y="548" width="160" height="50" fill="#fff7e6" stroke="#f29900" rx="8"/>
        <text x="250" y="567" text-anchor="middle" class="label">QGBT Inversores</text>
        <text x="250" y="590" text-anchor="middle" class="metric">{bt_symbol}</text>
      </g>

      <g>
        <rect x="480" y="480" width="220" height="55" class="box"/>
        <text x="590" y="503" text-anchor="middle" class="label">TR-07-CAG</text>
        <text x="590" y="522" text-anchor="middle" class="small">16 inversores SE100K</text>
        <rect x="510" y="548" width="160" height="50" fill="#fff7e6" stroke="#f29900" rx="8"/>
        <text x="590" y="567" text-anchor="middle" class="label">QGBT Inversores</text>
        <text x="590" y="590" text-anchor="middle" class="metric">{bt_symbol}</text>
      </g>

      <g>
        <rect x="820" y="480" width="220" height="55" class="box"/>
        <text x="930" y="503" text-anchor="middle" class="label">TR-08-G200</text>
        <text x="930" y="522" text-anchor="middle" class="small">4 inversores SE100K</text>
        <rect x="850" y="548" width="160" height="50" fill="#fff7e6" stroke="#f29900" rx="8"/>
        <text x="930" y="567" text-anchor="middle" class="label">QGBT Inversores</text>
        <text x="930" y="590" text-anchor="middle" class="metric">{bt_symbol}</text>
      </g>

      <line x1="250" y1="455" x2="250" y2="480" stroke="{grid_color}" stroke-width="4"/>
      <line x1="590" y1="455" x2="590" y2="480" stroke="{grid_color}" stroke-width="4"/>
      <line x1="930" y1="455" x2="930" y2="480" stroke="{grid_color}" stroke-width="4"/>

      <!-- Fluxo solar subindo para carga / barramento -->
      <line x1="250" y1="548" x2="250" y2="535" stroke="{solar_color}" stroke-width="5" marker-end="url(#arrowSolar)"/>
      <line x1="590" y1="548" x2="590" y2="535" stroke="{solar_color}" stroke-width="5" marker-end="url(#arrowSolar)"/>
      <line x1="930" y1="548" x2="930" y2="535" stroke="{solar_color}" stroke-width="5" marker-end="url(#arrowSolar)"/>

      <!-- Comunicação -->
      <path d="M692,320 C650,390 410,420 250,548" fill="none" stroke="{comm_color}" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#arrowComm)"/>
      <path d="M692,320 C650,410 590,430 590,548" fill="none" stroke="{comm_color}" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#arrowComm)"/>
      <path d="M692,320 C750,410 930,430 930,548" fill="none" stroke="{comm_color}" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#arrowComm)"/>
      <text x="835" y="345" class="small">Comunicação GridZero / setpoint</text>

      <!-- Carga -->
      <rect x="875" y="220" width="210" height="95" fill="#f7f9fb" stroke="#2b3440" rx="10"/>
      <text x="980" y="247" text-anchor="middle" class="title">Carga MELI</text>
      <text x="980" y="274" text-anchor="middle" class="metric">{sim["carga_atendida_kw"]:.0f} kW</text>
      <text x="980" y="296" text-anchor="middle" class="small">consumo atendido</text>
      <line x1="790" y1="285" x2="875" y2="285" stroke="{grid_color}" stroke-width="5" marker-end="url(#arrowGrid)"/>

      <!-- Métricas -->
      <rect x="70" y="50" width="305" height="165" fill="#f7f9fb" stroke="#d0d7de" rx="12"/>
      <text x="90" y="80" class="title">Ponto de medição AGC-150</text>
      <text x="90" y="112" class="label">Importação Light: <tspan class="ok">{sim["importacao_kw"]:.0f} kW</tspan></text>
      <text x="90" y="140" class="label">Exportação: <tspan class="danger">{sim["exportacao_kw"]:.0f} kW</tspan></text>
      <text x="90" y="168" class="label">Geração FV efetiva: {sim["geracao_final_kw"]:.0f} kW</text>
      <text x="90" y="196" class="label">Camada atuante: {sim["camada_atuante"]}</text>

      <!-- Legenda -->
      <rect x="70" y="235" width="305" height="95" fill="#ffffff" stroke="#d0d7de" rx="12"/>
      <line x1="90" y1="260" x2="140" y2="260" stroke="#2f6fed" stroke-width="5" marker-end="url(#arrowGrid)"/>
      <text x="155" y="264" class="small">Fluxo de importação / alimentação da carga</text>
      <line x1="90" y1="285" x2="140" y2="285" stroke="#d93025" stroke-width="5" marker-end="url(#arrowExport)"/>
      <text x="155" y="289" class="small">Fluxo de exportação para a rede</text>
      <line x1="90" y1="310" x2="140" y2="310" stroke="#6f42c1" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#arrowComm)"/>
      <text x="155" y="314" class="small">Comunicação / comando DEIF</text>
    </svg>
    """


st.title("Simulador GridZero e Proteção contra Exportação")
st.caption("Modelo conceitual para demonstrar o comportamento do controle DEIF, fluxo de energia e atuação das camadas de proteção.")

with st.sidebar:
    st.header("Entradas do cenário")
    consumo_kw = st.slider("Consumo do Mercado Livre (kW)", 0, 3000, 1200, 50)
    geracao_disp_kw = st.slider("Geração FV disponível (kW)", 0, 2400, 1500, 50)
    tempo_s = st.slider("Tempo após o evento (s)", 0.0, 12.0, 0.0, 0.5)

    st.header("Parâmetros GridZero")
    import_bias_kw = st.slider("Margem de importação / import bias (kW)", 0, 100, 40, 5)
    export_threshold_kw = st.slider("Limite de exportação para disparo (kW)", 0, 150, 20, 5)
    controle_habilitado = st.checkbox("Controle GridZero habilitado", True)

    st.header("Falhas simuladas")
    falha_controle_gridzero = st.checkbox("Falha no controle dinâmico GridZero", False)
    falha_com_agc_asc = st.checkbox("Falha comunicação AGC-150 → ASC-150", False)
    falha_com_asc_inv = st.checkbox("Falha comunicação ASC-150 → inversores", False)

    st.header("Falhas das camadas")
    falha_camada_1 = st.checkbox("Camada 1 falhou (ANSI 32 do AGC-150)", False)
    falha_camada_2 = st.checkbox("Camada 2 falhou (relé auxiliar ANSI 32)", False)
    falha_camada_3 = st.checkbox("Camada 3 falhou (Siemens 7SR1004)", False)

sim = simulate(
    consumo_kw=consumo_kw,
    geracao_disp_kw=geracao_disp_kw,
    tempo_s=tempo_s,
    import_bias_kw=import_bias_kw,
    export_threshold_kw=export_threshold_kw,
    controle_habilitado=controle_habilitado,
    falha_controle_gridzero=falha_controle_gridzero,
    falha_com_agc_asc=falha_com_agc_asc,
    falha_com_asc_inv=falha_com_asc_inv,
    falha_camada_1=falha_camada_1,
    falha_camada_2=falha_camada_2,
    falha_camada_3=falha_camada_3,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Setpoint GridZero", f"{sim['setpoint_gridzero_kw']:.0f} kW")
col2.metric("Geração FV efetiva", f"{sim['geracao_final_kw']:.0f} kW")
col3.metric("Importação da Light", f"{sim['importacao_kw']:.0f} kW")
col4.metric("Exportação", f"{sim['exportacao_kw']:.0f} kW")

st.subheader(sim["status_fornecimento"])
components.html(svg_diagram(sim), height=680, scrolling=False)

with st.expander("Linha de eventos / lógica de atuação", expanded=True):
    for evento in sim["eventos"]:
        st.write("• " + evento)

with st.expander("Interpretação técnica"):
    st.markdown(
        """
        - **Ponto de medição:** potência medida pelo AGC-150 MAINS no PMT.
        - **P > 0:** cliente importa energia da Light.
        - **P ≈ 0:** operação GridZero.
        - **P < 0:** exportação para a rede.
        - **Camada 0:** controle contínuo reduz o setpoint dos inversores.
        - **Camada 1:** ANSI 32 do AGC-150 comanda os ASC-150 para abertura dos disjuntores BT.
        - **Camada 2:** relé auxiliar ANSI 32 atua nos disjuntores BT.
        - **Camada 3:** Siemens 7SR1004 atua no disjuntor de média tensão do PMT.
        """
    )
