#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
EXEMPLO DE USO STANDALONE - GridZeroSimulator
================================================================================
Demonstra como usar o motor de simulação sem interface gráfica.
Pode ser executado via: python exemplo_uso.py
"""

from simulador_core import GridZeroSimulator


def banner():
    print("=" * 70)
    print("  SIMULADOR GRIDZERO - MODO CONSOLE")
    print("  Prologis Dutra II / Mercado Livre")
    print("=" * 70)


def print_estado(sim, titulo="Estado Atual"):
    """Imprime o estado formatado no console."""
    est = sim.get_estado()
    print(f"
┌─ {titulo} {'─' * (62 - len(titulo))}┐")
    print(f"│  Geração Solar:    {est['geracao_solar']:>6.0f} kW  →  Efetiva: {est['geracao_efetiva']:>6.0f} kW")
    print(f"│  Consumo MELI:     {est['consumo_meli']:>6.0f} kW")
    print(f"│  Fluxo Rede:       {est['fluxo_rede']:>+6.0f} kW  ({'Importando' if est['fluxo_rede'] > 0 else 'Exportando!' if est['fluxo_rede'] < 0 else 'Balanceado'})")
    print(f"│  Setpoint DEIF:    {est['setpoint']:>6.0f} kW")
    print(f"│")
    print(f"│  Disjuntores:  MT={'FECHADO' if est['dj_mt'] else 'ABERTO!'}  BT05={'F' if est['dj_bt_05'] else 'A'}  BT07={'F' if est['dj_bt_07'] else 'A'}  BT08={'F' if est['dj_bt_08'] else 'A'}")
    print(f"│")
    print(f"│  Camadas:  C0={'●' if est['camada_0'] else '○'}  C1={'●' if est['camada_1'] else '○'}  C2={'●' if est['camada_2'] else '○'}  C3={'●' if est['camada_3'] else '○'}  CC={'●' if est['camada_c'] else '○'}")
    print(f"│")
    print(f"│  Falhas:   AGC={'FALHA' if est['falha_agc'] else 'OK'}  COM_AGC-ASC={'FALHA' if est['falha_com_agc_asc'] else 'OK'}  COM_ASC-INV={'FALHA' if est['falha_com_asc_inv'] else 'OK'}")
    print(f"│")
    print(f"│  Status:   {est['mensagem']}")
    print(f"└{'─' * 68}┘")


def demo_cenarios():
    """Executa uma série de cenários pré-definidos."""
    sim = GridZeroSimulator()
    banner()

    # Cenário 1: Operação Normal (geração < consumo)
    print("
>>> CENÁRIO 1: Operação Normal (Dia nublado)")
    sim.resetar()
    sim.geracao_solar = 400
    sim.consumo_meli = 1500
    sim.passo()
    print_estado(sim, "Cenário 1 - Normal")

    # Cenário 2: GridZero atuando (geração > consumo, mas controlado)
    print("
>>> CENÁRIO 2: GridZero Regulando (Pico solar, carga alta)")
    sim.resetar()
    sim.geracao_solar = 2200
    sim.consumo_meli = 2000
    sim.passo()
    print_estado(sim, "Cenário 2 - Regulação Camada 0")

    # Cenário 3: Risco de Exportação - Camada 1
    print("
>>> CENÁRIO 3: Risco Exportação - Camada 1 (ANSI 32 AGC)")
    sim.resetar()
    sim.geracao_solar = 2000
    sim.consumo_meli = 800  # Carga baixa, muita geração
    sim.passo()
    print_estado(sim, "Cenário 3 - Camada 1 Ativa")

    # Cenário 4: Falha de comunicação AGC-ASC + Exportação
    print("
>>> CENÁRIO 4: Falha Comunicação AGC-ASC + Exportação")
    sim.resetar()
    sim.geracao_solar = 2000
    sim.consumo_meli = 300
    sim.falha_com_agc_asc = True
    sim.passo()
    print_estado(sim, "Cenário 4 - Falha Com + Export")

    # Cenário 5: Falha AGC + Exportação Crítica - Camada 3
    print("
>>> CENÁRIO 5: Falha AGC + Exportação Crítica - Camada 3")
    sim.resetar()
    sim.geracao_solar = 2500
    sim.consumo_meli = 100
    sim.falha_agc = True
    sim.passo()
    print_estado(sim, "Cenário 5 - Camada 3 Ativa")

    # Cenário 6: Reset e recuperação
    print("
>>> CENÁRIO 6: Reset do Sistema")
    sim.resetar()
    sim.passo()
    print_estado(sim, "Cenário 6 - Após Reset")

    print("
" + "=" * 70)
    print("  DEMO CONCLUÍDA")
    print("=" * 70)


def modo_interativo():
    """Modo interativo via console."""
    sim = GridZeroSimulator()
    banner()
    print("
Comandos disponíveis:")
    print("  gen <valor>    - Define geração solar (0-2400 kW)")
    print("  load <valor>   - Define consumo MELI (0-3000 kW)")
    print("  falha_agc      - Toggle falha AGC-150")
    print("  falha_com      - Toggle falha comunicação AGC-ASC")
    print("  falha_asc      - Toggle falha comunicação ASC-Inversores")
    print("  reset          - Reseta sistema")
    print("  estado         - Mostra estado atual")
    print("  json           - Exporta estado como JSON")
    print("  demo           - Executa cenários pré-definidos")
    print("  sair           - Encerra")
    print("=" * 70)

    sim.passo()
    print_estado(sim, "Inicial")

    while True:
        try:
            cmd = input("
gridzero> ").strip().lower()
            if not cmd:
                continue
            if cmd == "sair":
                break
            elif cmd == "demo":
                demo_cenarios()
                continue
            elif cmd == "reset":
                sim.resetar()
                sim.passo()
                print_estado(sim, "Reset")
            elif cmd == "estado":
                sim.passo()
                print_estado(sim, "Estado")
            elif cmd == "json":
                print(sim.get_estado_json())
            elif cmd == "falha_agc":
                sim.falha_agc = not sim.falha_agc
                sim.passo()
                print_estado(sim, f"Falha AGC={'ON' if sim.falha_agc else 'OFF'}")
            elif cmd == "falha_com":
                sim.falha_com_agc_asc = not sim.falha_com_agc_asc
                sim.passo()
                print_estado(sim, f"Falha COM={'ON' if sim.falha_com_agc_asc else 'OFF'}")
            elif cmd == "falha_asc":
                sim.falha_com_asc_inv = not sim.falha_com_asc_inv
                sim.passo()
                print_estado(sim, f"Falha ASC-INV={'ON' if sim.falha_com_asc_inv else 'OFF'}")
            elif cmd.startswith("gen "):
                val = float(cmd.split()[1])
                sim.geracao_solar = max(0, min(2400, val))
                sim.passo()
                print_estado(sim, f"Geração = {sim.geracao_solar:.0f} kW")
            elif cmd.startswith("load "):
                val = float(cmd.split()[1])
                sim.consumo_meli = max(0, min(3000, val))
                sim.passo()
                print_estado(sim, f"Consumo = {sim.consumo_meli:.0f} kW")
            else:
                print("Comando desconhecido. Digite 'sair' para encerrar.")
        except (ValueError, IndexError):
            print("Erro: valor inválido. Use: gen 1500 ou load 2000")
        except KeyboardInterrupt:
            print("
Encerrando...")
            break

    print("
Simulador finalizado.")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_cenarios()
    else:
        modo_interativo()
