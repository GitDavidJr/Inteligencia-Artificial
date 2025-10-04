def iniciar_som():
    ...
    return True

def atuar_sobre_som(acao, dispositivo):
    if acao in ["tocar", "parar"] and dispositivo in ["som", "música"]:
        print(f"Ação '{acao}' executada sobre o {dispositivo}.")
    else:
        print("Som não executará essa ação.")