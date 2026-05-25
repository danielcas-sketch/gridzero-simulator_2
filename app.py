
from dataclasses import dataclass
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Simulador GridZero - Visual Limpo",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Simulador conceitual
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


def fmt_kw(value):
    return f"{value:,.0f} kW".replace(",", ".")


def breaker_text(is_open):
    return "ABERTO" if is_open else "FECHADO"


def init_defaults():
    defaults = {
        "time_s": 3.0,
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
        "load_g1": 420,
        "load_g2": 1550,
        "load_g3": 520,
        "pv_g1": 360,
        "pv_g2": 1450,
        "pv_g3": 360,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def set_preset(name):
    presets = {
        "normal": {
            "time_s": 3.0,
            "load_g1": 420, "load_g2": 1550, "load_g3": 520,
            "pv_g1": 360, "pv_g2": 1450, "pv_g3": 360,
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
            "time_s": 1.5,
            "load_g1": 90, "load_g2": 280, "load_g3": 100,
            "pv_g1": 380, "pv_g2": 1500, "pv_g3": 380,
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
        "camada_1": {
            "time_s": 4.0,
            "load_g1": 250, "load_g2": 600, "load_g3": 200,
            "pv_g1": 380, "pv_g2": 1500, "pv_g3": 380,
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
        "camada_2": {
            "time_s": 6.5,
            "load_g1": 250, "load_g2": 600, "load_g3": 200,
            "pv_g1": 380, "pv_g2": 1500, "pv_g3": 380,
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
        "camada_3": {
            "time_s": 9.5,
            "load_g1": 250, "load_g2": 600, "load_g3": 200,
            "pv_g1": 380, "pv_g2": 1500, "pv_g3": 380,
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
            "time_s": 2.5,
            "load_g1": 420, "load_g2": 1550, "load_g3": 520,
            "pv_g1": 360, "pv_g2": 1450, "pv_g3": 360,
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
    for k, v in presets[name].items():
        st.session_state[k] = v


def build_groups():
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
            pmt="PMT-06",
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
    factor = min(1.0, target_kw / total_available)
    return {g.key: clamp(g.available_kw * factor, 0, g.available_kw) for g in groups}


def simulate(groups):
    time_s = st.session_state.time_s
    total_load_kw = sum(g.load_kw for g in groups)
    total_available_kw = sum(g.available_kw for g in groups)

    import_bias_kw = st.session_state.import_bias_kw
    export_threshold_kw = st.session_state.export_threshold_kw

    control_active = (
        st.session_state.control_enabled
        and not st.session_state.gridzero_failure
        and not st.session_state.agc_asc_failure
    )

    target_total_kw = clamp(total_load_kw - import_bias_kw, 0, total_available_kw)
    target_by_group = distribute_target(groups, target_total_kw)

    events = []
    layer = "Nenhuma"
    mt_open = False
    global_bt_trip = False
    critical_failure = False

    if control_active:
        response_factor = clamp(time_s / 3.0, 0, 1)
        events.append("Camada 0 ativa: AGC-150 mede o ponto do PMT e ajusta o setpoint dos ASC-150.")
    else:
        response_factor = 0.0
        if not st.session_state.control_enabled:
            events.append("Controle GridZero desabilitado pelo usuário.")
        if st.session_state.gridzero_failure:
            events.append("Falha simulada no laço de controle GridZero.")
        if st.session_state.agc_asc_failure:
            events.append("Falha simulada na comunicação entre AGC-150 e ASC-150.")

    for g in groups:
        if control_active:
            g.final_kw = g.available_kw + (target_by_group[g.key] - g.available_kw) * response_factor
        else:
            g.final_kw = g.available_kw

    if st.session_state.agc_asc_failure and time_s >= 2.0:
        global_bt_trip = True
        layer = "Fail-safe comunicação AGC-ASC"
        events.append("Fail-safe por comunicação: abertura dos disjuntores BT / comando 0%.")

    for g in groups:
        if g.comm_failed:
            if time_s >= 2.0:
                g.bt_open = True
                layer = f"Falha comunicação {g.name}"
                events.append(f"{g.name}: ASC-150 detecta falha de comunicação e abre o disjuntor BT.")
            else:
                events.append(f"{g.name}: falha de comunicação detectada, aguardando temporização.")
            if time_s >= 5.0:
                events.append(f"{g.name}: inversores entram em fallback 0% por timeout Modbus.")

    pv_before_trip = sum(0 if g.bt_open else g.final_kw for g in groups)
    p_mains_before = total_load_kw - pv_before_trip
    export_before_kw = max(0, -p_mains_before)

    if export_before_kw > export_threshold_kw and not global_bt_trip:
        events.append(f"Exportação detectada no ponto do AGC-150: {export_before_kw:.0f} kW.")
        if time_s < 3.0:
            events.append("Sistema ainda dentro da janela de resposta do controle / seletividade.")
        elif time_s >= 3.0 and not st.session_state.layer1_failure:
            global_bt_trip = True
            layer = "Camada 1 - ANSI 32 do AGC-150"
            events.append("Camada 1 atuou: AGC-150 comanda abertura dos disjuntores BT.")
        elif time_s >= 6.0 and st.session_state.layer1_failure and not st.session_state.layer2_failure:
            global_bt_trip = True
            layer = "Camada 2 - Relé auxiliar ANSI 32"
            events.append("Camada 2 atuou: relé auxiliar abre os disjuntores BT.")
        elif time_s >= 9.0 and st.session_state.layer1_failure and st.session_state.layer2_failure and not st.session_state.layer3_failure:
            mt_open = True
            layer = "Camada 3 - Siemens 7SR1004"
            events.append("Camada 3 atuou: Siemens 7SR1004 abre o disjuntor de MT do PMT.")
        elif time_s >= 9.0 and st.session_state.layer1_failure and st.session_state.layer2_failure and st.session_state.layer3_failure:
            critical_failure = True
            layer = "Falha crítica simulada"
            events.append("Falha crítica: exportação persiste com todas as camadas falhando.")

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
        status = "Disjuntor MT aberto: o cliente foi desligado para proteger a rede."
        severity = "danger"
    else:
        for g in groups:
            if g.bt_open:
                g.final_kw = 0.0
        total_pv_final_kw = sum(g.final_kw for g in groups)
        p_mains = total_load_kw - total_pv_final_kw
        import_kw = max(0, p_mains)
        export_kw = max(0, -p_mains)
        if critical_failure:
            status = "Falha crítica simulada: exportação permaneceu sem atuação."
            severity = "danger"
        elif export_kw > export_threshold_kw:
            status = "Exportação detectada: sistema está atuando ou aguardando a próxima camada."
            severity = "warning"
        elif global_bt_trip or any(g.bt_open for g in groups):
            status = "Usina desconectada em BT: a carga continua alimentada pela Light."
            severity = "warning"
        elif import_kw <= import_bias_kw + 10:
            status = "GridZero estabilizado: pequena importação mantida como margem de segurança."
            severity = "ok"
        else:
            status = "Importação normal da rede: geração menor que o consumo."
            severity = "info"

    return {
        "groups": groups,
        "total_load_kw": total_load_kw,
        "total_available_kw": total_available_kw,
        "target_total_kw": target_total_kw,
        "total_pv_final_kw": total_pv_final_kw,
        "import_kw": import_kw,
        "export_kw": export_kw,
        "layer": layer,
        "events": events,
        "mt_open": mt_open,
        "global_bt_trip": global_bt_trip,
        "status": status,
        "severity": severity,
        "control_active": control_active,
    }


def status_html(text, severity):
    colors = {
        "ok": ("#e7f6ec", "#117a37"),
        "info": ("#eaf2ff", "#1b63d1"),
        "warning": ("#fff4e5", "#b26a00"),
        "danger": ("#fdecec", "#cf2e2e"),
    }
    bg, fg = colors.get(severity, colors["info"])
    return f"""
    <div style="
        background:{bg};
        color:{fg};
        border:1px solid {fg}30;
        border-radius:14px;
        padding:14px 18px;
        font-weight:700;
        font-size:18px;
        margin-bottom:12px;">
        {text}
    </div>
    """


def card_metric(title, value, color="#1f2937"):
    return f"""
    <div style="
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-radius:16px;
        padding:14px 16px;
        min-height:86px;">
        <div style="font-size:13px;color:#6b7280;margin-bottom:8px;">{title}</div>
        <div style="font-size:28px;font-weight:800;color:{color};">{value}</div>
    </div>
    """


def draw_overview(sim):
    groups = sim["groups"]
    blue = "#1f6feb"
    orange = "#f59e0b"
    green = "#16a34a"
    purple = "#8b5cf6"
    red = "#dc2626"
    gray = "#9ca3af"
    dark = "#1f2937"

    import_color = blue if sim["import_kw"] > 0 and not sim["mt_open"] else "#cbd5e1"
    export_color = red if sim["export_kw"] > 0 else "#e5e7eb"
    comm_color = purple if sim["control_active"] and not sim["global_bt_trip"] and not sim["mt_open"] else "#d1d5db"

    group_x = [150, 500, 850]
    branch_parts = []

    for idx, (g, x) in enumerate(zip(groups, group_x), start=1):
        bt_color = red if g.bt_open else "#334155"
        bt_fill = "#fff1f2" if g.bt_open else "#f8fafc"
        pv_color = gray if g.bt_open or sim["mt_open"] else orange
        load_value_color = green if not sim["mt_open"] else gray

        comm_path = f"M 615 215 C 615 250, {x+75} 250, {x+75} 280"
        branch_parts.append(f"""
        <!-- Grupo {idx} -->
        <rect x="{x}" y="300" width="150" height="72" rx="14" fill="#ffffff" stroke="#dbe3ec"/>
        <text x="{x+75}" y="325" text-anchor="middle" class="group-title">{g.pmt}</text>
        <text x="{x+75}" y="345" text-anchor="middle" class="small">{g.transformer}</text>
        <text x="{x+75}" y="362" text-anchor="middle" class="load-value">{fmt_kw(g.load_kw)}</text>

        <line x1="{x+75}" y1="260" x2="{x+75}" y2="300" stroke="{import_color}" stroke-width="5"/>
        <line x1="{x+75}" y1="372" x2="{x+75}" y2="402" stroke="{green if not sim['mt_open'] else gray}" stroke-width="5" marker-end="url(#arrowLoad)"/>

        <rect x="{x}" y="420" width="150" height="102" rx="14" fill="#fffaf2" stroke="#f8c56a"/>
        <text x="{x+75}" y="444" text-anchor="middle" class="group-title">{g.name}</text>
        <text x="{x+75}" y="462" text-anchor="middle" class="small">ASC-150 Solar · {g.inverters} inversores</text>
        <text x="{x+75}" y="485" text-anchor="middle" class="small">Disponível: {fmt_kw(g.available_kw)}</text>
        <text x="{x+75}" y="508" text-anchor="middle" class="pv-value">Efetiva: {fmt_kw(g.final_kw)}</text>

        <line x1="{x+75}" y1="420" x2="{x+75}" y2="392" stroke="{pv_color}" stroke-width="5" marker-end="url(#arrowPv)"/>

        <rect x="{x+38}" y="548" width="74" height="58" rx="12" fill="{bt_fill}" stroke="{bt_color}"/>
        <text x="{x+75}" y="571" text-anchor="middle" class="small">Disj. BT</text>
        <text x="{x+75}" y="590" text-anchor="middle" class="bt-state" fill="{bt_color}">{breaker_text(g.bt_open)}</text>

        <line x1="{x+75}" y1="548" x2="{x+75}" y2="522" stroke="{pv_color}" stroke-width="5"/>

        <path d="{comm_path}" fill="none" stroke="{comm_color}" stroke-width="3" stroke-dasharray="8 8" marker-end="url(#arrowComm)"/>
        """)

    svg = f"""
    <svg width="100%" height="650" viewBox="0 0 1150 650" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrowDownBlue" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
          <path d="M0,0 L12,6 L0,12 z" fill="{import_color}" />
        </marker>
        <marker id="arrowUpRed" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
          <path d="M12,0 L0,6 L12,12 z" fill="{export_color}" />
        </marker>
        <marker id="arrowPv" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
          <path d="M12,0 L0,6 L12,12 z" fill="{orange}" />
        </marker>
        <marker id="arrowLoad" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
          <path d="M0,0 L12,6 L0,12 z" fill="{green}" />
        </marker>
        <marker id="arrowComm" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
          <path d="M0,0 L12,6 L0,12 z" fill="{comm_color}" />
        </marker>
        <style>
          .title {{ font-family: Arial, sans-serif; font-size: 18px; font-weight: 800; fill: #111827; }}
          .small {{ font-family: Arial, sans-serif; font-size: 12px; fill: #6b7280; }}
          .label {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: 700; fill: #1f2937; }}
          .group-title {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: 800; fill: #0f172a; }}
          .load-value {{ font-family: Arial, sans-serif; font-size: 20px; font-weight: 800; fill: {load_value_color}; }}
          .pv-value {{ font-family: Arial, sans-serif; font-size: 20px; font-weight: 800; fill: #b45309; }}
          .bt-state {{ font-family: Arial, sans-serif; font-size: 13px; font-weight: 800; }}
        </style>
      </defs>

      <rect x="5" y="5" width="1140" height="640" rx="18" fill="#fbfcfe" stroke="#e5e7eb"/>
      <text x="28" y="35" class="title">Visão geral simplificada do sistema</text>
      <text x="28" y="58" class="small">Azul = energia da Light · Laranja = geração FV · Verde = consumo das cargas · Roxo tracejado = comunicação DEIF</text>

      <!-- Bloco esquerdo de medição -->
      <rect x="30" y="85" width="240" height="175" rx="16" fill="#ffffff" stroke="#dbe3ec"/>
      <text x="50" y="115" class="label">Ponto medido pelo AGC-150</text>
      <text x="50" y="148" class="small">Consumo total</text>
      <text x="190" y="148" text-anchor="end" class="label">{fmt_kw(sim["total_load_kw"])}</text>
      <text x="50" y="176" class="small">Geração FV efetiva</text>
      <text x="190" y="176" text-anchor="end" class="label">{fmt_kw(sim["total_pv_final_kw"])}</text>
      <text x="50" y="204" class="small">Importação da Light</text>
      <text x="190" y="204" text-anchor="end" class="label" fill="{blue}">{fmt_kw(sim["import_kw"])}</text>
      <text x="50" y="232" class="small">Exportação</text>
      <text x="190" y="232" text-anchor="end" class="label" fill="{red}">{fmt_kw(sim["export_kw"])}</text>

      <!-- Bloco direito de proteção -->
      <rect x="905" y="85" width="210" height="175" rx="16" fill="#ffffff" stroke="#dbe3ec"/>
      <text x="925" y="115" class="label">Camadas de atuação</text>
      <text x="925" y="145" class="small">0 — Controle contínuo DEIF (&lt; 3 s)</text>
      <text x="925" y="168" class="small">1 — ANSI 32 AGC-150: abre BT</text>
      <text x="925" y="191" class="small">2 — Relé auxiliar 32: abre BT</text>
      <text x="925" y="214" class="small">3 — Siemens 7SR1004: abre MT</text>
      <text x="925" y="243" class="small">Camada ativa: {sim["layer"]}</text>

      <!-- Cabeçalho central -->
      <rect x="505" y="72" width="140" height="54" rx="14" fill="#ffffff" stroke="#dbe3ec"/>
      <text x="575" y="95" text-anchor="middle" class="label">LIGHT</text>
      <text x="575" y="114" text-anchor="middle" class="small">13,8 kV / 60 Hz</text>

      <rect x="470" y="145" width="210" height="60" rx="14" fill="#ffffff" stroke="#dbe3ec"/>
      <text x="575" y="169" text-anchor="middle" class="label">Cabine Primária</text>
      <text x="575" y="188" text-anchor="middle" class="small">Entrada da concessionária</text>

      <line x1="575" y1="126" x2="575" y2="145" stroke="{import_color}" stroke-width="6" marker-end="url(#arrowDownBlue)"/>
      <line x1="600" y1="145" x2="600" y2="126" stroke="{export_color}" stroke-width="4" marker-end="url(#arrowUpRed)"/>

      <!-- PMT -->
      <rect x="360" y="220" width="430" height="108" rx="18" fill="#f8fafc" stroke="#cbd5e1"/>
      <text x="575" y="247" text-anchor="middle" class="title">PMT-02-G200</text>

      <rect x="390" y="262" width="120" height="48" rx="12" fill="#fff8ef" stroke="#f8c56a"/>
      <text x="450" y="281" text-anchor="middle" class="label">Siemens 7SR1004</text>
      <text x="450" y="299" text-anchor="middle" class="small">Proteção 32 / 67 / 59 / 27 / 81</text>

      <rect x="525" y="262" width="140" height="48" rx="12" fill="#eff6ff" stroke="#8ab4ff"/>
      <text x="595" y="281" text-anchor="middle" class="label">DEIF AGC-150</text>
      <text x="595" y="299" text-anchor="middle" class="small">Medição + GridZero</text>

      <rect x="680" y="262" width="78" height="48" rx="12" fill="#ffffff" stroke="{red if sim['mt_open'] else '#64748b'}"/>
      <text x="719" y="281" text-anchor="middle" class="label">Disj. MT</text>
      <text x="719" y="299" text-anchor="middle" class="small">{breaker_text(sim["mt_open"])}</text>

      <line x1="575" y1="205" x2="575" y2="220" stroke="{import_color}" stroke-width="6" marker-end="url(#arrowDownBlue)"/>
      <line x1="600" y1="220" x2="600" y2="205" stroke="{export_color}" stroke-width="4" marker-end="url(#arrowUpRed)"/>

      <!-- Barramento -->
      <line x1="225" y1="260" x2="360" y2="260" stroke="#94a3b8" stroke-width="2"/>
      <line x1="790" y1="260" x2="905" y2="260" stroke="#94a3b8" stroke-width="2"/>

      <line x1="225" y1="260" x2="225" y2="260" stroke="#94a3b8"/>
      <line x1="225" y1="260" x2="925" y2="260" stroke="{import_color if not sim['mt_open'] else '#cbd5e1'}" stroke-width="5"/>
      <line x1="225" y1="260" x2="925" y2="260" stroke="transparent"/>

      <!-- Ramais -->
      {''.join(branch_parts)}

      <!-- Legendas inferiores -->
      <rect x="28" y="590" width="1090" height="36" rx="10" fill="#ffffff" stroke="#e5e7eb"/>
      <text x="48" y="613" class="small">BT aberto = apenas a usina é desconectada · MT aberto = desligamento do cliente no PMT · Em operação normal, o GridZero mantém pequena importação da Light.</text>
    </svg>
    """
    return svg


def draw_timeline(sim):
    layer = sim["layer"]
    active0 = "#16a34a" if "GridZero" in sim["status"] or "Importação normal" in sim["status"] or sim["control_active"] else "#e5e7eb"
    active1 = "#f59e0b" if "Camada 1" in layer else "#e5e7eb"
    active2 = "#f59e0b" if "Camada 2" in layer else "#e5e7eb"
    active3 = "#dc2626" if "Camada 3" in layer else "#e5e7eb"
    fail = "#dc2626" if "crítica" in layer.lower() else "#e5e7eb"

    return f"""
    <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;padding:16px;">
      <div style="font-size:18px;font-weight:800;margin-bottom:14px;color:#111827;">Escalonamento das proteções</div>
      <div style="display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
        <div style="flex:1;min-width:170px;background:{active0};padding:14px;border-radius:14px;">
          <div style="font-weight:800;">Camada 0</div>
          <div style="font-size:13px;">Controle contínuo</div>
          <div style="font-size:12px;margin-top:8px;">0–3 s</div>
        </div>
        <div style="flex:1;min-width:170px;background:{active1};padding:14px;border-radius:14px;">
          <div style="font-weight:800;">Camada 1</div>
          <div style="font-size:13px;">ANSI 32 do AGC-150</div>
          <div style="font-size:12px;margin-top:8px;">3–4 s</div>
        </div>
        <div style="flex:1;min-width:170px;background:{active2};padding:14px;border-radius:14px;">
          <div style="font-weight:800;">Camada 2</div>
          <div style="font-size:13px;">Relé auxiliar 32</div>
          <div style="font-size:12px;margin-top:8px;">5–7 s</div>
        </div>
        <div style="flex:1;min-width:170px;background:{active3};padding:14px;border-radius:14px;">
          <div style="font-weight:800;">Camada 3</div>
          <div style="font-size:13px;">Siemens 7SR1004</div>
          <div style="font-size:12px;margin-top:8px;">8–10 s</div>
        </div>
        <div style="flex:1;min-width:170px;background:{fail};padding:14px;border-radius:14px;">
          <div style="font-weight:800;">Falha crítica</div>
          <div style="font-size:13px;">Somente se todas falharem</div>
          <div style="font-size:12px;margin-top:8px;">&gt; 9 s</div>
        </div>
      </div>
    </div>
    """


# ============================================================
# Interface
# ============================================================

init_defaults()

with st.sidebar:
    st.header("Cenários rápidos")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Normal", use_container_width=True):
            set_preset("normal")
        if st.button("Camada 1", use_container_width=True):
            set_preset("camada_1")
        if st.button("Camada 3", use_container_width=True):
            set_preset("camada_3")
    with c2:
        if st.button("Queda de carga", use_container_width=True):
            set_preset("queda_carga")
        if st.button("Camada 2", use_container_width=True):
            set_preset("camada_2")
        if st.button("Falha AGC-ASC", use_container_width=True):
            set_preset("falha_com")

    st.divider()
    st.subheader("Tempo")
    st.slider("Tempo após o evento (s)", 0.0, 12.0, step=0.5, key="time_s")

    st.subheader("Cargas")
    st.slider("Carga grupo 1 (kW)", 0, 800, step=10, key="load_g1")
    st.slider("Carga grupo 2 (kW)", 0, 2200, step=10, key="load_g2")
    st.slider("Carga grupo 3 (kW)", 0, 900, step=10, key="load_g3")

    st.subheader("Geração FV disponível")
    st.slider("Grupo FV 1 (kW)", 0, 400, step=10, key="pv_g1")
    st.slider("Grupo FV 2 (kW)", 0, 1600, step=10, key="pv_g2")
    st.slider("Grupo FV 3 (kW)", 0, 400, step=10, key="pv_g3")

    st.subheader("Parâmetros")
    st.slider("Import bias (kW)", 0, 120, step=5, key="import_bias_kw")
    st.slider("Limite de exportação (kW)", 0, 200, step=5, key="export_threshold_kw")
    st.checkbox("Controle GridZero habilitado", key="control_enabled")

    st.subheader("Falhas simuladas")
    st.checkbox("Falha no controle GridZero", key="gridzero_failure")
    st.checkbox("Falha comunicação AGC → ASC", key="agc_asc_failure")
    st.checkbox("Falha ASC → inversores no grupo 1", key="asc_inv_failure_g1")
    st.checkbox("Falha ASC → inversores no grupo 2", key="asc_inv_failure_g2")
    st.checkbox("Falha ASC → inversores no grupo 3", key="asc_inv_failure_g3")

    st.subheader("Falha forçada das camadas")
    st.checkbox("Camada 1 falhou", key="layer1_failure")
    st.checkbox("Camada 2 falhou", key="layer2_failure")
    st.checkbox("Camada 3 falhou", key="layer3_failure")

groups = build_groups()
sim = simulate(groups)

st.title("Simulador GridZero — versão visual simplificada")
st.caption("Interface reprojetada para leitura mais limpa, com menos cruzamento de setas e foco no entendimento do fluxo elétrico e das proteções.")

components.html(status_html(sim["status"], sim["severity"]), height=72)

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    components.html(card_metric("Consumo total", fmt_kw(sim["total_load_kw"])), height=100)
with m2:
    components.html(card_metric("Geração disponível", fmt_kw(sim["total_available_kw"])), height=100)
with m3:
    components.html(card_metric("Setpoint GridZero", fmt_kw(sim["target_total_kw"])), height=100)
with m4:
    components.html(card_metric("Importação da Light", fmt_kw(sim["import_kw"]), "#1f6feb"), height=100)
with m5:
    components.html(card_metric("Exportação", fmt_kw(sim["export_kw"]), "#dc2626"), height=100)

tab1, tab2, tab3 = st.tabs(["Visão geral", "Grupos e cargas", "Proteções e eventos"])

with tab1:
    components.html(draw_overview(sim), height=660, scrolling=False)

with tab2:
    st.subheader("Resumo dos grupos")
    cols = st.columns(3)
    for col, g in zip(cols, sim["groups"]):
        with col:
            st.markdown(
                f"""
                <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;padding:16px;">
                    <div style="font-size:18px;font-weight:800;color:#111827;">{g.name}</div>
                    <div style="color:#6b7280;margin-top:4px;">{g.pmt} · {g.transformer}</div>
                    <hr style="margin:12px 0;border:none;border-top:1px solid #eef2f7;">
                    <div><b>Carga local:</b> {fmt_kw(g.load_kw)}</div>
                    <div><b>FV disponível:</b> {fmt_kw(g.available_kw)}</div>
                    <div><b>FV efetiva:</b> {fmt_kw(g.final_kw)}</div>
                    <div><b>Inversores:</b> {g.inverters}</div>
                    <div><b>Disjuntor BT:</b> {breaker_text(g.bt_open)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.dataframe(
        [
            {
                "Grupo": g.name,
                "PMT": g.pmt,
                "Transformador": g.transformer,
                "Carga local (kW)": g.load_kw,
                "FV disponível (kW)": g.available_kw,
                "FV efetiva (kW)": round(g.final_kw, 1),
                "Disjuntor BT": breaker_text(g.bt_open),
            }
            for g in sim["groups"]
        ],
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    components.html(draw_timeline(sim), height=180)
    st.subheader("Linha de eventos")
    for event in sim["events"]:
        st.write("• " + event)

    st.markdown(
        """
        **Interpretação rápida**
        - **Azul:** potência importada da Light.
        - **Laranja:** geração fotovoltaica dos grupos de inversores.
        - **Verde:** consumo das cargas locais.
        - **Roxo tracejado:** comunicação e comando do sistema DEIF.
        - **BT aberto:** desliga apenas a usina daquele grupo (ou toda a usina, se trip global).
        - **MT aberto:** atua no PMT e interrompe o fornecimento do cliente.
        """
    )

st.caption(
    "Observação: este simulador continua sendo conceitual. O objetivo desta versão é melhorar a clareza visual para apresentação e entendimento operacional."
)
