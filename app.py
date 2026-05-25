
import math
from dataclasses import dataclass

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Simulador GridZero - Prologis",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# MODELO CONCEITUAL
# ------------------------------------------------------------
# Convenção no ponto medido pelo AGC-150 MAINS:
#   P_mains > 0  => importação da rede Light
#   P_mains = 0  => GridZero ideal
#   P_mains < 0  => exportação para a rede
#
# Este simulador não substitui estudo de proteção, parametrização
# oficial, estudo de seletividade ou validação do fabricante.
# Ele serve para apresentação visual do funcionamento do sistema.
# ============================================================


@dataclass
class PvGroup:
    key: str
    name: str
    pmt: str
    transformer: str
    capacity_kw: float
    inverters: int
    load_kw: float
    available_kw: float
    final_kw: float = 0.0
    bt_open: bool = False
    comm_failed: bool = False


def clamp(value, vmin, vmax):
    return max(vmin, min(value, vmax))


def init_defaults():
    defaults = {
        "scenario_name": "Operação normal GridZero",
        "load_g1": 420,
        "load_g2": 1550,
        "load_g3": 520,
        "pv_g1": 360,
        "pv_g2": 1450,
        "pv_g3": 360,
        "time_s": 0.0,
        "import_bias_kw": 40,
        "export_threshold_kw": 20,
        "control_enabled": True,
        "gridzero_failure": False,
        "agc_asc_failure": False,
        "asc_inv_failure_g1": False,
        "asc_inv_failure_g2": False,
        "asc_inv_failure_g3": False,
        "layer1_failure": False,
        "layer2_failure": False,
        "layer3_failure": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def set_preset(name):
    presets = {
        "normal": {
            "scenario_name": "Operação normal GridZero",
            "load_g1": 420,
            "load_g2": 1550,
            "load_g3": 520,
            "pv_g1": 360,
            "pv_g2": 1450,
            "pv_g3": 360,
            "time_s": 3.0,
            "control_enabled": True,
            "gridzero_failure": False,
            "agc_asc_failure": False,
            "asc_inv_failure_g1": False,
            "asc_inv_failure_g2": False,
            "asc_inv_failure_g3": False,
            "layer1_failure": False,
            "layer2_failure": False,
            "layer3_failure": False,
        },
        "queda_carga": {
            "scenario_name": "Queda brusca de carga",
            "load_g1": 90,
            "load_g2": 280,
            "load_g3": 100,
            "pv_g1": 380,
            "pv_g2": 1500,
            "pv_g3": 380,
            "time_s": 1.5,
            "control_enabled": True,
            "gridzero_failure": False,
            "agc_asc_failure": False,
            "asc_inv_failure_g1": False,
            "asc_inv_failure_g2": False,
            "asc_inv_failure_g3": False,
            "layer1_failure": False,
            "layer2_failure": False,
            "layer3_failure": False,
        },
        "falha_controle": {
            "scenario_name": "Falha do controle GridZero",
            "load_g1": 250,
            "load_g2": 600,
            "load_g3": 200,
            "pv_g1": 380,
            "pv_g2": 1500,
            "pv_g3": 380,
            "time_s": 4.0,
            "control_enabled": True,
            "gridzero_failure": True,
            "agc_asc_failure": False,
            "asc_inv_failure_g1": False,
            "asc_inv_failure_g2": False,
            "asc_inv_failure_g3": False,
            "layer1_failure": False,
            "layer2_failure": False,
            "layer3_failure": False,
        },
        "camada2": {
            "scenario_name": "Camada 1 falha, relé auxiliar atua",
            "load_g1": 250,
            "load_g2": 600,
            "load_g3": 200,
            "pv_g1": 380,
            "pv_g2": 1500,
            "pv_g3": 380,
            "time_s": 6.5,
            "control_enabled": True,
            "gridzero_failure": True,
            "agc_asc_failure": False,
            "asc_inv_failure_g1": False,
            "asc_inv_failure_g2": False,
            "asc_inv_failure_g3": False,
            "layer1_failure": True,
            "layer2_failure": False,
            "layer3_failure": False,
        },
        "camada3": {
            "scenario_name": "Camadas 1 e 2 falham, Siemens atua",
            "load_g1": 250,
            "load_g2": 600,
            "load_g3": 200,
            "pv_g1": 380,
            "pv_g2": 1500,
            "pv_g3": 380,
            "time_s": 9.5,
            "control_enabled": True,
            "gridzero_failure": True,
            "agc_asc_failure": False,
            "asc_inv_failure_g1": False,
            "asc_inv_failure_g2": False,
            "asc_inv_failure_g3": False,
            "layer1_failure": True,
            "layer2_failure": True,
            "layer3_failure": False,
        },
        "falha_com": {
            "scenario_name": "Falha de comunicação AGC → ASC",
            "load_g1": 420,
            "load_g2": 1550,
            "load_g3": 520,
            "pv_g1": 360,
            "pv_g2": 1450,
            "pv_g3": 360,
            "time_s": 2.5,
            "control_enabled": True,
            "gridzero_failure": False,
            "agc_asc_failure": True,
            "asc_inv_failure_g1": False,
            "asc_inv_failure_g2": False,
            "asc_inv_failure_g3": False,
            "layer1_failure": False,
            "layer2_failure": False,
            "layer3_failure": False,
        },
    }
    for key, value in presets[name].items():
        st.session_state[key] = value


def build_groups():
    # A distribuição segue a lógica visual do diagrama: três blocos FV controlados
    # por ASC-150 Solar, com cargas no mesmo sistema alimentado pelo PMT.
    return [
        PvGroup(
            key="g1",
            name="Grupo FV 01",
            pmt="PMT-06",
            transformer="TR-05-G200",
            capacity_kw=400,
            inverters=4,
            load_kw=st.session_state.load_g1,
            available_kw=st.session_state.pv_g1,
            comm_failed=st.session_state.asc_inv_failure_g1,
        ),
        PvGroup(
            key="g2",
            name="Grupo FV 02",
            pmt="PMT-06 / TR-07-CAG",
            transformer="TR-07-CAG",
            capacity_kw=1600,
            inverters=16,
            load_kw=st.session_state.load_g2,
            available_kw=st.session_state.pv_g2,
            comm_failed=st.session_state.asc_inv_failure_g2,
        ),
        PvGroup(
            key="g3",
            name="Grupo FV 03",
            pmt="PMT-08",
            transformer="TR-08-G200",
            capacity_kw=400,
            inverters=4,
            load_kw=st.session_state.load_g3,
            available_kw=st.session_state.pv_g3,
            comm_failed=st.session_state.asc_inv_failure_g3,
        ),
    ]


def distribute_target(groups, target_kw):
    total_available = sum(max(0, g.available_kw) for g in groups)
    if total_available <= 0 or target_kw <= 0:
        return {g.key: 0.0 for g in groups}

    # Distribui proporcionalmente à potência FV disponível, respeitando o disponível de cada grupo.
    factor = min(1.0, target_kw / total_available)
    return {g.key: clamp(g.available_kw * factor, 0, g.available_kw) for g in groups}


def simulate(groups):
    time_s = st.session_state.time_s
    total_load_kw = sum(g.load_kw for g in groups)
    total_pv_available_kw = sum(g.available_kw for g in groups)

    import_bias_kw = st.session_state.import_bias_kw
    export_threshold_kw = st.session_state.export_threshold_kw

    control_active = (
        st.session_state.control_enabled
        and not st.session_state.gridzero_failure
        and not st.session_state.agc_asc_failure
    )

    target_total_kw = clamp(total_load_kw - import_bias_kw, 0, total_pv_available_kw)
    target_by_group = distribute_target(groups, target_total_kw)

    events = []
    layer = "Nenhuma"
    mt_open = False
    global_bt_trip = False
    critical_failure = False

    if control_active:
        # Resposta simplificada: em até 3 s o DEIF leva a usina do valor disponível
        # para o setpoint GridZero.
        response_factor = clamp(time_s / 3.0, 0, 1)
        events.append("Camada 0 ativa: AGC-150 mede o ponto do PMT e ajusta o setpoint dos ASC-150.")
    else:
        response_factor = 0.0
        if not st.session_state.control_enabled:
            events.append("Controle GridZero desabilitado manualmente.")
        if st.session_state.gridzero_failure:
            events.append("Falha simulada no laço de controle: inversores permanecem no último valor disponível.")
        if st.session_state.agc_asc_failure:
            events.append("Falha simulada na comunicação AGC-150 → ASC-150.")

    for g in groups:
        if control_active:
            g.final_kw = g.available_kw + (target_by_group[g.key] - g.available_kw) * response_factor
        else:
            g.final_kw = g.available_kw

    # Falha de comunicação entre AGC e ASC: atuação fail-safe em ~2 s.
    if st.session_state.agc_asc_failure and time_s >= 2.0:
        global_bt_trip = True
        layer = "Falha comunicação AGC-ASC"
        events.append("Fail-safe: Id missing / fallback abre os disjuntores BT ou comanda 0% nos grupos FV.")

    # Falhas ASC → inversores: grupo afetado abre disjuntor BT em ~2 s e fallback em ~5 s.
    for g in groups:
        if g.comm_failed:
            if time_s < 2.0:
                events.append(f"{g.name}: falha ASC-150 → inversores detectada; aguardando lógica temporizada.")
            elif time_s >= 2.0:
                g.bt_open = True
                layer = f"Falha comunicação {g.name}"
                events.append(f"{g.name}: ASC-150 detecta Id missing e abre o disjuntor BT do grupo.")
            if time_s >= 5.0:
                events.append(f"{g.name}: inversores entram em fallback 0% por timeout Modbus.")

    # Potência antes das proteções temporizadas por exportação.
    pv_before_trip = sum(0 if g.bt_open else g.final_kw for g in groups)
    p_mains_before = total_load_kw - pv_before_trip
    export_before_kw = max(0, -p_mains_before)

    # Proteções por potência reversa.
    if export_before_kw > export_threshold_kw and not global_bt_trip:
        events.append(
            f"Exportação no ponto de medição: {export_before_kw:.0f} kW "
            f"(limite configurado: {export_threshold_kw:.0f} kW)."
        )

        if time_s < 3.0:
            events.append("Proteções de exportação ainda aguardando seletividade temporal.")
        elif time_s >= 3.0 and not st.session_state.layer1_failure:
            global_bt_trip = True
            layer = "Camada 1 - ANSI 32 AGC-150"
            events.append("Camada 1 atuou: AGC-150 comanda ASC-150 e abre os disjuntores BT dos inversores.")
        elif time_s >= 6.0 and st.session_state.layer1_failure and not st.session_state.layer2_failure:
            global_bt_trip = True
            layer = "Camada 2 - Relé auxiliar ANSI 32"
            events.append("Camada 2 atuou: relé auxiliar ANSI 32 abre os disjuntores BT dos inversores.")
        elif time_s >= 9.0 and st.session_state.layer1_failure and st.session_state.layer2_failure and not st.session_state.layer3_failure:
            mt_open = True
            layer = "Camada 3 - Siemens 7SR1004"
            events.append("Camada 3 atuou: Siemens 7SR1004 abre o disjuntor de média tensão do PMT.")
        elif time_s >= 9.0 and st.session_state.layer1_failure and st.session_state.layer2_failure and st.session_state.layer3_failure:
            critical_failure = True
            layer = "Falha crítica simulada"
            events.append("Falha crítica: exportação persiste e todas as camadas foram marcadas como falhas.")

    if global_bt_trip:
        for g in groups:
            g.bt_open = True

    if mt_open:
        for g in groups:
            g.bt_open = True
            g.final_kw = 0.0
        total_pv_final_kw = 0.0
        import_kw = 0.0
        export_kw = 0.0
        load_served_kw = 0.0
        status = "Disjuntor MT aberto: cliente desligado, rede da Light protegida."
        severity = "danger"
    else:
        for g in groups:
            if g.bt_open:
                g.final_kw = 0.0

        total_pv_final_kw = sum(g.final_kw for g in groups)
        p_mains = total_load_kw - total_pv_final_kw
        import_kw = max(0, p_mains)
        export_kw = max(0, -p_mains)
        load_served_kw = total_load_kw

        if critical_failure:
            status = "Falha crítica simulada: exportação permanece sem atuação."
            severity = "danger"
        elif export_kw > export_threshold_kw:
            status = "Exportação detectada: sistema aguardando ou escalando camadas."
            severity = "warning"
        elif global_bt_trip or any(g.bt_open for g in groups):
            status = "Usina desconectada em BT: carga segue alimentada pela Light."
            severity = "warning"
        elif import_kw <= import_bias_kw + 10:
            status = "GridZero controlando: pequena importação mantida como margem de segurança."
            severity = "ok"
        else:
            status = "Importação normal: geração menor que o consumo."
            severity = "info"

    return {
        "groups": groups,
        "total_load_kw": total_load_kw,
        "total_pv_available_kw": total_pv_available_kw,
        "target_total_kw": target_total_kw,
        "total_pv_final_kw": total_pv_final_kw,
        "import_kw": import_kw,
        "export_kw": export_kw,
        "load_served_kw": load_served_kw,
        "layer": layer,
        "events": events,
        "mt_open": mt_open,
        "global_bt_trip": global_bt_trip,
        "status": status,
        "severity": severity,
        "control_active": control_active,
        "critical_failure": critical_failure,
    }


def status_badge(text, severity):
    colors = {
        "ok": ("#e6f4ea", "#188038"),
        "info": ("#e8f0fe", "#1967d2"),
        "warning": ("#fff7e6", "#b06000"),
        "danger": ("#fce8e6", "#d93025"),
    }
    bg, fg = colors.get(severity, colors["info"])
    st.markdown(
        f"""
        <div style="
            background:{bg};
            color:{fg};
            border:1px solid {fg}33;
            border-radius:14px;
            padding:14px 18px;
            font-weight:700;
            font-size:18px;
            margin: 8px 0 16px 0;">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def arrow_width(value_kw):
    if value_kw <= 0:
        return 2
    return clamp(2 + value_kw / 250, 3, 10)


def fmt_kw(value):
    return f"{value:,.0f} kW".replace(",", ".")


def breaker_symbol(is_open):
    return "ABERTO" if is_open else "FECHADO"


def svg_diagram(sim):
    groups = sim["groups"]
    mt_open = sim["mt_open"]
    import_kw = sim["import_kw"]
    export_kw = sim["export_kw"]
    total_load_kw = sim["total_load_kw"]

    blue = "#1a73e8"
    orange = "#f29900"
    green = "#188038"
    purple = "#6f42c1"
    red = "#d93025"
    gray = "#9aa0a6"
    dark = "#1f2937"

    import_color = blue if import_kw > 0 and not mt_open else gray
    export_color = red if export_kw > 0 else "#d6dbe1"
    comm_color = purple if sim["control_active"] and not sim["global_bt_trip"] and not mt_open else gray
    mt_color = red if mt_open else dark
    mt_symbol = "╱" if mt_open else "│"

    # posições dos grupos
    x_positions = [120, 460, 800]
    branch_svgs = []
    for g, x in zip(groups, x_positions):
        pv_color = gray if g.bt_open or mt_open or g.final_kw <= 0 else orange
        load_color = gray if mt_open or g.load_kw <= 0 else green
        bt_color = red if g.bt_open else dark
        bt_symbol = "╱" if g.bt_open else "│"
        w_pv = arrow_width(g.final_kw)
        w_load = arrow_width(g.load_kw)

        branch_svgs.append(f"""
        <g>
            <rect x="{x}" y="470" width="260" height="72" fill="#ffffff" stroke="#c9d1d9" rx="12"/>
            <text x="{x+130}" y="492" text-anchor="middle" class="label-bold">{g.pmt}</text>
            <text x="{x+130}" y="513" text-anchor="middle" class="small">{g.transformer} · carga local</text>
            <text x="{x+130}" y="535" text-anchor="middle" class="metric-green">{fmt_kw(g.load_kw)}</text>

            <line x1="{x+130}" y1="440" x2="{x+130}" y2="470" stroke="{import_color}" stroke-width="4"/>
            <line x1="{x+130}" y1="542" x2="{x+130}" y2="578" stroke="{load_color}" stroke-width="{w_load}" marker-end="url(#arrowLoad)"/>

            <rect x="{x+22}" y="585" width="216" height="108" fill="#fffaf0" stroke="#f29900" rx="12"/>
            <text x="{x+130}" y="608" text-anchor="middle" class="label-bold">{g.name}</text>
            <text x="{x+130}" y="628" text-anchor="middle" class="small">ASC-150 Solar · {g.inverters} inversores</text>
            <text x="{x+130}" y="650" text-anchor="middle" class="small">Disponível: {fmt_kw(g.available_kw)}</text>
            <text x="{x+130}" y="672" text-anchor="middle" class="metric-orange">Efetiva: {fmt_kw(g.final_kw)}</text>

            <rect x="{x+88}" y="707" width="84" height="60" fill="#ffffff" stroke="{bt_color}" rx="10"/>
            <text x="{x+130}" y="728" text-anchor="middle" class="small">Disj. BT</text>
            <text x="{x+130}" y="749" text-anchor="middle" class="breaker">{bt_symbol}</text>
            <text x="{x+130}" y="765" text-anchor="middle" class="tiny">{breaker_symbol(g.bt_open)}</text>

            <line x1="{x+130}" y1="707" x2="{x+130}" y2="693" stroke="{pv_color}" stroke-width="{w_pv}" marker-end="url(#arrowPv)"/>
            <line x1="{x+130}" y1="585" x2="{x+130}" y2="542" stroke="{pv_color}" stroke-width="{w_pv}" marker-end="url(#arrowPv)"/>

            <path d="M610,330 C{650 if x>450 else 570},{380} {x+130},{400} {x+130},{585}"
                fill="none" stroke="{comm_color}" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arrowComm)"/>
        </g>
        """)

    svg = f"""
    <svg width="100%" height="820" viewBox="0 0 1180 820" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrowImport" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,8 L11,4 z" fill="{import_color}" />
        </marker>
        <marker id="arrowExport" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,8 L11,4 z" fill="{export_color}" />
        </marker>
        <marker id="arrowPv" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,8 L11,4 z" fill="{orange}" />
        </marker>
        <marker id="arrowLoad" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,8 L11,4 z" fill="{green}" />
        </marker>
        <marker id="arrowComm" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,8 L11,4 z" fill="{comm_color}" />
        </marker>
      </defs>

      <style>
        .box {{ fill:#ffffff; stroke:#c9d1d9; stroke-width:1.4; rx:14; }}
        .box-dark {{ fill:#f7f9fb; stroke:#6b7280; stroke-width:1.4; rx:14; }}
        .label {{ font-family: Arial, sans-serif; font-size:14px; fill:#1f2937; }}
        .label-bold {{ font-family: Arial, sans-serif; font-size:14px; font-weight:700; fill:#1f2937; }}
        .small {{ font-family: Arial, sans-serif; font-size:12px; fill:#4b5563; }}
        .tiny {{ font-family: Arial, sans-serif; font-size:10px; fill:#4b5563; }}
        .title {{ font-family: Arial, sans-serif; font-size:18px; font-weight:800; fill:#111827; }}
        .metric {{ font-family: Arial, sans-serif; font-size:17px; font-weight:800; fill:#111827; }}
        .metric-blue {{ font-family: Arial, sans-serif; font-size:17px; font-weight:800; fill:#1a73e8; }}
        .metric-red {{ font-family: Arial, sans-serif; font-size:17px; font-weight:800; fill:#d93025; }}
        .metric-green {{ font-family: Arial, sans-serif; font-size:16px; font-weight:800; fill:#188038; }}
        .metric-orange {{ font-family: Arial, sans-serif; font-size:16px; font-weight:800; fill:#b06000; }}
        .breaker {{ font-family: Arial, sans-serif; font-size:24px; font-weight:900; fill:#d93025; }}
      </style>

      <rect x="10" y="10" width="1160" height="800" fill="#fbfcfe" stroke="#e5e7eb" rx="18"/>

      <!-- Título e status -->
      <text x="40" y="45" class="title">Rede local — PMT, cargas, GridZero e proteções</text>
      <text x="40" y="70" class="small">Setas azuis: energia da Light · setas laranja: geração FV · setas verdes: carga · tracejado roxo: comunicação/controle DEIF</text>

      <!-- Grid Light -->
      <rect x="505" y="90" width="170" height="62" class="box"/>
      <text x="590" y="116" text-anchor="middle" class="title">LIGHT</text>
      <text x="590" y="138" text-anchor="middle" class="small">13,8 kV / 60 Hz</text>

      <rect x="470" y="185" width="240" height="68" class="box"/>
      <text x="590" y="212" text-anchor="middle" class="label-bold">Cabine Primária</text>
      <text x="590" y="234" text-anchor="middle" class="small">Entrada da concessionária</text>

      <!-- Fluxos principais -->
      <line x1="590" y1="152" x2="590" y2="185" stroke="{import_color}" stroke-width="{arrow_width(import_kw)}" marker-end="url(#arrowImport)"/>
      <line x1="590" y1="253" x2="590" y2="285" stroke="{import_color}" stroke-width="{arrow_width(import_kw)}" marker-end="url(#arrowImport)"/>

      <line x1="620" y1="285" x2="620" y2="253" stroke="{export_color}" stroke-width="{arrow_width(export_kw)}" marker-end="url(#arrowExport)"/>
      <line x1="620" y1="185" x2="620" y2="152" stroke="{export_color}" stroke-width="{arrow_width(export_kw)}" marker-end="url(#arrowExport)"/>

      <!-- PMT principal -->
      <rect x="335" y="285" width="510" height="155" class="box-dark"/>
      <text x="590" y="313" text-anchor="middle" class="title">PMT-02-G200</text>

      <rect x="365" y="335" width="155" height="78" fill="#fff7e6" stroke="#f29900" rx="12"/>
      <text x="442" y="358" text-anchor="middle" class="label-bold">Siemens 7SR1004</text>
      <text x="442" y="378" text-anchor="middle" class="small">32 / 67 / 59 / 59G</text>
      <text x="442" y="396" text-anchor="middle" class="small">81 / 27 / 50 / 51</text>

      <rect x="535" y="335" width="150" height="78" fill="#eef4ff" stroke="#1a73e8" rx="12"/>
      <text x="610" y="358" text-anchor="middle" class="label-bold">DEIF AGC-150</text>
      <text x="610" y="378" text-anchor="middle" class="small">Mains Controller</text>
      <text x="610" y="396" text-anchor="middle" class="small">Medição + GridZero</text>

      <rect x="705" y="335" width="110" height="78" fill="#ffffff" stroke="{mt_color}" rx="12"/>
      <text x="760" y="358" text-anchor="middle" class="label-bold">Disj. MT</text>
      <text x="760" y="382" text-anchor="middle" class="breaker">{mt_symbol}</text>
      <text x="760" y="402" text-anchor="middle" class="tiny">{breaker_symbol(mt_open)}</text>

      <line x1="590" y1="285" x2="590" y2="335" stroke="{import_color}" stroke-width="{arrow_width(import_kw)}" marker-end="url(#arrowImport)"/>
      <line x1="760" y1="413" x2="760" y2="440" stroke="{import_color}" stroke-width="4"/>
      <line x1="250" y1="440" x2="930" y2="440" stroke="{import_color}" stroke-width="4"/>

      <!-- Painel de medição -->
      <rect x="55" y="110" width="310" height="205" fill="#ffffff" stroke="#c9d1d9" rx="16"/>
      <text x="80" y="140" class="title">Ponto medido pelo AGC-150</text>
      <text x="80" y="174" class="label">Consumo total:</text>
      <text x="240" y="174" class="metric">{fmt_kw(total_load_kw)}</text>
      <text x="80" y="205" class="label">Geração FV efetiva:</text>
      <text x="240" y="205" class="metric">{fmt_kw(sim["total_pv_final_kw"])}</text>
      <text x="80" y="236" class="label">Importação Light:</text>
      <text x="240" y="236" class="metric-blue">{fmt_kw(import_kw)}</text>
      <text x="80" y="267" class="label">Exportação:</text>
      <text x="240" y="267" class="metric-red">{fmt_kw(export_kw)}</text>
      <text x="80" y="298" class="small">Camada atuante: {sim["layer"]}</text>

      <!-- Legenda de proteção -->
      <rect x="860" y="110" width="275" height="220" fill="#ffffff" stroke="#c9d1d9" rx="16"/>
      <text x="885" y="140" class="title">Camadas de atuação</text>
      <text x="885" y="174" class="small">0 — Controle contínuo DEIF (&lt; 3 s)</text>
      <text x="885" y="201" class="small">1 — ANSI 32 AGC-150: abre BT</text>
      <text x="885" y="228" class="small">2 — Relé auxiliar 32: abre BT</text>
      <text x="885" y="255" class="small">3 — Siemens 7SR1004: abre MT</text>
      <text x="885" y="292" class="small">BT aberto: só usina desconectada</text>
      <text x="885" y="315" class="small">MT aberto: cliente desligado</text>

      {''.join(branch_svgs)}

      <!-- Barra inferior com explicação -->
      <rect x="55" y="782" width="1070" height="1" fill="#e5e7eb"/>
    </svg>
    """
    return svg


# Inicialização e presets
init_defaults()

with st.sidebar:
    st.header("Cenários rápidos")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Normal", use_container_width=True):
            set_preset("normal")
        if st.button("Falha controle", use_container_width=True):
            set_preset("falha_controle")
        if st.button("Camada 3", use_container_width=True):
            set_preset("camada3")
    with c2:
        if st.button("Queda carga", use_container_width=True):
            set_preset("queda_carga")
        if st.button("Camada 2", use_container_width=True):
            set_preset("camada2")
        if st.button("Falha comunicação", use_container_width=True):
            set_preset("falha_com")

    st.divider()
    st.header("Tempo")
    st.slider("Tempo após o evento (s)", 0.0, 12.0, step=0.5, key="time_s")

    st.header("Cargas locais")
    st.slider("Carga no grupo 1 / TR-05-G200 (kW)", 0, 800, step=10, key="load_g1")
    st.slider("Carga no grupo 2 / TR-07-CAG (kW)", 0, 2200, step=10, key="load_g2")
    st.slider("Carga no grupo 3 / TR-08-G200 (kW)", 0, 900, step=10, key="load_g3")

    st.header("Geração FV disponível")
    st.slider("FV grupo 1 — 4 inversores (kW)", 0, 400, step=10, key="pv_g1")
    st.slider("FV grupo 2 — 16 inversores (kW)", 0, 1600, step=10, key="pv_g2")
    st.slider("FV grupo 3 — 4 inversores (kW)", 0, 400, step=10, key="pv_g3")

    st.header("Parâmetros")
    st.slider("Margem de importação / import bias (kW)", 0, 120, step=5, key="import_bias_kw")
    st.slider("Limite de exportação para atuação (kW)", 0, 200, step=5, key="export_threshold_kw")
    st.checkbox("Controle GridZero habilitado", key="control_enabled")

    st.header("Falhas simuladas")
    st.checkbox("Falha do controle GridZero", key="gridzero_failure")
    st.checkbox("Falha comunicação AGC-150 → ASC-150", key="agc_asc_failure")
    st.checkbox("Falha ASC → inversores no grupo 1", key="asc_inv_failure_g1")
    st.checkbox("Falha ASC → inversores no grupo 2", key="asc_inv_failure_g2")
    st.checkbox("Falha ASC → inversores no grupo 3", key="asc_inv_failure_g3")

    st.header("Forçar falha das camadas")
    st.checkbox("Camada 1 falhou", key="layer1_failure")
    st.checkbox("Camada 2 falhou", key="layer2_failure")
    st.checkbox("Camada 3 falhou", key="layer3_failure")


groups = build_groups()
sim = simulate(groups)

st.title("Simulador visual — GridZero, cargas e camadas de proteção")
st.caption(
    "Modelo demonstrativo baseado na arquitetura Light → Cabine Primária → PMT-02-G200 → transformadores/cargas → grupos de inversores controlados por DEIF."
)

status_badge(sim["status"], sim["severity"])

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Consumo total", fmt_kw(sim["total_load_kw"]))
m2.metric("Geração disponível", fmt_kw(sim["total_pv_available_kw"]))
m3.metric("Setpoint GridZero", fmt_kw(sim["target_total_kw"]))
m4.metric("Importação Light", fmt_kw(sim["import_kw"]))
m5.metric("Exportação", fmt_kw(sim["export_kw"]))

components.html(svg_diagram(sim), height=840, scrolling=False)

with st.expander("Linha de eventos da simulação", expanded=True):
    for event in sim["events"]:
        st.write("• " + event)

with st.expander("Como interpretar a tela"):
    st.markdown(
        """
        **Fluxo de potência**

        - A seta **azul** representa energia importada da Light para atender as cargas.
        - A seta **laranja** representa a geração fotovoltaica entrando no barramento/local das cargas.
        - A seta **vermelha** aparece quando existe exportação no ponto medido.
        - A linha **roxa tracejada** representa comunicação e comando do sistema DEIF.

        **Disjuntores**

        - **Disjuntor BT aberto:** apenas o grupo de inversores é desconectado; a carga continua alimentada pela Light.
        - **Disjuntor MT aberto:** o circuito do cliente é desligado no PMT, último recurso de proteção.

        **Lógica simplificada**

        ```text
        P_mains = Consumo total - Geração FV efetiva

        P_mains > 0  → importação da Light
        P_mains ≈ 0  → GridZero
        P_mains < 0  → exportação para a rede
        ```
        """
    )

with st.expander("Tabela dos grupos"):
    st.dataframe(
        [
            {
                "Grupo": g.name,
                "PMT / Transformador": f"{g.pmt} / {g.transformer}",
                "Inversores": g.inverters,
                "Carga local (kW)": g.load_kw,
                "FV disponível (kW)": g.available_kw,
                "FV efetiva (kW)": round(g.final_kw, 1),
                "Disjuntor BT": breaker_symbol(g.bt_open),
            }
            for g in sim["groups"]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Observação: este simulador é conceitual e serve para apresentação visual. "
    "Tempos, setpoints e atuação final devem ser validados no estudo de proteção, comissionamento e parametrização dos fabricantes."
)
