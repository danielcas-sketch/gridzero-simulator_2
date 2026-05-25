import streamlit as st

st.set_page_config(page_title="Simulador DEIF - GridZero", layout="wide")
st.title("⚡ Simulador de Controle de Energia - Sistema DEIF")

# Estado da sessão
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

# Interface
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎮 Controles")
    geracao = st.slider("🌞 Geração Solar (kW)", 0, 500, st.session_state.geracao, key="slider_geracao")
    consumo = st.slider("🏭 Consumo Local (kW)", 0, 500, st.session_state.consumo, key="slider_consumo")
    if geracao != st.session_state.geracao or consumo != st.session_state.consumo:
        st.session_state.geracao = geracao
        st.session_state.consumo = consumo
        calcular_sistema()

    st.markdown("---")
    st.subheader("📋 Cenários Rápidos")
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("🌅 Exportação (400/100)", use_container_width=True):
        st.session_state.geracao = 400
        st.session_state.consumo = 100
        calcular_sistema()
    if col_b.button("🔥 Consumo Alto (200/450)", use_container_width=True):
        st.session_state.geracao = 200
        st.session_state.consumo = 450
        calcular_sistema()
    if col_c.button("⚠️ Sobrecarga (100/600)", use_container_width=True):
        st.session_state.geracao = 100
        st.session_state.consumo = 600
        calcular_sistema()
    if st.button("🔄 Reset Sistema", use_container_width=True):
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
    direcao = "importando" if st.session_state.fluxo_rede > 0 else "exportando"
    st.metric("Fluxo da Rede", f"{abs(st.session_state.fluxo_rede)} kW ({direcao})")

