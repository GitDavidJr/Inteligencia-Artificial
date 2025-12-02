from flask import Flask, Response, request, send_from_directory
from nltk import word_tokenize, corpus
import sys
from inicializador_modelo import *
from threading import Thread
from transcritor import *
import secrets
import pyaudio
import wave
import json
import os

from lampada import *
from som import *

LINGUAGEM = "portuguese"
FORMATO = pyaudio.paInt16
CANAIS = 1
AMOSTRAS = 1024
TEMPO_GRAVACAO = 5
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# diretório onde serão salvos os WAVs temporários
CAMINHO_AUDIO_FALAS = os.path.join(BASE_DIR, "temp")
# arquivo de configuração local ao pacote
CONFIGURACOES = os.path.join(BASE_DIR, "config.json")

# garante que a pasta de arquivos temporários exista
os.makedirs(CAMINHO_AUDIO_FALAS, exist_ok=True)

MODO_LINHA_DE_COMANDO = 1
MODO_WEB = 2
MODO_DE_FUNCIONAMENTO = MODO_WEB # MODO_LINHA_DE_COMANDO

def iniciar(dispositivo):
    modelo_iniciado, processador, modelo = iniciar_modelo(MODELOS[0], dispositivo)

    gravador = pyaudio.PyAudio()

    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    with open(CONFIGURACOES, "r", encoding="utf-8") as arquivo_configuracoes:
        configuracoes = json.load(arquivo_configuracoes)
        acoes = configuracoes["acoes"]

        arquivo_configuracoes.close()

    return modelo_iniciado, processador, modelo, gravador, palavras_de_parada, acoes

def iniciar_atuadores():
    atuadores = []

    if iniciar_lampada():
        atuadores.append({
            "nome": "lâmpada",
            "atuacao": atuar_sobre_lampada
        })

    if iniciar_som():
        atuadores.append({
            "nome": "sistema de som",
            "atuacao": atuar_sobre_som
        })

    return atuadores

def capturar_fala(gravador):
    gravacao = gravador.open(format=FORMATO, channels=CANAIS, rate=TAXA_AMOSTRAGEM, input=True, frames_per_buffer=AMOSTRAS)

    print("fale alguma coisa...")

    fala = []
    for _ in range(0, int(TAXA_AMOSTRAGEM/AMOSTRAS*TEMPO_GRAVACAO)):
        fala.append(gravacao.read(AMOSTRAS))

    gravacao.stop_stream()
    gravacao.close()

    print("fala capturada")

    return fala

def gravar_fala(gravador, fala):
    gravado = False
    arquivo = os.path.join(CAMINHO_AUDIO_FALAS, f"{secrets.token_hex(32).lower()}.wav")

    try:
        wav = wave.open(arquivo, "wb")
        wav.setnchannels(CANAIS)
        wav.setsampwidth(gravador.get_sample_size(FORMATO))
        wav.setframerate(TAXA_AMOSTRAGEM)
        wav.writeframes(b"".join(fala))
        wav.close()

        gravado = True
    except Exception as e:
        print(f"erro gravando arquivo de fala: {str(e)}")

    return gravado, arquivo

def processar_transcricao(transcricao, palavras_de_parada):
    comando = []

    tokens = word_tokenize(transcricao)
    for token in tokens:
        if token not in palavras_de_parada:
            comando.append(token)

    return comando

def validar_comando(comando, acoes):
    valido, acao, dispositivo = False, None, None

    if len(comando) >= 2:
        acao = comando[0]
        dispositivo = comando[1]

        for acao_prevista in acoes:
            if acao == acao_prevista["nome"]:
                if dispositivo in acao_prevista["dispositivos"]:
                    valido = True

                    break

    return valido, acao, dispositivo

def atuar(acao, dispositivo, atuadores):
    for atuador in atuadores:
        print(f"enviando comando para {atuador['nome']}")
        atuacao = Thread(target=atuador["atuacao"], args=[acao, dispositivo])
        atuacao.start()

############################## linha de comando

