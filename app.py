import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import random
from dataclasses import dataclass

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="GridZero Simulator",
    layout="wide"
)

st.title("⚡ GridZero Simulator — DEIF + SolarEdge")
st.markdown("Simulação dinâmica do controle GridZero")

# ============================================================
# CLASSES
# ============================================================

@dataclass
class Inverter:

    id: int
    nominal_power: float = 250.0
    current_power: float = 0.0
    online: bool = True
    fallback_mode: bool = False

    def update(self, target_percent):

        if not self.online:
            self.current_power = 0
            return

        target_power = (
            self.nominal_power
            * target_percent
            / 100
        )

        ramp_rate = 50

        if self.current_power < target_power:
            self.current_power += ramp_rate

        elif self.current_power > target_power:
            self.current_power -= ramp_rate

        if self.current_power < 0:
            self.current_power = 0

        if self.current_power > self.nominal_power:
            self.current_power = self.nominal_power


class ASC150:

    def __init__(self, name, inverter_group):

        self.name = name
        self.inverters = inverter_group
        self.communication_ok = True

    def send_setpoint(self, percent):

        if not self.communication_ok:

            for inv in self.inverters:
                inv.fallback_mode = True
                inv.update(0)

            return

        for inv in self.inverters:
            inv.fallback_mode = False
            inv.update(percent)

    def total_power(self):

        return sum(
            inv.current_power
            for inv in self.inverters
        )


class AGC150:

    def __init__(self):

        self.setpoint_import = 20
        self.kp = 2.0

        self.export_alarm = False
        self.ansi32_trip = False

    def calculate(self, p_load, p_pv):

        p_grid = p_load - p_pv

        error = p_grid - self.setpoint_import

        correction = self.kp * error / 100

        return p_grid, correction

    def protection_logic(self, p_grid):

        self.export_alarm = False
        self.ansi32_trip = False

        if p_grid < 0:
            self.export_alarm = True

        if p_grid < -100:
            self.ansi32_trip = True


# ============================================================
# INICIALIZAÇÃO
# ============================================================

if "initialized" not in st.session_state:

    st.session_state.initialized = True

    inverters = [
        Inverter(i + 1)
        for i in range(24)
    ]

    group1 = inverters[0:4]
    group2 = inverters[4:20]
    group3 = inverters[20:24]

    st.session_state.asc1 = ASC150(
        "ASC-150 #1",
        group1
    )

    st.session_state.asc2 = ASC150(
        "ASC-150 #2",
        group2
    )

    st.session_state.asc3 = ASC150(
        "ASC-150 #3",
        group3
    )

    st.session_state.agc = AGC150()

    st.session_state.history = pd.DataFrame(
        columns=[
            "time",
            "load",
            "pv",
            "grid"
        ]
    )

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Controles")

manual_load = st.sidebar.slider(
    "Carga Mercado Livre (kW)",
    500,
    5000,
    3000
)

irradiance = st.sidebar.slider(
    "Irradiância Solar (%)",
    0,
    100,
    75
)

simulate_modbus_failure = st.sidebar.checkbox(
    "Falha comunicação Modbus"
)

simulate_ansi32 = st.sidebar.checkbox(
    "Forçar ANSI 32"
)

auto_mode = st.sidebar.checkbox(
    "Modo Automático",
    value=True
)

# ============================================================
# REFERÊNCIAS
# ============================================================

asc1 = st.session_state.asc1
asc2 = st.session_state.asc2
asc3 = st.session_state.asc3
agc = st.session_state.agc

# ============================================================
# CARGA
# ============================================================

if auto_mode:

    p_load = (
        manual_load
        + random.randint(-100, 100)
    )

else:

    p_load = manual_load

# ============================================================
# GERAÇÃO FV
# ============================================================

p_pv = (
    asc1.total_power()
    + asc2.total_power()
    + asc3.total_power()
)

# ============================================================
# CONTROLE GRIDZERO
# ============================================================

p_grid, correction = agc.calculate(
    p_load,
    p_pv
)

target = irradiance + correction

if target > 100:
    target = 100

if target < 0:
    target = 0

# ============================================================
# FALHA MODBUS
# ============================================================

if simulate_modbus_failure:

    asc1.communication_ok = False
    asc2.communication_ok = False
    asc3.communication_ok = False

else:

    asc1.communication_ok = True
    asc2.communication_ok = True
    asc3.communication_ok = True

# ============================================================
# ENVIO SETPOINTS
# ============================================================

