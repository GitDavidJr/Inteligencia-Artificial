def iniciar_som():
    ...

    return True

def atuar_sobre_som(acao, dispositivo):
    if acao in ["tocar", "parar"] and dispositivo in ["som", "música"]:
        print(f"sistema de som executando a ação: {acao}")

        ...
    else:
        print("sistema de som não executará esta ação")
