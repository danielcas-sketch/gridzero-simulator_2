import streamlit as st
import time

# Configuração da página
st.set_page_config(page_title="Simulador GridZero - Prologis", layout="wide")

st.title("⚡ Simulador GridZero - Prologis Dutra II")
st.markdown("Controle de exportação e proteção em camadas para o cliente Mercado Livre.")

# Inicialização das variáveis de estado (Memória do Streamlit)
if "dj_mt_fechado" not in st.session_state:
    st.session_state.dj_mt_fechado = True  # Disjuntor Geral (Sala PMT)
    st.session_state.dj_bt_fechados = True # Disjuntores Inversores
    st.session_state.tempo_exportacao = 0

# --- PAINEL DE CONTROLE ---
st.sidebar.header("🎛️ Painel de Controle")
geracao_potencial = st.sidebar.slider("Potencial Solar (kW)", 0, 2400, 1500, step=100)
consumo_carga = st.sidebar.slider("Consumo Mercado Livre (kW)", 0, 3000, 500, step=100)

st.sidebar.divider()
falha_deif = st.sidebar.toggle("⚠️ Simular Falha no Controle DEIF", value=False, help="Desliga a Camada 0 e permite que a usina gere o máximo possível.")

if st.sidebar.button("🔄 Resetar Sistema / Religamento"):
    st.session_state.dj_mt_fechado = True
    st.session_state.dj_bt_fechados = True
    st.session_state.tempo_exportacao = 0
    st.rerun()

# --- LÓGICA DO SISTEMA ---
geracao_real = 0
exportacao = 0

# Se os disjuntores estão fechados, a usina pode gerar
if st.session_state.dj_mt_fechado and st.session_state.dj_bt_fechados:
    if falha_deif:
        # Falha: Inversores injetam tudo que podem
        geracao_real = geracao_potencial
    else:
        # Operação Normal (Camada 0): Geração acompanha a carga
        geracao_real = min(geracao_potencial, consumo_carga)

# Cálculo do fluxo no PMT
fluxo_pmt = consumo_carga - geracao_real

if fluxo_pmt < 0:
    exportacao = abs(fluxo_pmt)

# --- MÁQUINA DE ESTADOS E TEMPORIZADOR DE PROTEÇÃO ---
placeholder_alertas = st.empty()

if exportacao > 0:
    st.session_state.tempo_exportacao += 1
    
    with placeholder_alertas.container():
        st.error(f"🚨 **ALERTA DE EXPORTAÇÃO DETECTADA:** {exportacao} kW sendo injetados na rede Light!")
        st.warning(f"⏱️ Tempo de exportação sustentada: **{st.session_state.tempo_exportacao} segundos**")
        
    # Lógica de Seletividade (conforme Memorial)
    if st.session_state.tempo_exportacao >= 3 and st.session_state.tempo_exportacao < 8:
        st.session_state.dj_bt_fechados = False
        st.error("💥 **TRIP CAMADA 1:** Função 32 do AGC-150 atuou. Disjuntores de Baixa Tensão (BT) da usina abertos!")
    elif st.session_state.tempo_exportacao >= 9:
        st.session_state.dj_mt_fechado = False
        st.error("💥💥 **TRIP CAMADA 3:** Relé Siemens atuou no PMT. Disjuntor de Média Tensão (MT) aberto. Cliente desligado!")
        
    time.sleep(1) # Aguarda 1 segundo
    st.rerun()    # Roda a tela novamente para atualizar o cronômetro

else:
    st.session_state.tempo_exportacao = 0

# --- DIAGRAMA VISUAL ---
st.markdown("### Diagrama Unifilar Dinâmico")

col1, col2, col3 = st.columns(3)

# Bloco 1: Concessionária / PMT
with col1:
    cor_mt = "🟢 FECHADO" if st.session_state.dj_mt_fechado else "🔴 ABERTO (TRIP)"
    st.info("**Rede Light (13.8kV)**")
    st.metric(label=f"Disjuntor MT PMT-02-G200 ({cor_mt})", value=f"{fluxo_pmt} kW", delta="Importando" if fluxo_pmt >= 0 else "Exportando", delta_color="normal" if fluxo_pmt >= 0 else "inverse")

# Bloco 2: Carga
with col2:
    status_carga = "🟢 ENERGIZADO" if st.session_state.dj_mt_fechado else "⚫ DESLIGADO"
    st.warning(f"**Mercado Livre - G200**\nStatus: {status_carga}")
    consumo_ativo = consumo_carga if st.session_state.dj_mt_fechado else 0
    st.metric(label="Consumo Atual", value=f"{consumo_ativo} kW")

# Bloco 3: Usina
with col3:
    cor_bt = "🟢 FECHADO" if st.session_state.dj_bt_fechados else "🔴 ABERTO (TRIP)"
    st.success("**Usina Solar (Inversores SE)**")
    st.metric(label=f"Disjuntores BT ({cor_bt})", value=f"{geracao_real} kW")

st.markdown("---")
st.markdown("**Como usar:** O sistema estrangula a geração nativamente. Ligue o botão vermelho no menu lateral esquerdo para simular uma falha de controle. Observe o temporizador disparar as proteções em cascata.")
