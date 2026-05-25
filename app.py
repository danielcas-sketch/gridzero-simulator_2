import tkinter as tk
from tkinter import ttk, messagebox
import math
import time

class EnergySimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Controle de Energia - Sistema DEIF")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a2e')
        
        # Variáveis de estado
        self.geracao = 0  # kW
        self.consumo = 0  # kW
        self.exportacao = 0  # kW
        self.fluxo_rede = 0  # kW (positivo = importando, negativo = exportando)
        
        # Estados dos dispositivos
        self.disjuntor_media = True  # True = fechado
        self.disjuntores_inversores = [True, True, True]  # 3 inversores
        self.gridzero_ativo = False
        self.funcao32_ativa = False
        self.protecao_siemens_media_ativa = False
        
        # Limites
        self.limite_exportacao = 100  # kW
        self.limite_importacao = 500  # kW
        
        # Animação
        self.animacao_ativa = False
        self.fluxo_particulas = []
        
        self.criar_interface()
        self.atualizar_dashboard()
        
    def criar_interface(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = tk.Label(main_frame, text="SIMULADOR DE CONTROLE DE ENERGIA - SISTEMA DEIF", 
                         font=('Arial', 16, 'bold'), bg='#1a1a2e', fg='white')
        titulo.pack(pady=10)
        
        # Frame de controles
        controle_frame = tk.LabelFrame(main_frame, text="CONTROLES DO CENÁRIO", 
                                      font=('Arial', 12, 'bold'), bg='#16213e', fg='white',
                                      padx=20, pady=20)
        controle_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Grid de controles
        tk.Label(controle_frame, text="Geração Solar (kW):", bg='#16213e', fg='white',
                font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.geracao_scale = tk.Scale(controle_frame, from_=0, to=500, orient=tk.HORIZONTAL,
                                     length=300, command=self.atualizar_geracao,
                                     bg='#0f3460', fg='white', troughcolor='#e94560')
        self.geracao_scale.set(0)
        self.geracao_scale.grid(row=0, column=1, padx=10, pady=5)
        self.geracao_label = tk.Label(controle_frame, text="0 kW", bg='#16213e', fg='white',
                                     font=('Arial', 11, 'bold'))
        self.geracao_label.grid(row=0, column=2, padx=10, pady=5)
        
        tk.Label(controle_frame, text="Consumo Local (kW):", bg='#16213e', fg='white',
                font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.consumo_scale = tk.Scale(controle_frame, from_=0, to=500, orient=tk.HORIZONTAL,
                                     length=300, command=self.atualizar_consumo,
                                     bg='#0f3460', fg='white', troughcolor='#e94560')
        self.consumo_scale.set(0)
        self.consumo_scale.grid(row=1, column=1, padx=10, pady=5)
        self.consumo_label = tk.Label(controle_frame, text="0 kW", bg='#16213e', fg='white',
                                     font=('Arial', 11, 'bold'))
        self.consumo_label.grid(row=1, column=2, padx=10, pady=5)
        
        # Botões de cenário
        botoes_frame = tk.Frame(controle_frame, bg='#16213e')
        botoes_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        tk.Button(botoes_frame, text="Cenário: Exportação", command=self.cenario_exportacao,
                 bg='#e94560', fg='white', font=('Arial', 10, 'bold'), padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(botoes_frame, text="Cenário: Consumo Alto", command=self.cenario_consumo_alto,
                 bg='#0f3460', fg='white', font=('Arial', 10, 'bold'), padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(botoes_frame, text="Cenário: Sobrecarga", command=self.cenario_sobrecarga,
                 bg='#533483', fg='white', font=('Arial', 10, 'bold'), padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(botoes_frame, text="Reset", command=self.reset_sistema,
                 bg='#16213e', fg='white', font=('Arial', 10, 'bold'), padx=10).pack(side=tk.LEFT, padx=5)
        
        # Frame do diagrama
        self.diagrama_frame = tk.LabelFrame(main_frame, text="DIAGRAMA DO SISTEMA", 
                                           font=('Arial', 12, 'bold'), bg='#16213e', fg='white',
                                           padx=20, pady=20)
        self.diagrama_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas para o diagrama
        self.canvas = tk.Canvas(self.diagrama_frame, bg='#0f3460', height=500, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Frame de status
        status_frame = tk.LabelFrame(main_frame, text="STATUS DO SISTEMA", 
                                    font=('Arial', 12, 'bold'), bg='#16213e', fg='white',
                                    padx=20, pady=20)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Labels de status
        self.status_gridzero = tk.Label(status_frame, text="GridZero: INATIVO", 
                                       bg='#16213e', fg='red', font=('Arial', 11, 'bold'))
        self.status_gridzero.grid(row=0, column=0, padx=10, pady=5)
        
        self.status_funcao32 = tk.Label(status_frame, text="Função 32: INATIVA", 
                                       bg='#16213e', fg='red', font=('Arial', 11, 'bold'))
        self.status_funcao32.grid(row=0, column=1, padx=10, pady=5)
        
        self.status_disjuntor_media = tk.Label(status_frame, text="Disjuntor MT: FECHADO", 
                                               bg='#16213e', fg='green', font=('Arial', 11, 'bold'))
        self.status_disjuntor_media.grid(row=0, column=2, padx=10, pady=5)
        
        self.status_exportacao = tk.Label(status_frame, text="Exportação: 0 kW", 
                                         bg='#16213e', fg='white', font=('Arial', 11, 'bold'))
        self.status_exportacao.grid(row=0, column=3, padx=10, pady=5)
        
    def desenhar_diagrama(self):
        self.canvas.delete("all")
        
        # Dimensões do canvas
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w < 100:
            w = 1200
        if h < 100:
            h = 500
            
        # Coordenadas dos elementos
        self.rede_x, self.rede_y = 100, h/2
        self.pmt_x, self.pmt_y = 300, h/2
        self.mains_x, self.mains_y = 450, h/2
        self.quadro_x, self.quadro_y = 650, h/2
        self.inversor1_x, self.inversor1_y = 650, h/2 - 100
        self.inversor2_x, self.inversor2_y = 650, h/2
        self.inversor3_x, self.inversor3_y = 650, h/2 + 100
        self.carga_x, self.carga_y = 850, h/2
        self.geracao_x, self.geracao_y = 1000, h/2 - 150
        
        # Desenhar conexões com animação de fluxo
        self.desenhar_conexao(self.rede_x, self.rede_y, self.pmt_x, self.pmt_y, "REDE")
        self.desenhar_conexao(self.pmt_x, self.pmt_y, self.mains_x, self.mains_y, "PMT")
        self.desenhar_conexao(self.mains_x, self.mains_y, self.quadro_x, self.quadro_y, "MAINS")
        
        # Conexões dos inversores
        self.desenhar_conexao(self.quadro_x, self.quadro_y, self.inversor1_x, self.inversor1_y, "INV1")
        self.desenhar_conexao(self.quadro_x, self.quadro_y, self.inversor2_x, self.inversor2_y, "INV2")
        self.desenhar_conexao(self.quadro_x, self.quadro_y, self.inversor3_x, self.inversor3_y, "INV3")
        
        # Conexão da carga
        self.desenhar_conexao(self.quadro_x, self.quadro_y, self.carga_x, self.carga_y, "CARGA")
        
        # Conexão da geração solar
        self.desenhar_conexao(self.geracao_x, self.geracao_y - 50, self.inversor1_x, self.inversor1_y, "SOLAR")
        
        # Desenhar componentes
        self.desenhar_rede()
        self.desenhar_pmt()
        self.desenhar_mains_controller()
        self.desenhar_disjuntor_media(self.pmt_x, self.pmt_y - 80)
        self.desenhar_inversores()
        self.desenhar_carga()
        self.desenhar_geracao_solar()
        self.desenhar_rele_siemens(self.mains_x, self.mains_y - 120)
        
        # Desenhar setas de fluxo
        self.desenhar_fluxo_energia()
        
    def desenhar_conexao(self, x1, y1, x2, y2, label):
        # Desenhar linha de conexão
        if label in ["INV1", "INV2", "INV3"]:
            # Conexões com disjuntores
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_line(x1, y1, mid_x, mid_y, fill='#e94560', width=3)
            self.canvas.create_line(mid_x, mid_y, x2, y2, fill='#e94560', width=3)
            
            # Disjuntor
            disjuntor_idx = 0 if label == "INV1" else (1 if label == "INV2" else 2)
            estado = self.disjuntores_inversores[disjuntor_idx]
            cor = 'green' if estado else 'red'
            self.canvas.create_rectangle(mid_x-15, mid_y-15, mid_x+15, mid_y+15, 
                                        fill=cor, outline='white', width=2)
            self.canvas.create_text(mid_x, mid_y, text="DJ", fill='white', 
                                   font=('Arial', 8, 'bold'))
        else:
            self.canvas.create_line(x1, y1, x2, y2, fill='#e94560', width=3)
        
    def desenhar_rede(self):
        x, y = self.rede_x, self.rede_y
        self.canvas.create_rectangle(x-60, y-40, x+60, y+40, fill='#533483', outline='white', width=2)
        self.canvas.create_text(x, y, text="REDE\nELÉTRICA", fill='white', font=('Arial', 12, 'bold'))
        self.canvas.create_text(x, y+60, text="LIGHT", fill='white', font=('Arial', 10))
        
    def desenhar_pmt(self):
        x, y = self.pmt_x, self.pmt_y
        self.canvas.create_rectangle(x-60, y-30, x+60, y+30, fill='#0f3460', outline='white', width=2)
        self.canvas.create_text(x, y, text="PMT", fill='white', font=('Arial', 12, 'bold'))
        
    def desenhar_mains_controller(self):
        x, y = self.mains_x, self.mains_y
        # Corpo do DEIF Mains Controller
        self.canvas.create_rectangle(x-70, y-40, x+70, y+40, fill='#e94560', outline='white', width=3)
        self.canvas.create_text(x, y-10, text="DEIF MAINS", fill='white', font=('Arial', 12, 'bold'))
        self.canvas.create_text(x, y+10, text="CONTROLLER", fill='white', font=('Arial', 12, 'bold'))
        
        # Indicador GridZero
        if self.gridzero_ativo:
            self.canvas.create_text(x, y-60, text="GridZero ATIVO", fill='green', font=('Arial', 10, 'bold'))
        else:
            self.canvas.create_text(x, y-60, text="GridZero Inativo", fill='red', font=('Arial', 10))
            
    def desenhar_disjuntor_media(self, x, y):
        # Disjuntor de média tensão
        cor = 'green' if self.disjuntor_media else 'red'
        self.canvas.create_rectangle(x-25, y-15, x+25, y+15, fill=cor, outline='white', width=2)
        self.canvas.create_text(x, y, text="DJ MT", fill='white', font=('Arial', 8, 'bold'))
        self.canvas.create_text(x, y+30, text="Proteção Siemens", fill='white', font=('Arial', 8))
        
    def desenhar_inversores(self):
        # Inversor 1
        x, y = self.inversor1_x, self.inversor1_y
        self.canvas.create_rectangle(x-50, y-25, x+50, y+25, fill='#16213e', outline='white', width=2)
        self.canvas.create_text(x, y, text="INVERSOR 1\nASC-150", fill='white', font=('Arial', 10, 'bold'))
        
        # Inversor 2
        x, y = self.inversor2_x, self.inversor2_y
        self.canvas.create_rectangle(x-50, y-25, x+50, y+25, fill='#16213e', outline='white', width=2)
        self.canvas.create_text(x, y, text="INVERSOR 2\nASC-150", fill='white', font=('Arial', 10, 'bold'))
        
        # Inversor 3
        x, y = self.inversor3_x, self.inversor3_y
        self.canvas.create_rectangle(x-50, y-25, x+50, y+25, fill='#16213e', outline='white', width=2)
        self.canvas.create_text(x, y, text="INVERSOR 3\nASC-150", fill='white', font=('Arial', 10, 'bold'))
        
    def desenhar_rele_siemens(self, x, y):
        # Relé Siemens
        self.canvas.create_rectangle(x-50, y-20, x+50, y+20, fill='#533483', outline='white', width=2)
        self.canvas.create_text(x, y, text="RELÉ SIEMENS", fill='white', font=('Arial', 10, 'bold'))
        
        # Conexão com Mains Controller
        self.canvas.create_line(x, y+20, x, self.mains_y-40, fill='#e94560', width=2, dash=(5,5))
        
        # Indicador de proteção
        if self.protecao_siemens_media_ativa:
            self.canvas.create_text(x, y-35, text="PROTEÇÃO ATIVA", fill='red', font=('Arial', 10, 'bold'))
        
    def desenhar_carga(self):
        x, y = self.carga_x, self.carga_y
        self.canvas.create_rectangle(x-50, y-30, x+50, y+30, fill='#0f3460', outline='white', width=2)
        self.canvas.create_text(x, y, text="CARGA\nLOCAL", fill='white', font=('Arial', 12, 'bold'))
        
        # Mostrar consumo
        self.canvas.create_text(x, y+50, text=f"Consumo: {self.consumo} kW", 
                               fill='white', font=('Arial', 10))
        
    def desenhar_geracao_solar(self):
        x, y = self.geracao_x, self.geracao_y
        # Painéis solares
        for i in range(3):
            panel_x = x - 30 + i*30
            self.canvas.create_rectangle(panel_x-15, y-20, panel_x+15, y+20, 
                                        fill='#e94560', outline='white', width=1)
        
        self.canvas.create_text(x, y+40, text="GERAÇÃO\nSOLAR", fill='white', font=('Arial', 12, 'bold'))
        self.canvas.create_text(x, y+70, text=f"{self.geracao} kW", fill='white', font=('Arial', 10, 'bold'))
        
    def desenhar_fluxo_energia(self):
        # Desenhar setas de fluxo baseado nas condições atuais
        if self.geracao > self.consumo and self.disjuntor_media:
            # Exportando energia
            self.desenhar_seta(self.pmt_x, self.pmt_y, self.rede_x, self.rede_y, 'green')
            self.canvas.create_text(self.rede_x + 100, self.rede_y - 60, 
                                   text=f"Exportando: {abs(self.exportacao)} kW", 
                                   fill='green', font=('Arial', 10, 'bold'))
        elif self.consumo > self.geracao and self.disjuntor_media:
            # Importando energia
            self.desenhar_seta(self.rede_x, self.rede_y, self.pmt_x, self.pmt_y, 'yellow')
            self.canvas.create_text(self.rede_x + 100, self.rede_y - 60, 
                                   text=f"Importando: {abs(self.fluxo_rede)} kW", 
                                   fill='yellow', font=('Arial', 10, 'bold'))
            
        # Fluxo para carga (sempre que houver consumo)
        if self.consumo > 0:
            self.desenhar_seta(self.quadro_x, self.quadro_y, self.carga_x, self.carga_y, 'white')
            
        # Fluxo dos inversores para o quadro
        if self.geracao > 0:
            if self.disjuntores_inversores[0]:
                self.desenhar_seta(self.inversor1_x, self.inversor1_y, self.quadro_x, self.quadro_y, 'orange')
            if self.disjuntores_inversores[1]:
                self.desenhar_seta(self.inversor2_x, self.inversor2_y, self.quadro_x, self.quadro_y, 'orange')
            if self.disjuntores_inversores[2]:
                self.desenhar_seta(self.inversor3_x, self.inversor3_y, self.quadro_x, self.quadro_y, 'orange')
                
    def desenhar_seta(self, x1, y1, x2, y2, cor):
        # Calcular ponto médio para a seta
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Desenhar seta triangular
        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx)
        
        arrow_size = 10
        x3 = mid_x - arrow_size * math.cos(angle - math.pi/6)
        y3 = mid_y - arrow_size * math.sin(angle - math.pi/6)
        x4 = mid_x - arrow_size * math.cos(angle + math.pi/6)
        y4 = mid_y - arrow_size * math.sin(angle + math.pi/6)
        
        self.canvas.create_polygon(mid_x, mid_y, x3, y3, x4, y4, fill=cor, outline=cor)
        
    def atualizar_geracao(self, valor):
        self.geracao = int(valor)
        self.geracao_label.config(text=f"{self.geracao} kW")
        self.calcular_sistema()
        self.desenhar_diagrama()
        self.atualizar_dashboard()
        
    def atualizar_consumo(self, valor):
        self.consumo = int(valor)
        self.consumo_label.config(text=f"{self.consumo} kW")
        self.calcular_sistema()
        self.desenhar_diagrama()
        self.atualizar_dashboard()
        
    def calcular_sistema(self):
        # Calcular balanço de energia
        balanco = self.geracao - self.consumo
        
        if balanco > 0:
            # Excedente de geração - potencial exportação
            self.exportacao = min(balanco, self.limite_exportacao)
            self.fluxo_rede = -self.exportacao  # Negativo = exportando
            
            # Verificar GridZero
            if self.exportacao > 0:
                self.gridzero_ativo = True
                # Controla exportação para não ultrapassar limite
                if self.exportacao >= self.limite_exportacao:
                    self.funcao32_ativa = True
            else:
                self.gridzero_ativo = False
                self.funcao32_ativa = False
        else:
            # Déficit de energia - importando da rede
            self.exportacao = 0
            self.fluxo_rede = abs(balanco)  # Positivo = importando
            self.gridzero_ativo = False
            self.funcao32_ativa = False
            
        # Verificar sobrecarga
        if self.fluxo_rede > self.limite_importacao:
            self.protecao_siemens_media_ativa = True
            self.disjuntor_media = False
        elif self.fluxo_rede < self.limite_importacao and not self.protecao_siemens_media_ativa:
            self.disjuntor_media = True
            
    def atualizar_dashboard(self):
        # Atualizar labels de status
        if self.gridzero_ativo:
            self.status_gridzero.config(text="GridZero: ATIVO", fg='green')
        else:
            self.status_gridzero.config(text="GridZero: INATIVO", fg='red')
            
        if self.funcao32_ativa:
            self.status_funcao32.config(text="Função 32: ATIVA (Limitando Exportação)", fg='green')
        else:
            self.status_funcao32.config(text="Função 32: INATIVA", fg='red')
            
        if self.disjuntor_media:
            self.status_disjuntor_media.config(text="Disjuntor MT: FECHADO", fg='green')
        else:
            self.status_disjuntor_media.config(text="Disjuntor MT: ABERTO (Sobrecarga)", fg='red')
            
        self.status_exportacao.config(text=f"Exportação: {self.exportacao} kW")
        
    def cenario_exportacao(self):
        """Cenário com alta geração e baixo consumo"""
        self.geracao_scale.set(400)
        self.consumo_scale.set(100)
        self.geracao = 400
        self.consumo = 100
        self.geracao_label.config(text="400 kW")
        self.consumo_label.config(text="100 kW")
        self.calcular_sistema()
        self.desenhar_diagrama()
        self.atualizar_dashboard()
        
    def cenario_consumo_alto(self):
        """Cenário com consumo maior que geração"""
        self.geracao_scale.set(200)
        self.consumo_scale.set(450)
        self.geracao = 200
        self.consumo = 450
        self.geracao_label.config(text="200 kW")
        self.consumo_label.config(text="450 kW")
        self.calcular_sistema()
        self.desenhar_diagrama()
        self.atualizar_dashboard()
        
    def cenario_sobrecarga(self):
        """Cenário com sobrecarga para testar proteção"""
        self.geracao_scale.set(100)
        self.consumo_scale.set(600)
        self.geracao = 100
        self.consumo = 600
        self.geracao_label.config(text="100 kW")
        self.consumo_label.config(text="600 kW")
        self.calcular_sistema()
        self.desenhar_diagrama()
        self.atualizar_dashboard()
        
    def reset_sistema(self):
        """Resetar para estado inicial"""
        self.geracao_scale.set(0)
        self.consumo_scale.set(0)
        self.geracao = 0
        self.consumo = 0
        self.exportacao = 0
        self.fluxo_rede = 0
        self.disjuntor_media = True
        self.disjuntores_inversores = [True, True, True]
        self.gridzero_ativo = False
        self.funcao32_ativa = False
        self.protecao_siemens_media_ativa = False
        
        self.geracao_label.config(text="0 kW")
        self.consumo_label.config(text="0 kW")
        self.calcular_sistema()
        self.desenhar_diagrama()
        self.atualizar_dashboard()

def main():
    root = tk.Tk()
    app = EnergySimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
