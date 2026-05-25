import streamlit as st
import time

# Configuração da página
st.set_page_config(page_title="Simulador GridZero - Prologis", layout="wide")

st.title("⚡ Simulador Dinâmico GridZero - Complexo Prologis Dutra II")
st.markdown("Visualização em tempo real do fluxo de potência e atuação das camadas de proteção.")

# Inicialização das variáveis de estado na memória do Streamlit
if "dj_mt_fechado" not in st.session_state:
    st.session_state.dj_mt_fechado = True  
    st.session_state.dj_bt_fechados = True 
    st.session_state.tempo_exportacao = 0

# --- PAINEL DE CONTROLE (MENU LATERAL) ---
st.sidebar.header("🎛️ Parâmetros de Entrada")
geracao_potencial = st.sidebar.slider("Capacidade de Geração Solar (kW)", 0, 2400, 1200, step=100)
consumo_carga = st.sidebar.slider("Demanda de Carga Mercado Livre (kW)", 0, 3000, 1500, step=100)

st.sidebar.divider()
falha_deif = st.sidebar.toggle("⚠️ Simular Falha no Controle DEIF", value=False, 
                               help="Desativa a Camada 0 (estrangulamento), forçando os inversores a injetarem a potência máxima disponível.")

if st.sidebar.button("🔄 Resetar Sistema / Religamento Geral"):
    st.session_state.dj_mt_fechado = True
    st.session_state.dj_bt_fechados = True
    st.session_state.tempo_exportacao = 0
    st.rerun()

# --- LÓGICA DE OPERAÇÃO (SISTEMA DE CONTROLE) ---
geracao_real = 0
exportacao = 0

# Processamento do estado dos disjuntores
if st.session_state.dj_mt_fechado and st.session_state.dj_bt_fechados:
    if falha_deif:
        # Cenário de Falha de Comunicação ou Controle: usina opera em potência máxima disponível
        geracao_real = geracao_potencial
    else:
        # Operação Normal (Camada 0): Controle dinâmico limita a geração ao consumo instantâneo
        geracao_real = min(geracao_potencial, consumo_carga)

# Cálculo do balanço de energia no ponto de medição (PMT-02-G200)
fluxo_rede = consumo_carga - geracao_real if st.session_state.dj_mt_fechado else 0

if fluxo_rede < 0:
    exportacao = abs(fluxo_rede)
    fluxo_rede_abs = abs(fluxo_rede)
else:
    fluxo_rede_abs = fluxo_rede

# --- CRONÔMETRO DAS CAMADAS DE PROTEÇÃO ---
placeholder_alertas = st.empty()

if exportacao > 0:
    st.session_state.tempo_exportacao += 1
    
    with placeholder_alertas.container():
        st.error(f"🚨 **CONDIÇÃO CRÍTICA: EXPORTAÇÃO DETECTADA!** Injeção de {exportacao} kW em direção à rede externa.")
        st.warning(f"⏱️ Tempo acumulado de inversão de fluxo: **{st.session_state.tempo_exportacao} segundos**")
        
    # Tratamento das camadas temporizadas de proteção
    if 3 <= st.session_state.tempo_exportacao < 8:
        st.session_state.dj_bt_fechados = False
        st.error("💥 **CAMADA 1 ATUOU (ANSI 32 - AGC-150):** Comando enviado para abertura dos disjuntores de Baixa Tensão. Usina desconectada.")
    elif st.session_state.tempo_exportacao >= 8:
        st.session_state.dj_mt_fechado = False
        st.error("💥💥 **CAMADA 3 ATUOU (ANSI 32/67 - Siemens 7SR1004):** Abertura do disjuntor de Média Tensão geral na cabine. Interrupção total do fornecimento.")
        
    time.sleep(1)
    st.rerun()
else:
    st.session_state.tempo_exportacao = 0

