#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
STREAMLIT APP - SIMULADOR GRIDZERO
Prologis Dutra II / Mercado Livre
================================================================================
Como executar:
    streamlit run app_streamlit.py
================================================================================
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np
from simulador_core import GridZeroSimulator

# ================================================================================
# CONFIGURAÇÃO DA PÁGINA
# ================================================================================
st.set_page_config(
    page_title="GridZero Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================================
# CSS CUSTOMIZADO
# ================================================================================
st.markdown("""
<style>
    .main { background-color: #0a0e27; }
    .stSlider > div > div > div { color: #00d4ff; }
    .camada-ativa {
        background: linear-gradient(90deg, rgba(255,100,0,0.2) 0%, rgba(255,0,0,0.1) 100%);
        border-left: 4px solid #ff6600;
        padding: 10px;
        border-radius: 8px;
        margin: 4px 0;
    }
    .camada-inativa {
        background: rgba(30,30,50,0.5);
        border-left: 4px solid #444466;
        padding: 10px;
        border-radius: 8px;
        margin: 4px 0;
        opacity: 0.6;
    }
    .status-box {
        background: #1a1f3a;
        border: 2px solid;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1em;
    }
    .metric-card {
        background: #111936;
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #222244;
    }
    .disjuntor-fechado { color: #00ff88; font-weight: bold; }
    .disjuntor-aberto { color: #ff4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================================================================================
# INICIALIZAÇÃO DO ESTADO
# ================================================================================
if 'sim' not in st.session_state:
    st.session_state.sim = GridZeroSimulator()
    st.session_state.sim.passo()

sim = st.session_state.sim

# ================================================================================
# TÍTULO
# ================================================================================
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title("⚡ Simulador GridZero")
    st.markdown("**Prologis Dutra II** | Cliente: *Mercado Livre* | Concessionária: Light 13,8kV")
    st.caption("Baseado no Memorial Técnico SolarVolt — 4 camadas de proteção + proteções nativas")

# ================================================================================
# SIDEBAR — CONTROLES
# ================================================================================
st.sidebar.header("🎛️ Controles do Sistema")

st.sidebar.subheader("Potências")
geracao = st.sidebar.slider(
    "☀️ Geração Solar (kW)", 0, 2400, int(sim.geracao_solar), 50,
    help="Potência total dos 24 inversores SE100K"
)
consumo = st.sidebar.slider(
    "🏭 Consumo MELI (kW)", 0, 3000, int(sim.consumo_meli), 50,
    help="Demanda do centro de distribuição"
)

st.sidebar.divider()
st.sidebar.subheader("Falhas Simuladas")
col_f1, col_f2 = st.sidebar.columns(2)
with col_f1:
    falha_agc = st.toggle("Falha AGC-150", sim.falha_agc, help="Falha no controlador DEIF")
    falha_com = st.toggle("Falha AGC↔ASC", sim.falha_com_agc_asc, help="Perda de comunicação entre AGC e ASC")
with col_f2:
    falha_asc = st.toggle("Falha ASC↔Inv", sim.falha_com_asc_inv, help="Perda de comunicação entre ASC e inversores")

st.sidebar.divider()
st.sidebar.subheader("⚡ Cenários Rápidos")
cenario = st.sidebar.selectbox(
    "Selecione um cenário:",
    [
        "Manual (usar sliders)",
        "1. Dia Nublado — Gen 400 / Load 1500",
        "2. Pico Solar — Gen 2200 / Load 1500",
        "3. Carga Mínima — Gen 1000 / Load 300",
        "4. Carga Máxima — Gen 2000 / Load 2800",
        "5. Falha COM + Exportação — Gen 2000 / Load 300",
        "6. Falha AGC + Crítico — Gen 2500 / Load 100",
    ]
)

if st.sidebar.button("🔄 RESET TOTAL", use_container_width=True, type="primary"):
    sim.resetar()
    st.rerun()

# Aplicar cenário
if cenario.startswith("1."):
    geracao, consumo, falha_agc, falha_com, falha_asc = 400, 1500, False, False, False
elif cenario.startswith("2."):
    geracao, consumo, falha_agc, falha_com, falha_asc = 2200, 1500, False, False, False
elif cenario.startswith("3."):
    geracao, consumo, falha_agc, falha_com, falha_asc = 1000, 300, False, False, False
elif cenario.startswith("4."):
    geracao, consumo, falha_agc, falha_com, falha_asc = 2000, 2800, False, False, False
elif cenario.startswith("5."):
    geracao, consumo, falha_agc, falha_com, falha_asc = 2000, 300, False, True, False
elif cenario.startswith("6."):
    geracao, consumo, falha_agc, falha_com, falha_asc = 2500, 100, True, False, False

# Atualizar estado do simulador
sim.geracao_solar = float(geracao)
sim.consumo_meli = float(consumo)
sim.falha_agc = falha_agc
sim.falha_com_agc_asc = falha_com
sim.falha_com_asc_inv = falha_asc
est = sim.passo()

# ================================================================================
# MÉTRICAS PRINCIPAIS
# ================================================================================
st.divider()
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(
        label="☀️ Geração Efetiva",
        value=f"{est['geracao_efetiva']:.0f} kW",
        delta=f"Solicitada: {est['geracao_solar']:.0f} kW" if est['geracao_efetiva'] != est['geracao_solar'] else None,
        delta_color="inverse"
    )
with col_m2:
    st.metric(
        label="🏭 Consumo MELI",
        value=f"{est['consumo_meli']:.0f} kW"
    )
with col_m3:
    fluxo = est['fluxo_rede']
    if fluxo > 0:
        label_m3 = "↳ Importando da Rede"
        color_m3 = "normal"
    elif fluxo < 0:
        label_m3 = "⚠ EXPORTANDO (Proibido!)"
        color_m3 = "inverse"
    else:
        label_m3 = "✓ Balanceado"
        color_m3 = "off"
    st.metric(
        label=label_m3,
        value=f"{abs(fluxo):.0f} kW",
        delta=f"{fluxo:+.0f} kW" if fluxo != 0 else "0 kW",
        delta_color=color_m3
    )
with col_m4:
    st.metric(
        label="🎯 Setpoint DEIF",
        value=f"{est['setpoint']:.0f} kW"
    )

# ================================================================================
# STATUS GERAL
# ================================================================================
st.markdown(
    f'<div class="status-box" style="border-color: {est["cor"]}; color: {est["cor"]};">'
    f'{est["mensagem"]}'
    f'</div>',
    unsafe_allow_html=True
)

# ================================================================================
# LAYOUT PRINCIPAL: DIAGRAMA + CAMADAS
# ================================================================================
col_diag, col_camadas = st.columns([3, 2])

# -------------------------------------------------------------------------------
# DIAGRAMA UNIFILAR (matplotlib)
# -------------------------------------------------------------------------------
with col_diag:
    st.subheader("📐 Diagrama Unifilar")

    fig, ax = plt.subplots(figsize=(10, 8), facecolor='#0a0e27')
    ax.set_facecolor('#111936')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    C_GRID = '#00d4ff'
    C_SOLAR = '#00ff88'
    C_CARGA = '#ffaa00'
    C_EXPORT = '#ff3333'
    C_NEUTRO = '#555566'
    C_CONTROL = '#e040fb'
    C_OK = '#4caf50'
    C_DANGER = '#f44336'

    def draw_box(ax, x, y, w, h, titulo, subtitulo, cor, fontsize=8, sub2=None):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3",
                               facecolor='#1a1f3a', edgecolor=cor, linewidth=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 2.5, titulo, ha='center', va='center',
               color=cor, fontsize=fontsize, fontweight='bold')
        ax.text(x + w/2, y + h - 6, subtitulo, ha='center', va='center',
               color='#aaaaaa', fontsize=6)
        if sub2:
            ax.text(x + w/2, y + h - 9, sub2, ha='center', va='center',
                   color='#888888', fontsize=5)

    def draw_dj(ax, x, y, fechado, label, cor_base):
        cor = cor_base if fechado else C_DANGER
        ax.plot([x-2, x+2], [y, y], color='#444466', linewidth=2)
        if fechado:
            ax.plot([x-1.5, x+1.5], [y, y], color=cor, linewidth=4)
            ax.text(x, y-3, f'{label}\nFECHADO', ha='center', va='top',
                   color=C_OK, fontsize=5, fontweight='bold')
        else:
            ax.plot([x-1.5, x], [y, y+2], color=cor, linewidth=3)
            ax.plot([x, x+1.5], [y+2, y], color=cor, linewidth=3)
            ax.text(x, y-3, f'{label}\nABERTO!', ha='center', va='top',
                   color=C_DANGER, fontsize=5, fontweight='bold')

    def draw_linha(ax, x1, y1, x2, y2, cor, lw):
        ax.plot([x1, x2], [y1, y2], color=cor, linewidth=lw, solid_capstyle='round')

    # Cabine Light
    draw_box(ax, 5, 75, 20, 16, 'CABINE LIGHT', '13,8 kV | Relé 7SR1002', C_GRID, sub2='ANSI 50/51/50N/51N')
    draw_dj(ax, 15, 73, est['dj_mt'], 'DJ MT Light', C_GRID)
    draw_linha(ax, 15, 73, 15, 65, C_GRID, 3)

    # PMT
    draw_box(ax, 30, 75, 38, 16, 'PMT-02-G200', 'Circuito Exclusivo MELI', '#ffaa00', sub2='Disjuntor Geral MT + Relé 7SR1004')

    # AGC
    cor_agc = C_CONTROL if not est['falha_agc'] else C_DANGER
    draw_box(ax, 32, 77, 14, 10, 'AGC-150 MAINS', 'DEIF Controller', cor_agc, fontsize=7,
             sub2='✗ FALHA' if est['falha_agc'] else '✓ OK')

    # Siemens
    draw_box(ax, 52, 77, 14, 10, 'Siemens 7SR1004', 'Proteção MT', '#ff6666', fontsize=7,
             sub2='ANSI 32/67/59/81/27/50/51')

    # DJ MT PMT
    draw_dj(ax, 50, 65, est['dj_mt'], 'DJ MT PMT-02', C_OK if est['dj_mt'] else C_DANGER)
    draw_linha(ax, 50, 65, 50, 58, C_GRID if est['dj_mt'] else C_NEUTRO, 3)

    # Medidor
    circle = Circle((44, 60), 2.5, facecolor='#2a1a4e', edgecolor=C_CONTROL, linewidth=2)
    ax.add_patch(circle)
    ax.text(44, 60, 'M', ha='center', va='center', color=C_CONTROL, fontsize=8, fontweight='bold')
    ax.text(44, 56, 'TC/TP', ha='center', va='top', color=C_CONTROL, fontsize=5)

    # Transformadores
    transformadores = [
        (5, 35, 'TR-05-G200', '500 kVA', 4, 'dj_bt_05'),
        (37, 35, 'TR-07-CAG', '2000 kVA', 16, 'dj_bt_07'),
        (69, 35, 'TR-08-G200', '750 kVA', 4, 'dj_bt_08'),
    ]
    for x, y, nome, pot, n_inv, dj_key in transformadores:
        cor_tr = C_CARGA if est['dj_mt'] else C_NEUTRO
        rect = FancyBboxPatch((x, y), 24, 12, boxstyle="round,pad=0.2",
                               facecolor='#1a2a1a', edgecolor=cor_tr, linewidth=2)
        ax.add_patch(rect)
        ax.add_patch(Circle((x+12, y+7), 2.5, facecolor='none', edgecolor=cor_tr, linewidth=2))
        ax.add_patch(Circle((x+12, y+7), 1.2, facecolor='none', edgecolor=cor_tr, linewidth=2))
        ax.text(x+12, y+10, nome, ha='center', va='center', color=cor_tr, fontsize=7, fontweight='bold')
        ax.text(x+12, y+6.5, pot, ha='center', va='center', color='#aaaaaa', fontsize=6)
        ax.text(x+12, y+3, f'{n_inv} inv.', ha='center', va='center', color='#888888', fontsize=5)

        # DJ BT
        dj_ok = est[dj_key]
        dj_cor = C_SOLAR if dj_ok else C_DANGER
        ax.plot([x+12, x+12], [y+12, y+15], color=dj_cor, linewidth=2)
        if dj_ok:
            ax.plot([x+10.5, x+13.5], [y+13.5, y+13.5], color=dj_cor, linewidth=3)
        else:
            ax.plot([x+10.5, x+12], [y+13.5, y+15.5], color=dj_cor, linewidth=2)
            ax.plot([x+12, x+13.5], [y+15.5, y+13.5], color=dj_cor, linewidth=2)

    # Inversores
    gerando = est['geracao_efetiva'] > 0
    cor_inv = C_SOLAR if gerando else C_NEUTRO
    rect = FancyBboxPatch((5, 5), 90, 20, boxstyle="round,pad=0.3",
                           facecolor='#0a1a0a', edgecolor=cor_inv, linewidth=2)
    ax.add_patch(rect)
    ax.text(50, 22, 'INVERSORES SOLAREDGE SE100K', ha='center', va='center',
           color=cor_inv, fontsize=9, fontweight='bold')
    ax.text(50, 18, '24 unidades | 2.400 kWp | Modbus RTU Broadcast', ha='center', va='center',
           color='#88aa88', fontsize=6)

    grupos = [(17, 'Grupo 1\nTR-05', est['dj_bt_05']),
              (50, 'Grupo 2\nTR-07', est['dj_bt_07']),
              (83, 'Grupo 3\nTR-08', est['dj_bt_08'])]
    for x, label, dj_ok in grupos:
        cor_g = C_SOLAR if dj_ok and gerando else C_NEUTRO
        for i in range(4):
            ix = x - 6 + (i % 2) * 4
            iy = 10 if i < 2 else 14
            inv = FancyBboxPatch((ix-1.5, iy-1), 3, 2, boxstyle="round,pad=0.1",
                                  facecolor='#1a3a1a' if dj_ok else '#2a2a2a',
                                  edgecolor=cor_g, linewidth=1)
            ax.add_patch(inv)
        ax.text(x, 7, label, ha='center', va='center', color=cor_g, fontsize=6)

    # Carga MELI
    energizado = est['dj_mt'] and est['consumo_meli'] > 0
    cor_carga = C_CARGA if energizado else C_NEUTRO
    rect = FancyBboxPatch((72, 75), 23, 16, boxstyle="round,pad=0.3",
                           facecolor='#2a1a0a', edgecolor=cor_carga, linewidth=3)
    ax.add_patch(rect)
    ax.text(83.5, 88, 'CARGA MELI', ha='center', va='center', color=cor_carga, fontsize=9, fontweight='bold')
    ax.text(83.5, 84, 'Mercado Livre', ha='center', va='center', color='#aaaaaa', fontsize=7)
    if energizado:
        ax.text(83.5, 79, f'{est["consumo_meli"]:.0f} kW', ha='center', va='center',
               color='#ffcc88', fontsize=10, fontweight='bold')
        ax.text(83.5, 76, '✓ ENERGIZADO', ha='center', va='center', color=C_OK, fontsize=7, fontweight='bold')
    else:
        ax.text(83.5, 79, '0 kW', ha='center', va='center', color='#666666', fontsize=10)
        ax.text(83.5, 76, '✗ DESLIGADO', ha='center', va='center', color=C_DANGER, fontsize=7, fontweight='bold')

    # Fluxos
    fluxo = est['fluxo_rede']
    if est['dj_mt']:
        if fluxo > 0:
            ax.annotate('', xy=(32, 83), xytext=(25, 83),
                       arrowprops=dict(arrowstyle='->', color=C_GRID, lw=3))
            ax.text(28.5, 85, f'{fluxo:.0f} kW', ha='center', va='bottom', color=C_GRID, fontsize=7, fontweight='bold')
        elif fluxo < 0:
            ax.annotate('', xy=(25, 83), xytext=(32, 83),
                       arrowprops=dict(arrowstyle='->', color=C_EXPORT, lw=4))
            ax.text(28.5, 85, f'{abs(fluxo):.0f} kW', ha='center', va='bottom', color=C_EXPORT, fontsize=7, fontweight='bold')

    if est['dj_mt'] and est['consumo_meli'] > 0:
        ax.annotate('', xy=(72, 83), xytext=(68, 83),
                   arrowprops=dict(arrowstyle='->', color=C_CARGA, lw=3))

    if est['geracao_efetiva'] > 0:
        ax.plot([15, 83.5], [5, 5], color=C_SOLAR, linewidth=2, alpha=0.5)
        for x in [15, 50, 83.5]:
            ax.annotate('', xy=(x, 35), xytext=(x, 27),
                       arrowprops=dict(arrowstyle='->', color=C_SOLAR, lw=2))
        ax.text(50, 30, f'{est["geracao_efetiva"]:.0f} kW', ha='center', va='center',
               color=C_SOLAR, fontsize=8, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='#0a1a0a', edgecolor=C_SOLAR))

    # Legenda
    y_leg = 2
    items = [(C_GRID, 'Rede Light'), (C_SOLAR, 'Geração Solar'), (C_CARGA, 'Consumo MELI'), (C_EXPORT, 'Exportação')]
    x_leg = 8
    for cor, texto in items:
        ax.plot([x_leg, x_leg+3], [y_leg, y_leg], color=cor, linewidth=3)
        ax.text(x_leg+4, y_leg, texto, ha='left', va='center', color='white', fontsize=6)
        x_leg += 22

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

# -------------------------------------------------------------------------------
# PAINEL DE CAMADAS
# -------------------------------------------------------------------------------
with col_camadas:
    st.subheader("🛡️ Camadas de Proteção")

    camadas = [
        ("Camada 0", "Controle DEIF (Laço Fechado)", est['camada_0'],
         "#00ff88", "< 3s", "Reduz setpoint inversores"),
        ("Camada 1", "ANSI 32 — AGC-150 MAINS", est['camada_1'],
         "#ffaa00", "3–4s", "Abre disjuntores BT"),
        ("Camada 2", "Relé Auxiliar ANSI 32", est['camada_2'],
         "#ff8800", "5–7s", "Redundância — abre BTs"),
        ("Camada 3", "Siemens 7SR1004 (32/67)", est['camada_3'],
         "#ff4444", "8–10s", "ABRE DISJUNTOR MT"),
        ("Camada C", "Proteções Nativas Inversores", est['camada_c'],
         "#aa44ff", "< 2s", "Anti-ilhamento"),
    ]

    for nome, desc, ativa, cor, tempo, acao in camadas:
        css_class = "camada-ativa" if ativa else "camada-inativa"
        status_text = "▶ ATIVA" if ativa else "○ Inativa"
        st.markdown(
            '<div class="' + css_class + '">'
            '<div style="display:flex; justify-content:space-between; align-items:center;">'
            '<div><span style="color:' + cor + '; font-weight:bold; font-size:1.05em;">' + nome + '</span>'
            '<span style="color:#888888; font-size:0.85em;"> | ' + desc + '</span></div>'
            '<div style="text-align:right;">'
            '<div style="color:' + (cor if ativa else '#666688') + '; font-weight:bold;">' + status_text + '</div>'
            '<div style="color:#888888; font-size:0.75em;">' + tempo + '</div>'
            '</div></div>'
            '<div style="color:#aaaaaa; font-size:0.85em; margin-top:4px; font-style:italic;">' + acao + '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # Disjuntores
    st.subheader("🔌 Estados dos Disjuntores")
    cols_dj = st.columns(4)
    dj_states = [
        ("DJ MT PMT", est['dj_mt'], "MT"),
        ("DJ BT TR-05", est['dj_bt_05'], "BT"),
        ("DJ BT TR-07", est['dj_bt_07'], "BT"),
        ("DJ BT TR-08", est['dj_bt_08'], "BT"),
    ]
    for col, (nome, fechado, tipo) in zip(cols_dj, dj_states):
        with col:
            css = "disjuntor-fechado" if fechado else "disjuntor-aberto"
            icon = "🟢" if fechado else "🔴"
            st.markdown(
                '<div class="metric-card"><span class="' + css + '">' + icon + ' ' + nome + '</span><br><small>' + tipo + '</small></div>',
                unsafe_allow_html=True
            )

# ================================================================================
# GRÁFICO DE BARRAS — POTÊNCIAS
# ================================================================================
st.divider()
st.subheader("📊 Distribuição de Potências")

col_chart, col_json = st.columns([3, 1])

with col_chart:
    fig2, ax2 = plt.subplots(figsize=(10, 4), facecolor='#0a0e27')
    ax2.set_facecolor('#111936')

    dados = [
        ('Geração Solar', est['geracao_efetiva'], 2400, C_SOLAR),
        ('Consumo MELI', est['consumo_meli'], 3000, C_CARGA),
        ('Importação Rede', max(0, est['fluxo_rede']), 3000, C_GRID),
        ('Exportação (Risco)', max(0, -est['fluxo_rede']), 500, C_EXPORT),
    ]

    for i, (nome, valor, maximo, cor) in enumerate(dados):
        y = 3 - i
        ax2.barh(y, maximo, height=0.5, color='#222233', alpha=0.5, left=0)
        if valor > 0:
            ax2.barh(y, valor, height=0.5, color=cor, alpha=0.85, left=0)
        ax2.text(-100, y, nome, ha='right', va='center', color='white', fontsize=9, fontweight='bold')
        ax2.text(valor + 50, y, f'{valor:.0f} kW', ha='left', va='center', color=cor, fontsize=9, fontweight='bold')
        pct = min(valor / maximo * 100, 100) if maximo > 0 else 0
        ax2.text(maximo + 100, y, f'{pct:.0f}%', ha='left', va='center', color='#666688', fontsize=8)

    ax2.set_xlim(-200, 3600)
    ax2.set_ylim(-0.8, 3.8)
    ax2.set_yticks([])
    ax2.tick_params(colors='white')
    for spine in ax2.spines.values():
        spine.set_color('#444466')

    plt.tight_layout()
    st.pyplot(fig2, use_container_width=True)

with col_json:
    st.subheader("📋 Estado JSON")
    with st.expander("Ver estado completo"):
        st.json(sim.get_estado())

    st.download_button(
        label="⬇️ Download JSON",
        data=sim.get_estado_json(),
        file_name="gridzero_estado.json",
        mime="application/json",
        use_container_width=True
    )

# ================================================================================
# LOG / HISTÓRICO
# ================================================================================
st.divider()
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Adicionar ponto atual ao histórico (evitar duplicatas seguidas)
if not st.session_state.historico or st.session_state.historico[-1] != est:
    st.session_state.historico.append(est.copy())
    # Manter apenas últimos 50 pontos
    st.session_state.historico = st.session_state.historico[-50:]

if len(st.session_state.historico) > 1:
    st.subheader("📈 Evolução Temporal (últimos 50 ciclos)")
    hist = st.session_state.historico
    fig3, ax3 = plt.subplots(figsize=(12, 4), facecolor='#0a0e27')
    ax3.set_facecolor('#111936')

    x = range(len(hist))
    ax3.plot(x, [h['geracao_efetiva'] for h in hist], color=C_SOLAR, linewidth=2, label='Geração Efetiva')
    ax3.plot(x, [h['consumo_meli'] for h in hist], color=C_CARGA, linewidth=2, label='Consumo')
    ax3.plot(x, [h['fluxo_rede'] for h in hist], color=C_GRID, linewidth=2, label='Fluxo Rede', linestyle='--')

    ax3.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
    ax3.axhline(y=-50, color='#ffaa00', linewidth=1, linestyle=':', alpha=0.7, label='Limite Alarme')
    ax3.axhline(y=-100, color='#ff4444', linewidth=1, linestyle=':', alpha=0.7, label='Limite Crítico')

    ax3.set_xlabel('Ciclo', color='white')
    ax3.set_ylabel('kW', color='white')
    ax3.tick_params(colors='white')
    ax3.legend(facecolor='#1a1f3a', edgecolor='#444466', labelcolor='white', loc='upper left')
    for spine in ax3.spines.values():
        spine.set_color('#444466')

    plt.tight_layout()
    st.pyplot(fig3, use_container_width=True)

# ================================================================================
# RODAPÉ
# ================================================================================
st.divider()
st.caption("GridZero Simulator v1.0 | Baseado no Memorial Técnico SolarVolt | 2026-05-25")
