import tkinter as tk
from tkinter import ttk
import time

class GridZeroSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador GridZero - Prologis Dutra II")
        self.root.geometry("800x600")

        # Variáveis de Estado
        self.geracao_potencial = tk.DoubleVar(value=0)
        self.consumo_carga = tk.DoubleVar(value=500)
        self.tempo_exportacao = 0
        self.inicio_exportacao = None
        
        # Estado dos Disjuntores (True = Fechado, False = Aberto)
        self.disjuntor_mt_fechado = True
        self.disjuntores_bt_fechados = True

        self.setup_ui()
        self.atualizar_simulacao()

    def setup_ui(self):
        # Painel de Controle (Inputs)
        controle_frame = ttk.LabelFrame(self.root, text="Controle de Cenário (kW)")
        controle_frame.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Label(controle_frame, text="Potencial de Geração (Inversores):").grid(row=0, column=0, padx=5, pady=5)
        self.scale_geracao = ttk.Scale(controle_frame, from_=0, to=2400, variable=self.geracao_potencial, orient="horizontal", length=300)
        self.scale_geracao.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controle_frame, text="Consumo do Mercado Livre:").grid(row=1, column=0, padx=5, pady=5)
        self.scale_consumo = ttk.Scale(controle_frame, from_=0, to=3000, variable=self.consumo_carga, orient="horizontal", length=300)
        self.scale_consumo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(controle_frame, text="Resetar Proteções", command=self.resetar_sistema).grid(row=0, column=2, rowspan=2, padx=20)

        # Tela do Diagrama (Canvas)
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

    def resetar_sistema(self):
        self.disjuntor_mt_fechado = True
        self.disjuntores_bt_fechados = True
        self.inicio_exportacao = None
        self.tempo_exportacao = 0
        self.geracao_potencial.set(0)

    def atualizar_simulacao(self):
        # Lógica de Controle (Camada 0)
        consumo = self.consumo_carga.get()
        potencial = self.geracao_potencial.get()
        
        # Se os disjuntores BT estão abertos, geração injetada é 0
        geracao_real = 0
        if self.disjuntores_bt_fechados and self.disjuntor_mt_fechado:
            # Camada 0 Atuando: Limita a geração ao consumo (GridZero)
            geracao_real = min(potencial, consumo)
        
        # Simulação de Falha de Controle: Forçando exportação se potencial > consumo
        # Para testar as proteções, podemos criar um botão "Simular Falha DEIF" no futuro.
        # Aqui, vamos assumir que o sistema permite um "vazamento" temporário para ver as proteções agirem.
        exportacao = potencial - consumo if potencial > consumo else 0
        
        if exportacao > 0 and self.disjuntores_bt_fechados and self.disjuntor_mt_fechado:
            if self.inicio_exportacao is None:
                self.inicio_exportacao = time.time()
            self.tempo_exportacao = time.time() - self.inicio_exportacao
            self.verificar_protecoes()
        else:
            self.inicio_exportacao = None
            self.tempo_exportacao = 0

        self.desenhar_diagrama(consumo, geracao_real, exportacao)
        self.root.after(100, self.atualizar_simulacao) # Roda a cada 100ms

    def verificar_protecoes(self):
        # Camada 1: AGC-150 atua nos disjuntores BT (3 a 4s)
        if 3.5 <= self.tempo_exportacao < 8:
            self.disjuntores_bt_fechados = False
            print("TRIP: Camada 1 (AGC-150) atuou. Disjuntores BT abertos.")
            
        # Camada 3: Relé Siemens atua no disjuntor MT (8 a 10s)
        elif self.tempo_exportacao >= 9:
            self.disjuntor_mt_fechado = False
            print("TRIP: Camada 3 (Siemens 7SR1004) atuou. Disjuntor MT aberto.")

    def desenhar_diagrama(self, consumo, geracao, exportacao):
        self.canvas.delete("all")
        
        # Status de Cores
        cor_mt = "green" if self.disjuntor_mt_fechado else "red"
        cor_bt = "green" if self.disjuntores_bt_fechados else "red"

        # Desenhar Cabine Light (Rede)
        self.canvas.create_rectangle(50, 50, 150, 100, fill="lightgray")
        self.canvas.create_text(100, 75, text="Rede Light\n(13.8kV)")

        # Desenhar PMT-02-G200 (Mains Controller / Siemens)
        self.canvas.create_rectangle(300, 50, 450, 150, fill="lightblue", outline=cor_mt, width=3)
        self.canvas.create_text(375, 100, text="PMT-02-G200\nAGC-150 MAINS\nRelé Siemens")
        
        # Desenhar Carga (Mercado Livre)
        self.canvas.create_rectangle(600, 50, 700, 100, fill="orange")
        self.canvas.create_text(650, 75, text=f"Carga MELI\n{consumo:.0f} kW")

        # Desenhar Inversores (ASC-150)
        self.canvas.create_rectangle(300, 300, 450, 350, fill="yellow", outline=cor_bt, width=3)
        self.canvas.create_text(375, 325, text=f"Inversores SE\nGeração: {geracao:.0f} kW")

        # Linhas de Conexão (Diagrama Unifilar Simples)
        self.canvas.create_line(150, 75, 300, 75, width=4) # Light -> PMT
        self.canvas.create_line(450, 75, 600, 75, width=4) # PMT -> Carga
        self.canvas.create_line(375, 150, 375, 300, width=4) # Inversores -> PMT

        # HUD de Informações
        self.canvas.create_text(400, 200, text=f"Fluxo Medido AGC: {consumo - geracao:.0f} kW", font=("Arial", 12, "bold"))
        
        if exportacao > 0 and self.disjuntores_bt_fechados and self.disjuntor_mt_fechado:
            self.canvas.create_text(400, 230, text=f"ALERTA: Exportando {exportacao:.0f} kW", fill="red", font=("Arial", 12, "bold"))
            self.canvas.create_text(400, 250, text=f"Tempo de Falha: {self.tempo_exportacao:.1f}s", fill="red")
            
        # Status Disjuntores
        self.canvas.create_text(375, 35, text=f"Disjuntor MT: {'FECHADO' if self.disjuntor_mt_fechado else 'ABERTO'}", fill=cor_mt, font=("Arial", 10, "bold"))
        self.canvas.create_text(375, 370, text=f"Disjuntor BT: {'FECHADO' if self.disjuntores_bt_fechados else 'ABERTO'}", fill=cor_bt, font=("Arial", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    app = GridZeroSimulator(root)
    root.mainloop()