# --- CARD METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    status_mt = "🟢 FECHADO" if st.session_state.dj_mt_fechado else "🔴 ABERTO (TRIP)"
    st.metric(label=f"Rede Concessionária (Disjuntor MT: {status_mt})", 
              value=f"{fluxo_rede_abs:.0f} kW", 
              delta="Importando Energia" if fluxo_rede >= 0 else "Exportando Energia",
              delta_color="normal" if fluxo_rede >= 0 else "inverse")

with col2:
    status_meli = "🟢 ENERGIZADO" if st.session_state.dj_mt_fechado else "⚫ APAGÃO (LIVRE)"
    st.metric(label=f"Demanda Total Galpão G200 ({status_meli})", value=f"{consumo_carga if st.session_state.dj_mt_fechado else 0:.0f} kW")

with col3:
    status_bt = "🟢 FECHADO" if st.session_state.dj_bt_fechados else "🔴 ABERTO (TRIP)"
    st.metric(label=f"Geração Fotovoltaica Real (Disjuntores BT: {status_bt})", value=f"{geracao_real:.0f} kW")

# --- DIAGRAMA DE FLUXO DE ENERGIA DINÂMICO (HTML/CSS) ---
st.write("### Diagrama de Fluxo de Potência Ativa")

# Definição de cores e direções de setas baseadas no estado atual do simulador
seta_rede_pmt = "➡️" if fluxo_rede >= 0 else "⬅️"
cor_seta_rede = "#2ecc71" if fluxo_rede >= 0 else "#e74c3c"
if not st.session_state.dj_mt_fechado:
    seta_rede_pmt = "❌"
    cor_seta_rede = "#95a5a6"

seta_solar_pmt = "⬆️" if geracao_real > 0 else "🛑"
cor_seta_solar = "#f1c40f" if geracao_real > 0 else "#95a5a6"

seta_pmt_carga = "➡️" if (st.session_state.dj_mt_fechado and consumo_carga > 0) else "🛑"
cor_seta_carga = "#e67e22" if (st.session_state.dj_mt_fechado and consumo_carga > 0) else "#95a5a6"