def ativar_linha_de_comando():
    while True:
        fala = capturar_fala(gravador)
        gravado, arquivo = gravar_fala(gravador, fala)
        if gravado:
            fala = carregar_fala(arquivo)
            transcricao = transcrever_fala(dispositivo, fala, modelo, processador)

            if os.path.exists(arquivo):
                os.remove(arquivo)

            comando = processar_transcricao(transcricao, palavras_de_parada)
            print(f"comando: {comando}")

            valido, acao, dispositivo_alvo = validar_comando(comando, acoes)
            if valido:
                print(f"executando {acao} sobre {dispositivo_alvo}")

                atuar(acao, dispositivo_alvo, atuadores)
            else:
                print("comando inválido")
        else:
            print("ocorreu um erro gravando a fala")

############################## servico web

servico = Flask("assistente", static_folder="public")

@servico.get("/")
def acessar_pagina():
    return send_from_directory("public", "index.html")

@servico.get("/<path:caminho>")
def acessar_pasta_estatica(caminho):
    return send_from_directory("public", caminho)

@servico.post("/reconhecer_comando")
def reconhecer_comando():
    if "fala" not in request.files:
        return Response(status=400)
    
    fala = request.files["fala"]
    caminho_arquivo = os.path.join(CAMINHO_AUDIO_FALAS, f"{secrets.token_hex(32).lower()}.wav")
    fala.save(caminho_arquivo)

    try:
        # se estiver em modo de desenvolvimento sem modelo carregado, devolve transcrição simulada
        if not servico.config.get("modelo"):
            transcricao = "modo-dev: áudio recebido"
        else:
            transcricao = transcrever_fala(servico.config["dispositivo"], carregar_fala(caminho_arquivo), servico.config["modelo"], servico.config["processador"])

        comando = processar_transcricao(transcricao, servico.config.get("palavras_de_parada", set()))
        valido, acao, dispositivo_alvo = validar_comando(comando, servico.config["acoes"])

        if valido:
            print(f"comando válido, executar atuação")

            atuar(acao, dispositivo_alvo, servico.config["atuadores"])

            return Response(json.dumps({"transcricao": transcricao}), status=200)
        else:
            return Response(json.dumps({"transcricao": "Comando não reconhecido."}), status=200)
    except Exception as e:
        print(f"erro ao processar fala: {str(e)}")

        return Response(status=500)
    finally:
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)

def ativar_web(dispositivo, modelo, processador, palavras_de_parada, acoes, atuadores):
    servico.config["dispositivo"] = dispositivo
    servico.config["modelo"] = modelo
    servico.config["processador"] = processador
    servico.config["palavras_de_parada"] = palavras_de_parada
    servico.config["acoes"] = acoes
    servico.config["atuadores"] = atuadores

    servico.run(host="0.0.0.0", port=7001)


def iniciar_dev():
    """Inicia o servidor em modo desenvolvimento sem carregar modelos pesados."""
    dispositivo = "cpu"
    modelo = None
    processador = None
    palavras_de_parada = set()

    # tenta ler config localmente; se não existir, usa ações de exemplo
    try:
        with open(CONFIGURACOES, "r", encoding="utf-8") as f:
            configuracoes = json.load(f)
            acoes = configuracoes.get("acoes", [])
    except Exception:
        print("config.json não encontrado — entrando em modo dev com ações de exemplo")
        acoes = [
            {"nome": "ligar", "dispositivos": ["lampada"]},
            {"nome": "desligar", "dispositivos": ["lampada"]},
            {"nome": "tocar", "dispositivos": ["som"]}
        ]

    atuadores = iniciar_atuadores()

    ativar_web(dispositivo, modelo, processador, palavras_de_parada, acoes, atuadores)

if __name__ == "__main__":
    # permite iniciar em modo dev: servidor web sem carregar modelo pesado
    if "--dev" in sys.argv:
        iniciar_dev()
        sys.exit(0)

    # tenta detectar dispositivo CUDA sem quebrar se torch não estiver instalado
    try:
        import torch
        dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    except Exception:
        dispositivo = "cpu"

    iniciado, processador, modelo, gravador, palavras_de_parada, acoes = iniciar(dispositivo)

    if iniciado:
        atuadores = iniciar_atuadores()

        if MODO_DE_FUNCIONAMENTO == MODO_LINHA_DE_COMANDO:
            ativar_linha_de_comando()
        elif MODO_DE_FUNCIONAMENTO == MODO_WEB:
            ativar_web(dispositivo, modelo, processador, palavras_de_parada, acoes, atuadores)
        else:
            print("modo de funcionamento não implementado")
    else:
        print("ocorre um erro de inicialização")