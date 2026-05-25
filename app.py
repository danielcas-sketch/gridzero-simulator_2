import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Configuração da página
st.set_page_config(page_title="Simulador DEIF - GridZero", layout="wide")
st.title("⚡ Simulador de Controle de Energia - Sistema DEIF")

# Inicializar estado da sessão
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

# Funções de cálculo
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

    # Proteção por sobrecarga
    if st.session_state.fluxo_rede > st.session_state.limite_importacao:
        st.session_state.protecao_siemens_ativa = True
        st.session_state.disjuntor_media = False
    elif st.session_state.fluxo_rede < st.session_state.limite_importacao and not st.session_state.protecao_siemens_ativa:
        st.session_state.disjuntor_media = True

# Função para desenhar diagrama com matplotlib
def desenhar_diagrama():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')

    # Posições (x, y)
    pos_rede = (1.5, 3)
    pos_pmt = (3.5, 3)
    pos_deif = (5.5, 3)
    pos_quadro = (7.5, 3)
    pos_inversores = [(7.5, 4.5), (7.5, 3), (7.5, 1.5)]
    pos_carga = (9.0, 3)
    pos_solar = (9.5, 5)

    # Desenhar componentes
    def desenha_retangulo(x, y, larg, alt, cor, texto, cor_texto='white'):
        rect = patches.Rectangle((x-larg/2, y-alt/2), larg, alt, facecolor=cor, edgecolor='white', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, texto, ha='center', va='center', color=cor_texto, fontsize=10, fontweight='bold')

    desenha_retangulo(*pos_rede, 1.2, 0.8, '#533483', 'REDE')
    desenha_retangulo(*pos_pmt, 1.0, 0.6, '#0f3460', 'PMT')
    desenha_retangulo(*pos_deif, 1.4, 0.8, '#e94560', 'DEIF MAINS\nCONTROLLER')
    desenha_retangulo(*pos_quadro, 1.0, 0.6, '#16213e', 'QUADRO')
    for i, (x, y) in enumerate(pos_inversores):
        desenha_retangulo(x, y, 1.0, 0.6, '#16213e', f'INV {i+1}')
    desenha_retangulo(*pos_carga, 1.0, 0.6, '#0f3460', f'CARGA\n{st.session_state.consumo} kW')
    desenha_retangulo(*pos_solar, 1.2, 0.8, '#e94560', f'SOLAR\n{st.session_state.geracao} kW')

    # Linhas de conexão
    def linha(x1, y1, x2, y2, cor, estilo='-'):
        ax.plot([x1, x2], [y1, y2], color=cor, linestyle=estilo, linewidth=2)

    linha(pos_rede[0], pos_rede[1], pos_pmt[0], pos_pmt[1], 'white')
    linha(pos_pmt[0], pos_pmt[1], pos_deif[0], pos_deif[1], 'white')
    linha(pos_deif[0], pos_deif[1], pos_quadro[0], pos_quadro[1], 'white')
    for (x, y) in pos_inversores:
        linha(pos_quadro[0], pos_quadro[1], x, y, '#e94560')
    linha(pos_quadro[0], pos_quadro[1], pos_carga[0], pos_carga[1], 'white')
    linha(pos_solar[0], pos_solar[1], pos_inversores[0][0], pos_inversores[0][1], '#e94560')

    # Disjuntor de média tensão
    dj_x, dj_y = 2.5, 4.2
    cor_dj = 'green' if st.session_state.disjuntor_media else 'red'
    ax.add_patch(patches.Rectangle((dj_x-0.3, dj_y-0.2), 0.6, 0.4, facecolor=cor_dj, edgecolor='white'))
    ax.text(dj_x, dj_y, 'DJ MT', ha='center', va='center', color='white', fontsize=8)

    # Indicador de proteção Siemens
    if st.session_state.protecao_siemens_ativa:
        ax.text(pos_deif[0], pos_deif[1]+1.2, '⚠️ PROTEÇÃO SIEMENS ATIVA', ha='center', color='red', fontweight='bold')

    # Setas de fluxo
    if st.session_state.geracao > st.session_state.consumo and st.session_state.disjuntor_media:
        ax.annotate('', xy=(pos_rede[0]-0.2, pos_rede[1]), xytext=(pos_pmt[0]+0.2, pos_pmt[1]),
                    arrowprops=dict(arrowstyle='->', color='lime', lw=2))
        ax.text(pos_rede[0]-0.8, pos_rede[1]+0.3, f'Exportando: {abs(st.session_state.exportacao)} kW', color='lime')
    elif st.session_state.consumo > st.session_state.geracao and st.session_state.disjuntor_media:
        ax.annotate('', xy=(pos_pmt[0]-0.2, pos_pmt[1]), xytext=(pos_rede[0]+0.2, pos_rede[1]),
                    arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
        ax.text(pos_rede[0]-0.8, pos_rede[1]-0.3, f'Importando: {st.session_state.fluxo_rede} kW', color='yellow')

    return fig

# Interface Streamlit
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎮 Controles")
    geracao = st.slider("🌞 Geração Solar (kW)", 0, 500, st.session_state.geracao)
    consumo = st.slider("🏭 Consumo Local (kW)", 0, 500, st.session_state.consumo)
    
    if geracao != st.session_state.geracao or consumo != st.session_state.consumo:
        st.session_state.geracao = geracao
        st.session_state.consumo = consumo
        calcular_sistema()
    
    st.markdown("---")
    st.subheader("📋 Cenários Rápidos")
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
    if st.button("🔄 Reset Sistema"):
        st.session_state.geracao = 0
        st.session_state.consumo = 0
        st.session_state.exportacao = 0
        st.session_state.fluxo_rede = 0
        st.session_state.disjuntor_media = True
        st.session_state.gridzero_ativo = False
        st.session_state.funcao32_ativa = False
        st.session_state.protecao_siemens_ativa = False
        calcular_sistema()
    
    st.markdown("---")
    st.subheader("📊 Status do Sistema")
    st.metric("GridZero", "🟢 ATIVO" if st.session_state.gridzero_ativo else "🔴 INATIVO")
    st.metric("Função 32", "🟢 ATIVA" if st.session_state.funcao32_ativa else "🔴 INATIVA")
    st.metric("Disjuntor MT", "🔒 FECHADO" if st.session_state.disjuntor_media else "⚠️ ABERTO")
    st.metric("Exportação Líquida", f"{st.session_state.exportacao} kW")
    st.metric("Fluxo da Rede", f"{abs(st.session_state.fluxo_rede)} kW ({'importando' if st.session_state.fluxo_rede > 0 else 'exportando'})")

with col2:
    st.subheader("🔌 Diagrama do Sistema")
    fig = desenhar_diagrama()
    st.pyplot(fig)

st.markdown("---")
st.caption("Simulador de estratégia GridZero com proteção Siemens e lógica DEIF Mains Controller.")
