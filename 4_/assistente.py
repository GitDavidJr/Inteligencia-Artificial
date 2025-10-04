from nltk import word_tokenize, corpus
from inicializador_modelo import *
from transcritor import *
from testar_gpu import *
import pyaudio
import secrets
import wave
import os



FORMATO = pyaudio.paInt16
CANAIS = 1
TAXA_AMOSTRAGEM = 16_000
AMOSTRAS_POR_SEGUNDO = 1024
TEMPO_GRAVACAO = 5
CAMINHO_AUDIO_FALAS = "3_assistente_virtual/temp"
LINGUAGEM = 'portuguese'

def iniciar(dispositivo):
    modelo_iniciado, processador, modelo = iniciar_modelo(MODELOS[0], dispositivo)

    gravador = pyaudio.PyAudio()

    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    return modelo_iniciado, processador, modelo, gravador, palavras_de_parada

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

if __name__ == "__main__":
    dispositivo = testar_gpu()
    modelo_iniciado, processador, modelo, gravador, palavras_de_parada = iniciar(dispositivo)

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
            else:
                print("Erro ao gravar fala. Tente novamente.")
    else:
        print("Modelo não iniciado. Verifique a configuração.")
        exit(1)        
    
