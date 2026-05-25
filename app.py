import streamlit as st

st.set_page_config(page_title="Simulador DEIF - GridZero", layout="wide")
st.title("⚡ Simulador de Controle de Energia - Sistema DEIF")

# Estado da sessão (mesmo código anterior)
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
    geracao = st.slider("🌞 Geração Solar (kW)", 0, 500, st.session_state.geracao)
    consumo = st.slider("🏭 Consumo Local (kW)", 0, 500, st.session_state.consumo)
    if geracao != st.session_state.geracao or consumo != st.session_state.consumo:
        st.session_state.geracao = geracao
        st.session_state.consumo = consumo
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
    fluxo_dir = "importando" if st.session_state.fluxo_rede > 0 else "exportando"
    st.metric("Fluxo Rede", f"{abs(st.session_state.fluxo_rede)} kW ({fluxo_dir})")

with col2:
    st.subheader("🔌 Diagrama do Sistema (SVG)")

    # Gerar SVG dinâmico com base no estado atual
    cor_dj = "green" if st.session_state.disjuntor_media else "red"
    gridzero_texto = "GridZero ATIVO" if st.session_state.gridzero_ativo else "GridZero inativo"
    cor_gridzero = "green" if st.session_state.gridzero_ativo else "red"

    fluxo_texto = ""
    if st.session_state.geracao > st.session_state.consumo and st.session_state.disjuntor_media:
        fluxo_texto = f'<text x="180" y="100" fill="lime" font-size="12">→ Exportando {st.session_state.exportacao} kW</text>'
    elif st.session_state.consumo > st.session_state.geracao and st.session_state.disjuntor_media:
        fluxo_texto = f'<text x="180" y="80" fill="yellow" font-size="12">← Importando {st.session_state.fluxo_rede} kW</text>'

    svg_diagram = f'''
    <svg width="100%" height="500" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" style="background-color:#1a1a2e; border-radius:10px;">
        <!-- Rede -->
        <rect x="50" y="160" width="100" height="60" fill="#533483" stroke="white" stroke-width="2"/>
        <text x="100" y="195" fill="white" text-anchor="middle" font-weight="bold">REDE</text>

        <!-- PMT -->
        <rect x="200" y="160" width="80" height="60" fill="#0f3460" stroke="white" stroke-width="2"/>
        <text x="240" y="195" fill="white" text-anchor="middle">PMT</text>

        <!-- Disjuntor MT -->
        <rect x="310" y="170" width="40" height="40" fill="{cor_dj}" stroke="white" stroke-width="2"/>
        <text x="330" y="195" fill="white" text-anchor="middle" font-size="10">DJ MT</text>

        <!-- DEIF Mains Controller -->
        <rect x="390" y="150" width="120" height="80" fill="#e94560" stroke="white" stroke-width="2"/>
        <text x="450" y="180" fill="white" text-anchor="middle" font-weight="bold">DEIF MAINS</text>
        <text x="450" y="200" fill="white" text-anchor="middle" font-weight="bold">CONTROLLER</text>
        <text x="450" y="130" fill="{cor_gridzero}" text-anchor="middle" font-size="12">{gridzero_texto}</text>

        <!-- Quadro -->
        <rect x="560" y="160" width="80" height="60" fill="#16213e" stroke="white" stroke-width="2"/>
        <text x="600" y="195" fill="white" text-anchor="middle">QUADRO</text>

        <!-- Inversores -->
        <rect x="560" y="250" width="70" height="50" fill="#16213e" stroke="white" stroke-width="1.5"/>
        <text x="595" y="280" fill="white" text-anchor="middle" font-size="10">INV 1</text>

        <rect x="560" y="160" width="70" height="50" fill="#16213e" stroke="white" stroke-width="1.5"/>
        <text x="595" y="190" fill="white" text-anchor="middle" font-size="10">INV 2</text>

        <rect x="560" y="70" width="70" height="50" fill="#16213e" stroke="white" stroke-width="1.5"/>
        <text x="595" y="100" fill="white" text-anchor="middle" font-size="10">INV 3</text>

        <!-- Carga -->
        <rect x="690" y="160" width="80" height="60" fill="#0f3460" stroke="white" stroke-width="2"/>
        <text x="730" y="185" fill="white" text-anchor="middle">CARGA</text>
        <text x="730" y="205" fill="white" text-anchor="middle" font-size="10">{st.session_state.consumo} kW</text>

        <!-- Geração Solar -->
        <rect x="690" y="60" width="80" height="60" fill="#e94560" stroke="white" stroke-width="2"/>
        <text x="730" y="85" fill="white" text-anchor="middle">SOLAR</text>
        <text x="730" y="105" fill="white" text-anchor="middle" font-size="10">{st.session_state.geracao} kW</text>

        <!-- Linhas de conexão -->
        <line x1="150" y1="190" x2="200" y2="190" stroke="white" stroke-width="2"/>
        <line x1="280" y1="190" x2="310" y2="190" stroke="white" stroke-width="2"/>
        <line x1="350" y1="190" x2="390" y2="190" stroke="white" stroke-width="2"/>
        <line x1="510" y1="190" x2="560" y2="190" stroke="white" stroke-width="2"/>
        <line x1="640" y1="190" x2="690" y2="190" stroke="white" stroke-width="2"/>

        <!-- Conexões inversores -->
        <line x1="600" y1="210" x2="595" y2="250" stroke="#e94560" stroke-width="2"/>
        <line x1="600" y1="160" x2="595" y2="160" stroke="#e94560" stroke-width="2"/>
        <line x1="600" y1="120" x2="595" y2="70" stroke="#e94560" stroke-width="2"/>

        <!-- Conexão solar -->
        <line x1="690" y1="90" x2="630" y2="90" stroke="#e94560" stroke-width="2"/>

        <!-- Proteção Siemens ativa -->
        {f'<text x="450" y="270" fill="red" text-anchor="middle" font-size="14" font-weight="bold">⚠️ PROTEÇÃO SIEMENS ATIVA</text>' if st.session_state.protecao_siemens_ativa else ''}

        <!-- Setas de fluxo -->
        {fluxo_texto}
    </svg>
    '''

    st.markdown(svg_diagram, unsafe_allow_html=True)

st.markdown("---")
st.caption("Simulador GridZero com controle DEIF e proteção Siemens. Diagrama em SVG puro (sem matplotlib).")import streamlit as st
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