with col2:
    st.subheader("🔌 Diagrama do Sistema")

    # Cores dinâmicas
    cor_dj = "#2ecc71" if st.session_state.disjuntor_media else "#e74c3c"  # verde ou vermelho
    cor_gridzero_texto = "#2ecc71" if st.session_state.gridzero_ativo else "#e74c3c"
    status_dj = "FECHADO" if st.session_state.disjuntor_media else "ABERTO"
    
    # Texto de fluxo
    fluxo_info = ""
    seta_esquerda = ""
    seta_direita = ""
    if st.session_state.geracao > st.session_state.consumo and st.session_state.disjuntor_media:
        fluxo_info = f'<text x="250" y="50" fill="#f1c40f" font-size="14" font-weight="bold">→ EXPORTANDO {st.session_state.exportacao} kW →</text>'
        seta_direita = '<polygon points="170,195 190,185 190,205" fill="#f1c40f"/>'
    elif st.session_state.consumo > st.session_state.geracao and st.session_state.disjuntor_media:
        fluxo_info = f'<text x="250" y="50" fill="#f1c40f" font-size="14" font-weight="bold">← IMPORTANDO {st.session_state.fluxo_rede} kW ←</text>'
        seta_esquerda = '<polygon points="310,195 290,185 290,205" fill="#f1c40f"/>'

    svg_diagram = f'''
    <svg width="100%" height="550" viewBox="0 0 900 450" xmlns="http://www.w3.org/2000/svg" style="background-color:#0f172a; border-radius:15px; font-family: Arial, sans-serif;">
        <defs>
            <filter id="sombra" x="-5%" y="-5%" width="120%" height="120%">
                <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.5"/>
            </filter>
            <marker id="seta_dir" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#f1c40f"/>
            </marker>
            <marker id="seta_esq" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto">
                <polygon points="10 0, 0 3.5, 10 7" fill="#f1c40f"/>
            </marker>
        </defs>

        <!-- Título do diagrama -->
        <text x="450" y="35" fill="white" text-anchor="middle" font-size="20" font-weight="bold">DIAGRAMA UNIFILAR - SISTEMA DEIF</text>

        <!-- REDE -->
        <rect x="40" y="180" width="110" height="70" fill="#1e293b" stroke="#94a3b8" stroke-width="2" rx="8" filter="url(#sombra)"/>
        <text x="95" y="210" fill="#38bdf8" text-anchor="middle" font-size="14" font-weight="bold">REDE</text>
        <text x="95" y="230" fill="#94a3b8" text-anchor="middle" font-size="11">ELÉTRICA</text>

        <!-- Linha Rede → PMT -->
        <line x1="150" y1="215" x2="200" y2="215" stroke="#cbd5e1" stroke-width="3"/>
        {seta_direita}
        {seta_esquerda}

        <!-- PMT -->
        <rect x="200" y="180" width="90" height="70" fill="#1e293b" stroke="#94a3b8" stroke-width="2" rx="8" filter="url(#sombra)"/>
        <text x="245" y="215" fill="#38bdf8" text-anchor="middle" font-size="16" font-weight="bold">PMT</text>
        <text x="245" y="235" fill="#94a3b8" text-anchor="middle" font-size="10">13.8 kV</text>

        <!-- Linha PMT → Disjuntor -->
        <line x1="290" y1="215" x2="330" y2="215" stroke="#cbd5e1" stroke-width="3"/>

        <!-- Disjuntor MT -->
        <rect x="330" y="180" width="60" height="70" fill="{cor_dj}" stroke="white" stroke-width="2" rx="8" filter="url(#sombra)"/>
        <text x="360" y="210" fill="white" text-anchor="middle" font-size="12" font-weight="bold">DJ MT</text>
        <text x="360" y="230" fill="white" text-anchor="middle" font-size="10">{status_dj}</text>

        <!-- Linha Disjuntor → DEIF -->
        <line x1="390" y1="215" x2="430" y2="215" stroke="#cbd5e1" stroke-width="3"/>

        <!-- DEIF Mains Controller (destacado) -->
        <rect x="430" y="150" width="140" height="110" fill="#e94560" stroke="#facc15" stroke-width="3" rx="10" filter="url(#sombra)"/>
        <text x="500" y="185" fill="white" text-anchor="middle" font-size="16" font-weight="bold">DEIF MAINS</text>
        <text x="500" y="205" fill="white" text-anchor="middle" font-size="14" font-weight="bold">CONTROLLER</text>
        <text x="500" y="230" fill="{cor_gridzero_texto}" text-anchor="middle" font-size="13" font-weight="bold">⚡ GridZero</text>
        {f'<text x="500" y="245" fill="#facc15" text-anchor="middle" font-size="11">Função 32 ATIVA</text>' if st.session_state.funcao32_ativa else ''}

        <!-- Linha DEIF → Quadro -->
        <line x1="570" y1="205" x2="610" y2="205" stroke="#cbd5e1" stroke-width="3"/>

        <!-- Quadro Geral -->
        <rect x="610" y="180" width="90" height="70" fill="#1e293b" stroke="#94a3b8" stroke-width="2" rx="8" filter="url(#sombra)"/>
        <text x="655" y="210" fill="#38bdf8" text-anchor="middle" font-size="14" font-weight="bold">QUADRO</text>
        <text x="655" y="230" fill="#94a3b8" text-anchor="middle" font-size="11">GERAL</text>

        <!-- Ramificações para inversores (vertical) -->
        <line x1="655" y1="250" x2="655" y2="290" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="655" y1="290" x2="580" y2="290" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="655" y1="290" x2="730" y2="290" stroke="#cbd5e1" stroke-width="2"/>
        
        <!-- Inversor 1 -->
        <rect x="520" y="300" width="100" height="50" fill="#334155" stroke="#facc15" stroke-width="2" rx="6"/>
        <text x="570" y="320" fill="white" text-anchor="middle" font-size="12" font-weight="bold">INVERSOR 1</text>
        <text x="570" y="338" fill="#94a3b8" text-anchor="middle" font-size="10">ASC-150</text>
        <line x1="570" y1="350" x2="570" y2="370" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="570" y1="370" x2="570" y2="390" stroke="#facc15" stroke-width="2" stroke-dasharray="4"/>

        <!-- Inversor 2 -->
        <rect x="520" y="300" width="100" height="50" fill="#334155" stroke="#facc15" stroke-width="2" rx="6"/>
        <text x="570" y="320" fill="white" text-anchor="middle" font-size="12" font-weight="bold">INVERSOR 2</text>
        <text x="570" y="338" fill="#94a3b8" text-anchor="middle" font-size="10">ASC-150</text>
        <!-- (não desenhamos o INV2 separadamente, pois a posição x=570 é a mesma; melhor distribuir horizontalmente) -->
        
        <!-- Vamos corrigir: três inversores lado a lado -->
        <!-- Inversor 1 (esquerda) -->
        <rect x="520" y="300" width="80" height="50" fill="#334155" stroke="#facc15" stroke-width="2" rx="6"/>
        <text x="560" y="320" fill="white" text-anchor="middle" font-size="11">INV 1</text>
        <text x="560" y="338" fill="#94a3b8" text-anchor="middle" font-size="9">ASC-150</text>
        <line x1="560" y1="350" x2="560" y2="370" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="560" y1="370" x2="560" y2="390" stroke="#facc15" stroke-width="2" stroke-dasharray="4"/>

        <!-- Inversor 2 (centro) -->
        <rect x="615" y="300" width="80" height="50" fill="#334155" stroke="#facc15" stroke-width="2" rx="6"/>
        <text x="655" y="320" fill="white" text-anchor="middle" font-size="11">INV 2</text>
        <text x="655" y="338" fill="#94a3b8" text-anchor="middle" font-size="9">ASC-150</text>
        <line x1="655" y1="350" x2="655" y2="370" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="655" y1="370" x2="655" y2="390" stroke="#facc15" stroke-width="2" stroke-dasharray="4"/>

        <!-- Inversor 3 (direita) -->
        <rect x="710" y="300" width="80" height="50" fill="#334155" stroke="#facc15" stroke-width="2" rx="6"/>
        <text x="750" y="320" fill="white" text-anchor="middle" font-size="11">INV 3</text>
        <text x="750" y="338" fill="#94a3b8" text-anchor="middle" font-size="9">ASC-150</text>
        <line x1="750" y1="350" x2="750" y2="370" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="750" y1="370" x2="750" y2="390" stroke="#facc15" stroke-width="2" stroke-dasharray="4"/>

        <!-- Conexões do quadro para os inversores -->
        <line x1="655" y1="250" x2="560" y2="300" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="655" y1="250" x2="655" y2="300" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="655" y1="250" x2="750" y2="300" stroke="#cbd5e1" stroke-width="2"/>

        <!-- Carga -->
        <rect x="780" y="180" width="100" height="70" fill="#1e293b" stroke="#94a3b8" stroke-width="2" rx="8" filter="url(#sombra)"/>
        <text x="830" y="210" fill="#38bdf8" text-anchor="middle" font-size="14" font-weight="bold">CARGA</text>
        <text x="830" y="230" fill="#facc15" text-anchor="middle" font-size="15" font-weight="bold">{st.session_state.consumo} kW</text>

        <!-- Linha Quadro → Carga -->
        <line x1="700" y1="205" x2="780" y2="205" stroke="#cbd5e1" stroke-width="3"/>

        <!-- Geração Solar -->
        <rect x="780" y="60" width="100" height="70" fill="#2d6a4f" stroke="#74c69d" stroke-width="2" rx="8" filter="url(#sombra)"/>
        <text x="830" y="90" fill="#74c69d" text-anchor="middle" font-size="14" font-weight="bold">SOLAR</text>
        <text x="830" y="110" fill="#facc15" text-anchor="middle" font-size="15" font-weight="bold">{st.session_state.geracao} kW</text>

        <!-- Conexão Solar → Inversores -->
        <line x1="830" y1="130" x2="830" y2="170" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="830" y1="170" x2="750" y2="170" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="750" y1="170" x2="750" y2="300" stroke="#facc15" stroke-width="2" stroke-dasharray="4"/>
        <line x1="830" y1="170" x2="655" y2="170" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="655" y1="170" x2="655" y2="300" stroke="#facc15" stroke-width="2" stroke-dasharray="4"/>
        <line x1="830" y1="170" x2="560" y2="170" stroke="#cbd5e1" stroke-width="2"/>
        <line x1="560" y1="170" x2="560" y2="300" stroke="#facc15" stroke-width="2" stroke-dasharray="4"/>

        <!-- Proteção Siemens ativa (destaque) -->
        {f'<rect x="400" y="260" width="200" height="30" fill="#e74c3c" rx="5" /><text x="500" y="280" fill="white" text-anchor="middle" font-size="13" font-weight="bold">⚠️ PROTEÇÃO SIEMENS ATIVA ⚠️</text>' if st.session_state.protecao_siemens_ativa else ''}

        <!-- Informações de fluxo -->
        {fluxo_info}
    </svg>
    '''
    st.markdown(svg_diagram, unsafe_allow_html=True)

st.markdown("---")
st.caption("Simulador GridZero com controle DEIF, função 32 e proteção Siemens. Diagrama em SVG com layout melhorado.")
