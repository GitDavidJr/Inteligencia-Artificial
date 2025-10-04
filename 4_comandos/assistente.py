from nltk import word_tokenize, corpus
from inicializador_modelo import *
from threading import Thread
from transcritor import *
from testar_gpu import *
import pyaudio
import secrets
import wave
import json
import os

from lampada import *
from som import *



FORMATO = pyaudio.paInt16
CANAIS = 1
TAXA_AMOSTRAGEM = 16_000
AMOSTRAS_POR_SEGUNDO = 1024
TEMPO_GRAVACAO = 5
CAMINHO_AUDIO_FALAS = "4_comandos/temp"
LINGUAGEM = 'portuguese'
CONFIGURACOES = "4_comandos/config.json"

def iniciar(dispositivo):
    modelo_iniciado, processador, modelo = iniciar_modelo(MODELOS[0], dispositivo)

    gravador = pyaudio.PyAudio()

    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    with open(CONFIGURACOES, "r", encoding="utf-8") as arquivo:
        configuracoes = json.load(arquivo)
        acoes = configuracoes.get("acoes")

        arquivo.close()

    return modelo_iniciado, processador, modelo, gravador, palavras_de_parada, acoes

def capturar_fala(gravador):
    gravacao = gravador.open(format=FORMATO, channels=CANAIS, rate=TAXA_AMOSTRAGEM, input=True, frames_per_buffer=AMOSTRAS_POR_SEGUNDO)
    print("Gravando...")
    falas = []
    for _ in range(0, int(TAXA_AMOSTRAGEM / AMOSTRAS_POR_SEGUNDO * TEMPO_GRAVACAO)):
        dados = gravacao.read(AMOSTRAS_POR_SEGUNDO)
        falas.append(dados)
    gravacao.stop_stream()
    gravacao.close()
    print("Gravação concluída.")
    return falas

def gravar_fala(gravador, fala):
    gravado, arquivo = False, f"{CAMINHO_AUDIO_FALAS}/fala_{secrets.token_hex(32).lower()}.wav"

    try:
        wav = wave.open(arquivo, "wb")
        wav.setnchannels(CANAIS)
        wav.setsampwidth(gravador.get_sample_size(FORMATO))
        wav.setframerate(TAXA_AMOSTRAGEM)
        wav.writeframes(b"".join(fala))
        wav.close()

        gravado = True

    except Exception as e:
        print(f"Erro ao gravar fala: {str(e)}")
    
    return gravado, arquivo 

def processar_transcricao(transcricao, palavras_de_parada):
    comandos = []
    tokens = word_tokenize(transcricao.lower())

    for token in tokens:
        if token not in palavras_de_parada:
            comandos.append(token)

    return comandos

def validar_comando(comandos, acoes):
    valido, acao, dispositivo = False, None, None

    if len(comandos) >= 2:
        acao = comandos[0]
        dispositivo = comandos[1]

        for acao_prevista in acoes:
            if acao == acao_prevista["nome"]:
                if dispositivo in acao_prevista["dispositivo"]:
                    valido = True
                    break

    return valido, acao, dispositivo

def iniciar_atuadores():
    atuadores = []
    
    if iniciar_lampada():
        atuadores.append({
            "nome": "lâmpada",
            "funcao": atuar_sobre_lampada
        })

    if iniciar_som():
        atuadores.append({
            "nome": "som",
            "funcao": atuar_sobre_som
        })

    return atuadores

def atuar(acao, dispositivo, atuadores):
    for atuador in atuadores:
        if dispositivo in atuador["nome"]:
            atuador_thread = Thread(target=atuador["funcao"], args=(acao, dispositivo))
            atuador_thread.start()
            return

    print(f"Nenhum atuador encontrado para o dispositivo: {dispositivo}")

if __name__ == "__main__":
    dispositivo = testar_gpu()
    modelo_iniciado, processador, modelo, gravador, palavras_de_parada, acoes = iniciar(dispositivo)
    atuadores = iniciar_atuadores()

    if modelo_iniciado:
        while True:
            fala = capturar_fala(gravador)
            gravado, arquivo = gravar_fala(gravador, fala)
            if gravado:
                fala = carregar_audio(arquivo)
                transcricao = transcrever_fala(dispositivo, fala, modelo, processador)

                if os.path.exists(arquivo):
                    os.remove(arquivo)

                comando = processar_transcricao(transcricao, palavras_de_parada)

                print(f"Comando processado: {comando}")

                valido, acao, dispositivo_alvo = validar_comando(comando, acoes)

                if valido:
                    print(f"Executando {acao} sobre {dispositivo_alvo}")
                    atuar(acao, dispositivo_alvo, atuadores)
                else:
                    print(f"Comando inválido ou não reconhecido: {transcricao}")
            else:
                print("Erro ao gravar fala. Tente novamente.")
    else:
        print("Modelo não iniciado. Verifique a configuração.")
        exit(1)        
    