asc1.send_setpoint(target)
asc2.send_setpoint(target)
asc3.send_setpoint(target)

# ============================================================
# RECALCULA
# ============================================================

p_pv = (
    asc1.total_power()
    + asc2.total_power()
    + asc3.total_power()
)

p_grid = p_load - p_pv

# ============================================================
# PROTEÇÕES
# ============================================================

agc.protection_logic(p_grid)

if simulate_ansi32:
    agc.ansi32_trip = True

if agc.ansi32_trip:

    for inv in (
        asc1.inverters
        + asc2.inverters
        + asc3.inverters
    ):

        inv.online = False

    p_pv = 0
    p_grid = p_load

# ============================================================
# HISTÓRICO
# ============================================================

new_row = pd.DataFrame({

    "time": [pd.Timestamp.now()],
    "load": [p_load],
    "pv": [p_pv],
    "grid": [p_grid]

})

st.session_state.history = pd.concat(
    [
        st.session_state.history,
        new_row
    ],
    ignore_index=True
)

if len(st.session_state.history) > 100:

    st.session_state.history = (
        st.session_state.history.iloc[-100:]
    )

# ============================================================
# KPIs
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Carga Mercado Livre",
        f"{p_load:.0f} kW"
    )

with col2:

    st.metric(
        "Geração FV",
        f"{p_pv:.0f} kW"
    )

with col3:

    st.metric(
        "Potência Rede",
        f"{p_grid:.0f} kW"
    )

with col4:

    if agc.ansi32_trip:
        st.error("ANSI 32 TRIP")

    elif agc.export_alarm:
        st.warning("EXPORTAÇÃO")

    else:
        st.success("GRIDZERO OK")

# ============================================================
# DIAGRAMA
# ============================================================

st.subheader("Arquitetura do Sistema")

diagram = f"""
LIGHT 13.8 kV
│
├── Potência Rede: {p_grid:.0f} kW
│
└── AGC-150 MAINS
    │
    ├── ASC-150 #1 → TR-05 → 4 Inversores
    ├── ASC-150 #2 → TR-07 → 16 Inversores
    └── ASC-150 #3 → TR-08 → 4 Inversores
"""

st.text(diagram)

# ============================================================
# GRÁFICOS
# ============================================================

st.subheader("Fluxo de Potência")

fig = go.Figure()

fig.add_trace(go.Scatter(

    x=st.session_state.history["time"],
    y=st.session_state.history["load"],
    mode='lines',
    name='Carga'

))

fig.add_trace(go.Scatter(

    x=st.session_state.history["time"],
    y=st.session_state.history["pv"],
    mode='lines',
    name='Geração FV'

))

fig.add_trace(go.Scatter(

    x=st.session_state.history["time"],
    y=st.session_state.history["grid"],
    mode='lines',
    name='Rede'

))

fig.update_layout(

    height=500,
    xaxis_title="Tempo",
    yaxis_title="Potência (kW)"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ============================================================
# INVERSORES
# ============================================================

st.subheader("Estado dos Inversores")

all_inverters = (
    asc1.inverters
    + asc2.inverters
    + asc3.inverters
)

for inv in all_inverters:

    col1, col2, col3, col4, col5 = st.columns([2,2,2,2,2])

    with col1:

        st.write(
            f"### INV-{inv.id:02d}"
        )

    with col2:

        st.metric(
            "Potência",
            f"{inv.current_power:.1f} kW"
        )

    with col3:

        if inv.online:
            st.success("🟢 ONLINE")
        else:
            st.error("🔴 OFFLINE")

    with col4:

        if inv.fallback_mode:
            st.warning("🟡 FALLBACK")
        else:
            st.success("🟢 NORMAL")

    with col5:

        new_state = st.toggle(
            f"Ligado {inv.id}",
            value=inv.online,
            key=f"toggle_{inv.id}"
        )

        inv.online = new_state

# ============================================================
# ALARMES
# ============================================================

st.subheader("Alarmes e Eventos")

if agc.export_alarm:

    st.warning(
        "⚠ Exportação detectada — AGC reduzindo geração"
    )

if simulate_modbus_failure:

    st.error(
        "❌ Falha comunicação Modbus — inversores em fallback"
    )

if agc.ansi32_trip:

    st.error(
        "🚨 ANSI 32 ATUADO — disjuntor geral aberto"
    )

# ============================================================
# AUTO REFRESH
# ============================================================

time.sleep(0.1)
st.rerun()
