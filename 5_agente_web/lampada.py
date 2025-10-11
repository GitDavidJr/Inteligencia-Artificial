def iniciar_lampada():
    ...
    return True

def atuar_sobre_lampada(acao, dispositivo):
    if acao in ["ligar", "acender", "desligar", "apagar"] and dispositivo == "lâmpada":
        print(f"Ação '{acao}' executada sobre a {dispositivo}.")
        ...
    else:
        print("lampada não executara essa ação.")