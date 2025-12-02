from assistente import *
import os
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REINICIAR_BANCO = os.path.join(BASE_DIR, "audios", "reiniciar banco.wav")

def main():
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    iniciado, processador, modelo, _, palavras_de_parada, acoes = iniciar(dispositivo)

    print('modelo iniciado:', iniciado)

    fala = carregar_fala(REINICIAR_BANCO)
    print('arquivo carregado, shape:', None if fala is None else getattr(fala, 'shape', 'scalar'))

    transcricao = transcrever_fala(dispositivo, fala, modelo, processador)
    print('transcricao raw:', transcricao)

    transcricao_normalizada = normalizar_transcricao(transcricao)
    print('transcricao normalizada:', transcricao_normalizada)

    comando = processar_transcricao(transcricao_normalizada, palavras_de_parada)
    print('comando tokens:', comando)

    valido, acao, dispositivo_alvo = validar_comando(comando, acoes)
    print('validar_comando ->', valido, acao, dispositivo_alvo)

if __name__ == '__main__':
    main()
