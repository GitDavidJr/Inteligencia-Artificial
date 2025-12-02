from time import sleep

def iniciar_lampada():
    ...

    return True

def atuar_sobre_lampada(acao, dispositivo):
    if acao in ["ligar", "acender", "desligar", "apagar"] and dispositivo == "lâmpada":
        print(f"lâmpada executando a ação: {acao}")

        ...
    else:
        print(f"lâmpada não executará esta ação")