"""
================================================================================
GRIDZERO SIMULATOR CORE - PROLOGIS DUTRA II / MERCADO LIVRE
Módulo de simulação independente (sem dependências de GUI)
Baseado no Memorial Técnico SolarVolt
Autor: Assistente AI | Data: 2026-05-25
================================================================================
"""

import json


class GridZeroSimulator:
    """
    Motor de simulação do sistema GridZero.
    Implementa a lógica das 4 camadas de proteção + proteções nativas.
    Pode ser usado standalone, via CLI, ou importado em outros projetos.
    """

    def __init__(self):
        # --- Parâmetros do sistema (conforme memorial) ---
        self.potencia_inversores_total = 2400  # kW (24 x SE100K)
        self.margem_importacao = 30  # kW (import bias)
        self.limite_exportacao_alarme = 50  # kW
        self.limite_exportacao_critico = 100  # kW

        # --- Variáveis de entrada ---
        self.geracao_solar = 0.0       # kW
        self.consumo_meli = 1500.0     # kW

        # --- Variáveis calculadas ---
        self.fluxo_rede = 0.0          # kW (>0 importa, <0 exporta)
        self.setpoint_geracao = 0.0    # kW (referência do DEIF)
        self.geracao_efetiva = 0.0     # kW (após limitações)

        # --- Estados dos disjuntores ---
        self.dj_mt_pmt_fechado = True
        self.dj_bt_tr05_fechado = True
        self.dj_bt_tr07_fechado = True
        self.dj_bt_tr08_fechado = True

        # --- Estados das camadas ---
        self.camada_0_ativa = False   # Controle contínuo DEIF
        self.camada_1_ativa = False   # ANSI 32 AGC-150
        self.camada_2_ativa = False   # Relé auxiliar ANSI 32
        self.camada_3_ativa = False   # Siemens 7SR1004 MT
        self.camada_c_ativa = False   # Proteções nativas inversores

        # --- Flags de falha ---
        self.falha_agc = False           # Falha no AGC-150 MAINS
        self.falha_com_agc_asc = False   # Falha comunicação AGC-ASC
        self.falha_com_asc_inv = False   # Falha comunicação ASC-Inversores

        # --- Mensagens de status ---
        self.mensagem_status = "Operação Normal"
        self.cor_status = "#00ccff"

    def calcular_fluxo(self):
        """Calcula o fluxo no ponto de medição do AGC-150."""
        self.fluxo_rede = self.consumo_meli - self.geracao_efetiva
        return self.fluxo_rede

    def processar_controle(self):
        """
        Simula o laço de controle GridZero (Camada 0).
        Em operação normal, o DEIF ajusta a geração para não exportar.
        """
        if self.falha_agc or self.falha_com_agc_asc:
            # Sem controle: inversores ficam no último setpoint ou fallback
            if self.falha_com_asc_inv:
                self.geracao_efetiva = 0  # Fallback F312=0%
            else:
                # Mantém último setpoint (perigoso!)
                self.geracao_efetiva = self.geracao_solar
            return

        # Controle ativo: DEIF calcula setpoint
        if self.geracao_solar > self.consumo_meli - self.margem_importacao:
            # Risco de exportação - reduzir geração
            self.camada_0_ativa = True
            self.setpoint_geracao = max(0, self.consumo_meli - self.margem_importacao)
            self.geracao_efetiva = self.setpoint_geracao
        else:
            self.camada_0_ativa = False
            self.setpoint_geracao = self.geracao_solar
            self.geracao_efetiva = self.geracao_solar

    def verificar_protecoes(self):
        """
        Verifica e atua as camadas de proteção conforme o fluxo de rede.
        Ordem temporal: Camada 0 (contínuo) -> 1 (3-4s) -> 2 (5-7s) -> 3 (8-10s)
        """
        fluxo = self.calcular_fluxo()

        # Reset camadas (exceto 0 que é processada em processar_controle)
        self.camada_1_ativa = False
        self.camada_2_ativa = False
        self.camada_3_ativa = False
        self.camada_c_ativa = False

        # --- CAMADA 1: ANSI 32 do AGC-150 MAINS (3-4 segundos) ---
        # Detecta potência reversa e comanda abertura dos disjuntores BT
        if fluxo < -self.limite_exportacao_alarme and not self.falha_agc:
            self.camada_1_ativa = True
            self.dj_bt_tr05_fechado = False
            self.dj_bt_tr07_fechado = False
            self.dj_bt_tr08_fechado = False
            self.geracao_efetiva = 0
            self.mensagem_status = "CAMADA 1 ATIVA: Disjuntores BT abertos - Usina desconectada"
            self.cor_status = "#ffaa00"

        # --- CAMADA 2: Relé Auxiliar ANSI 32 (5-7 segundos) ---
        # Redundância independente do DEIF
        elif fluxo < -self.limite_exportacao_alarme:
            self.camada_2_ativa = True
            self.dj_bt_tr05_fechado = False
            self.dj_bt_tr07_fechado = False
            self.dj_bt_tr08_fechado = False
            self.geracao_efetiva = 0
            self.mensagem_status = "CAMADA 2 ATIVA: Relé auxiliar desconectou usina"
            self.cor_status = "#ff8800"

        # --- CAMADA 3: Siemens 7SR1004 no PMT (8-10 segundos) ---
        # Último recurso - desliga o disjuntor de MT
        if fluxo < -self.limite_exportacao_critico:
            self.camada_3_ativa = True
            self.dj_mt_pmt_fechado = False
            self.geracao_efetiva = 0
            self.consumo_meli = 0  # Mercado Livre fica sem energia
            self.mensagem_status = "CAMADA 3 ATIVA: DISJUNTOR MT ABERTO - MELI DESLIGADO!"
            self.cor_status = "#ff4444"

        # --- CAMADA C: Proteções nativas dos inversores ---
        # Anti-ilhamento: se MT abre, inversores detectam perda de referência
        if not self.dj_mt_pmt_fechado:
            self.camada_c_ativa = True
            self.geracao_efetiva = 0

        # Status normal
        if not any([self.camada_1_ativa, self.camada_2_ativa, self.camada_3_ativa]):
            if self.camada_0_ativa:
                self.mensagem_status = "Camada 0: GridZero regulando geração (import bias ativo)"
                self.cor_status = "#00ff88"
            else:
                self.mensagem_status = "Operação Normal: Geração < Consumo (importando da rede)"
                self.cor_status = "#00ccff"

    def resetar(self):
        """Reseta todos os estados para condição inicial."""
        self.dj_mt_pmt_fechado = True
        self.dj_bt_tr05_fechado = True
        self.dj_bt_tr07_fechado = True
        self.dj_bt_tr08_fechado = True
        self.camada_0_ativa = False
        self.camada_1_ativa = False
        self.camada_2_ativa = False
        self.camada_3_ativa = False
        self.camada_c_ativa = False
        self.falha_agc = False
        self.falha_com_agc_asc = False
        self.falha_com_asc_inv = False
        self.geracao_efetiva = self.geracao_solar
        self.mensagem_status = "Sistema resetado - Operação Normal"
        self.cor_status = "#00ccff"

    def passo(self):
        """Executa um ciclo completo de simulação."""
        self.processar_controle()
        self.verificar_protecoes()
        return self.get_estado()

    def get_estado(self):
        """Retorna dicionário com o estado atual."""
        return {
            'geracao_solar': self.geracao_solar,
            'geracao_efetiva': self.geracao_efetiva,
            'consumo_meli': self.consumo_meli,
            'fluxo_rede': self.fluxo_rede,
            'setpoint': self.setpoint_geracao,
            'dj_mt': self.dj_mt_pmt_fechado,
            'dj_bt_05': self.dj_bt_tr05_fechado,
            'dj_bt_07': self.dj_bt_tr07_fechado,
            'dj_bt_08': self.dj_bt_tr08_fechado,
            'camada_0': self.camada_0_ativa,
            'camada_1': self.camada_1_ativa,
            'camada_2': self.camada_2_ativa,
            'camada_3': self.camada_3_ativa,
            'camada_c': self.camada_c_ativa,
            'falha_agc': self.falha_agc,
            'falha_com_agc_asc': self.falha_com_agc_asc,
            'falha_com_asc_inv': self.falha_com_asc_inv,
            'mensagem': self.mensagem_status,
            'cor': self.cor_status
        }

    def get_estado_json(self, indent=2):
        """Retorna o estado atual como string JSON formatada."""
        return json.dumps(self.get_estado(), indent=indent, ensure_ascii=False)

    def __repr__(self):
        est = self.get_estado()
        return (
            f"<GridZeroSimulator "
            f"Gen={est['geracao_efetiva']:.0f}kW "
            f"Load={est['consumo_meli']:.0f}kW "
            f"Grid={est['fluxo_rede']:+.0f}kW "
            f"C0={int(est['camada_0'])} "
            f"C1={int(est['camada_1'])} "
            f"C2={int(est['camada_2'])} "
            f"C3={int(est['camada_3'])}>"
        )