# Construção do layout visual do circuito unifilar simplificado
html_diagrama = f"""
<div style="display: flex; flex-direction: column; align-items: center; background-color: #f8f9fa; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; font-family: sans-serif;">
    
    <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; max-width: 900px; margin-bottom: 20px;">
        
        <div style="border: 2px solid #34495e; padding: 15px; background-color: #ffffff; border-radius: 8px; width: 180px; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
            <div style="font-weight: bold; color: #34495e; font-size: 14px;">CABINE PRIMÁRIA</div>
            <div style="font-size: 11px; color: #7f8c8d; margin-top: 4px;">Ponto de Entrega Light</div>
            <div style="font-size: 12px; font-weight: bold; margin-top: 8px; color: #2c3e50;">13,8 kV / 60 Hz</div>
        </div>
        
        <div style="font-size: 28px; color: {cor_seta_rede}; font-weight: bold; display: flex; flex-direction: column; align-items: center; width: 100px;">
            <span style="font-size: 12px; color: #7f8c8d; margin-bottom: 2px;">{fluxo_rede_abs:.0f} kW</span>
            {seta_rede_pmt}
        </div>
        
        <div style="border: 3px solid {'#2ecc71' if st.session_state.dj_mt_fechado else '#e74c3c'}; padding: 15px; background-color: #ebf5fb; border-radius: 8px; width: 220px; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
            <div style="font-weight: bold; color: #2980b9; font-size: 14px;">SALA DE PMT</div>
            <div style="font-size: 12px; font-weight: bold; background-color: #ffffff; padding: 4px; border-radius: 4px; margin-top: 5px; border: 1px solid #d6dbdf;">
                DEIF AGC-150 MAINS
            </div>
            <div style="font-size: 11px; color: #2c3e50; margin-top: 6px; font-weight: bold;">
                Disjuntor MT: <span style="color: {'#2ecc71' if st.session_state.dj_mt_fechado else '#e74c3c'};">{'CONECTADO' if st.session_state.dj_mt_fechado else 'DESLIGADO'}</span>
            </div>
        </div>
        
        <div style="font-size: 28px; color: {cor_seta_carga}; font-weight: bold; display: flex; flex-direction: column; align-items: center; width: 100px;">
            <span style="font-size: 12px; color: #7f8c8d; margin-bottom: 2px;">{consumo_carga if st.session_state.dj_mt_fechado else 0:.0f} kW</span>
            {seta_pmt_carga}
        </div>
        
        <div style="border: 2px solid #e67e22; padding: 15px; background-color: #ffffff; border-radius: 8px; width: 180px; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
            <div style="font-weight: bold; color: #d35400; font-size: 14px;">MERCADO LIVRE</div>
            <div style="font-size: 11px; color: #7f8c8d; margin-top: 4px;">Consumo Ativo Galpão</div>
            <div style="font-size: 16px; font-weight: bold; margin-top: 8px; color: #e67e22;">{consumo_carga:.0f} kW</div>
        </div>
    </div>
    
    <div style="display: flex; justify-content: center; width: 100%; max-width: 900px; margin-left: -35px;">
        <div style="display: flex; flex-direction: column; align-items: center;">
            <span style="font-size: 12px; color: #7f8c8d; margin-bottom: 2px;">{geracao_real:.0f} kW</span>
            <div style="font-size: 28px; color: {cor_seta_solar}; font-weight: bold; margin-top: -5px; margin-bottom: -5px;">{seta_solar_pmt}</div>
        </div>
    </div>
    
    <div style="display: flex; justify-content: center; width: 100%; max-width: 900px; margin-top: 10px; margin-left: -35px;">
        <div style="border: 3px solid {'#2ecc71' if st.session_state.dj_bt_fechados else '#e74c3c'}; padding: 15px; background-color: #fef9e7; border-radius: 8px; width: 340px; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
            <div style="font-weight: bold; color: #f39c12; font-size: 14px;">⚡ USINA SOLAR FOTOVOLTAICA</div>
            <div style="font-size: 11px; color: #7f8c8d; margin-top: 2px;">24x Inversores SolarEdge SE100K</div>
            <div style="display: flex; justify-content: space-around; margin-top: 8px; font-size: 11px; background-color: #ffffff; padding: 5px; border-radius: 4px; border: 1px solid #f9e79f;">
                <div><b>TR-05:</b> 4 Inv</div>
                <div><b>TR-07:</b> 16 Inv</div>
                <div><b>TR-08:</b> 4 Inv</div>
            </div>
            <div style="font-size: 11px; color: #2c3e50; margin-top: 8px; font-weight: bold;">
                Quadros BT: <span style="color: {'#2ecc71' if st.session_state.dj_bt_fechados else '#e74c3c'};">{'INTEGROS (CONECTADOS)' if st.session_state.dj_bt_fechados else 'ABERTOS (DESCONECTADOS)'}</span>
            </div>
        </div>
    </div>
</div>
"""

st.markdown(html_diagrama, unsafe_allow_html=True)

# --- INSTRUÇÕES E DOCUMENTAÇÃO ---
st.markdown("---")
st.markdown("""
### Parâmetros de Ajuste da Arquitetura do Sistema:
* **Camada 0 (Controle Ativo):** O controlador de topo `DEIF AGC-150 MAINS` monitora o fluxo continuamente e atua na malha fechada via Modbus broadcast para que a geração solar nunca supere a demanda local[cite: 48, 181].
* **Camada 1 (ANSI 32 - Rápida):** Atua entre **3 e 4 segundos** de exportação sustentada, disparando a abertura física dos disjuntores de Baixa Tensão (BT)[cite: 225, 230].
* **Camada 3 (ANSI 32/67 - Retaguarda Final):** Caso as etapas locais falhem, o relé `Siemens 7SR1004` abre o disjuntor de Média Tensão geral entre **8 e 10 segundos**, isolando o complexo da rede para cumprir a exigência da concessionária Light[cite: 204, 244, 247].
""")
