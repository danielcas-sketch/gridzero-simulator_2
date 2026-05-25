import streamlit as st

st.set_page_config(page_title="Simulador DEIF - GridZero", layout="wide")
st.title("⚡ Simulador de Controle de Energia - Sistema DEIF")

# Estado da sessão (igual ao anterior)
if "geracao" not in st.session_state:
    st.session_state.geracao = 0
    st.session_state.consumo = 0
    st.session_state.exportacao = 0
    st.session_state.fluxo_rede = 0
    st.session_state.disjuntor_media = True
    st.session_state.gridzero_ativo = False
    st.session_state.funcao32_ativa = False
    st.session_state.protecao_siemens_ativa = False
    st.session_state.limite_exportacao = 100
    st.session_state.limite_importacao = 500

def calcular_sistema():
    balanco = st.session_state.geracao - st.session_state.consumo
    if balanco > 0:
        st.session_state.exportacao = min(balanco, st.session_state.limite_exportacao)
        st.session_state.fluxo_rede = -st.session_state.exportacao
        st.session_state.gridzero_ativo = st.session_state.exportacao > 0
        st.session_state.funcao32_ativa = st.session_state.exportacao >= st.session_state.limite_exportacao
    else:
        st.session_state.exportacao = 0
        st.session_state.fluxo_rede = abs(balanco)
        st.session_state.gridzero_ativo = False
        st.session_state.funcao32_ativa = False

    if st.session_state.fluxo_rede > st.session_state.limite_importacao:
        st.session_state.protecao_siemens_ativa = True
        st.session_state.disjuntor_media = False
    elif st.session_state.fluxo_rede < st.session_state.limite_importacao and not st.session_state.protecao_siemens_ativa:
        st.session_state.disjuntor_media = True

# Interface de controle
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎮 Controles")
    nova_geracao = st.slider("🌞 Geração Solar (kW)", 0, 500, st.session_state.geracao)
    novo_consumo = st.slider("🏭 Consumo Local (kW)", 0, 500, st.session_state.consumo)
    if nova_geracao != st.session_state.geracao or novo_consumo != st.session_state.consumo:
        st.session_state.geracao = nova_geracao
        st.session_state.consumo = novo_consumo
        calcular_sistema()

    st.markdown("---")
    st.subheader("📋 Cenários")
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("🌅 Exportação (400/100)"):
        st.session_state.geracao = 400
        st.session_state.consumo = 100
        calcular_sistema()
    if col_b.button("🔥 Consumo Alto (200/450)"):
        st.session_state.geracao = 200
        st.session_state.consumo = 450
        calcular_sistema()
    if col_c.button("⚠️ Sobrecarga (100/600)"):
        st.session_state.geracao = 100
        st.session_state.consumo = 600
        calcular_sistema()
    if st.button("🔄 Reset"):
        for key in ["geracao", "consumo", "exportacao", "fluxo_rede"]:
            st.session_state[key] = 0
        st.session_state.disjuntor_media = True
        st.session_state.gridzero_ativo = False
        st.session_state.funcao32_ativa = False
        st.session_state.protecao_siemens_ativa = False
        calcular_sistema()

    st.markdown("---")
    st.subheader("📊 Status")
    st.metric("GridZero", "🟢 ATIVO" if st.session_state.gridzero_ativo else "🔴 INATIVO")
    st.metric("Função 32", "🟢 ATIVA" if st.session_state.funcao32_ativa else "🔴 INATIVA")
    st.metric("Disjuntor MT", "🔒 FECHADO" if st.session_state.disjuntor_media else "⚠️ ABERTO")
    st.metric("Exportação", f"{st.session_state.exportacao} kW")
    direcao = "importando" if st.session_state.fluxo_rede > 0 else "exportando"
    st.metric("Fluxo Rede", f"{abs(st.session_state.fluxo_rede)} kW ({direcao})")

# ---------- DIAGRAMA USANDO COMPONENTES STREAMLIT (SEM SVG) ----------
with col2:
    st.subheader("🔌 Diagrama do Sistema (layout em blocos)")

    # Linha 1: Rede → PMT → Disjuntor → DEIF
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.markdown("**REDE**\n🔌", unsafe_allow_html=True)
        st.caption("Concessionária")
    with col_b:
        st.markdown("**PMT**\n⚡", unsafe_allow_html=True)
        st.caption("13.8 kV")
    with col_c:
        cor_dj = "🟢" if st.session_state.disjuntor_media else "🔴"
        st.markdown(f"**DJ MT**\n{cor_dj}", unsafe_allow_html=True)
        st.caption("Fechado" if st.session_state.disjuntor_media else "Aberto")
    with col_d:
        st.markdown("**DEIF MAINS**\n🎛️", unsafe_allow_html=True)
        st.caption("Controller")

    st.markdown("→ → → → → → → → → → → → → → → → → →")

    # Linha 2: Quadro Geral
    st.markdown("### 📦 QUADRO GERAL")
    st.caption("Distribui energia para carga e inversores")

    # Linha 3: Inversores + Geração Solar
    col_e, col_f, col_g, col_h = st.columns(4)
    with col_e:
        st.markdown("**INVERSOR 1**\n☀️", unsafe_allow_html=True)
        st.caption("ASC-150")
    with col_f:
        st.markdown("**INVERSOR 2**\n☀️", unsafe_allow_html=True)
        st.caption("ASC-150")
    with col_g:
        st.markdown("**INVERSOR 3**\n☀️", unsafe_allow_html=True)
        st.caption("ASC-150")
    with col_h:
        st.markdown(f"**GERAÇÃO SOLAR**\n🔆 {st.session_state.geracao} kW", unsafe_allow_html=True)

    st.markdown("↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓")

    # Linha 4: Carga local
    st.markdown(f"### 🏭 CARGA LOCAL")
    st.metric("Consumo atual", f"{st.session_state.consumo} kW")

    # Linha 5: Proteção Siemens (se ativa)
    if st.session_state.protecao_siemens_ativa:
        st.error("⚠️ PROTEÇÃO SIEMENS ATIVA - Disjuntor MT aberto por sobrecarga!")

    # Linha 6: Fluxo de potência
    st.markdown("---")
    st.subheader("⚡ Fluxo de Potência")
    if st.session_state.geracao > st.session_state.consumo:
        st.success(f"📤 EXPORTANDO {st.session_state.exportacao} kW para a rede")
    elif st.session_state.consumo > st.session_state.geracao:
        st.warning(f"📥 IMPORTANDO {st.session_state.fluxo_rede} kW da rede")
    else:
        st.info("⚖️ Geração igual ao consumo - sem fluxo líquido")

# Rodapé
st.markdown("---")
st.caption("Simulador GridZero com controle DEIF, função 32 e proteção Siemens.")
