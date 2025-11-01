from flask import Flask, Response, request, send_from_directory
from infra_atuadores import iniciar_infra, atuar_sobre_infra
from nltk import word_tokenize, corpus
from inicializador_modelo import *
from threading import Thread
from transcritor import *
import secrets
import pyaudio
import torch
import wave
import json
import sys
import os
import re

# mapeamentos simples para normalizar transcrições que contenham estrangeirismos
# ou erros comuns de reconhecimento (ex.: 'becap' -> 'backup')
NORMALIZACOES = {
    # backup
    r"\bbecap\b": "backup",
    r"\bback ?up\b": "backup",
    r"\bbackap\b": "backup",
    r"\bbakap\b": "backup",
    r"\bbecape\b": "backup",
    r"\bbecup\b": "backup",
    # reiniciar variações
    r"\breiniciar\b": "reiniciar",
    r"\breinicia\b": "reiniciar",
    # juntar formas separadas que o ASR pode emitir: 're iniciar', 're inicia', 'rei inicia'
    r"\bre\s*-?\s*iniciar\b": "reiniciar",
    r"\bre\s*-?\s*inicia\b": "reiniciar",
    r"\brei\s*-?\s*inicia\b": "reiniciar",
    # verificar variantes
    r"\bverifica(r|r)?\b": "verificar",
    # cpu / cpg variantes (captura CEPEU, CEPE, 'c p u', 'acepeu', 'a cepel', etc.)
    r"\bcepeu\b": "cpu",
    r"\bcepe\b": "cpu",
    r"\bcepel\b": "cpu",
    r"\bacepeu\b": "cpu",
    r"\bacepel\b": "cpu",
    r"\bacepe\b": "cpu",
    r"\ba\s+cepeu\b": "cpu",
    r"\ba\s+cepe\b": "cpu",
    r"\ba\s+cepel\b": "cpu",
    r"\bc\s*p\s*u\b": "cpu",
    r"\bcpg\b": "cpu",
}


def normalizar_transcricao(transcricao: str) -> str:
    """Aplica regras simples de normalização por expressões regulares.
    Retorna a transcrição normalizada (minúscula).
    """
    if not transcricao:
        return transcricao

    texto = transcricao.lower()
    for padrao, substituicao in NORMALIZACOES.items():
        try:
            texto = re.sub(padrao, substituicao, texto)
        except re.error:
            # se regex inválida por algum motivo, ignora
            continue

    # colapsa espaços extras
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


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

    # Atuador único para operações de infraestrutura (simulado)
    if iniciar_infra():
        atuadores.append({
            "nome": "infra",
            "atuacao": atuar_sobre_infra
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
        print("erro gravando arquivo de fala")

    return gravado, arquivo

def processar_transcricao(transcricao, palavras_de_parada):
    comando = []
    # normaliza erros comuns antes de tokenizar (corrige variações do ASR)
    try:
        transcricao = normalizar_transcricao(transcricao)
    except Exception:
        # se algo falhar na normalização, prossegue com a transcrição original
        pass

    # retorna tokens úteis (sem stopwords)
    tokens = word_tokenize(transcricao.lower())
    for token in tokens:
        if token not in palavras_de_parada and token.strip():
            comando.append(token)

    return comando

def validar_comando(comando_tokens, acoes):
    """Valida o comando procurando correspondência de ação e dispositivo por substring.
    Retorna (valido, nome_acao, dispositivo_encontrado).
    """
    texto = " ".join(comando_tokens).lower()

    acao_encontrada = None
    dispositivo_encontrado = None

    tokens = texto.split()

    # procura ação: prioridade para correspondência por token exato (mais previsível)
    for acao in acoes:
        nome = acao.get("nome", "").lower()
        nome_raiz = nome.split()[0]

        if nome_raiz in tokens or nome in texto or nome.replace("_", " ") in texto:
            acao_encontrada = nome

            # procura dispositivo por correspondência exata de token primeiro
            for disp in acao.get("dispositivos", []):
                disp_l = disp.lower()
                if disp_l in tokens:
                    dispositivo_encontrado = disp
                    break

            # fallback: busca por substring (menos previsível)
            if not dispositivo_encontrado:
                for disp in acao.get("dispositivos", []):
                    if disp.lower() in texto:
                        dispositivo_encontrado = disp
                        break

            # se ação encontrada mas nenhum dispositivo explícito, tenta extrair palavra após verbo
            if not dispositivo_encontrado:
                try:
                    idx = tokens.index(nome_raiz)
                    if idx + 1 < len(tokens):
                        dispositivo_encontrado = tokens[idx + 1]
                except ValueError:
                    pass

            break

    # se o usuário disse 'verificar' mas o dispositivo é relacionado a uso (cpu/memoria),
    # mapear para a ação 'consultar' se existir nas ações configuradas
    if acao_encontrada == "verificar" and dispositivo_encontrado:
        if any(x in dispositivo_encontrado.lower() for x in ["uso", "cpu", "mem", "memoria", "memória", "cpg"]):
            for a in acoes:
                if a.get("nome") and a.get("nome").lower() == "consultar":
                    acao_encontrada = "consultar"
                    break

    valido = acao_encontrada is not None and dispositivo_encontrado is not None

    return valido, acao_encontrada, dispositivo_encontrado

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

        # DEBUG: imprimir transcrição completa no servidor para testes
        try:
            print(f"[SERVER] transcrição completa (raw): {transcricao}")
        except Exception:
            pass

        # normaliza transcrição para corrigir estrangeirismos / erros comuns
        try:
            transcricao_normalizada = normalizar_transcricao(transcricao)
            print(f"[SERVER] transcrição normalizada: {transcricao_normalizada}")
        except Exception:
            transcricao_normalizada = transcricao

        comando = processar_transcricao(transcricao_normalizada, servico.config.get("palavras_de_parada", set()))
        valido, acao, dispositivo_alvo = validar_comando(comando, servico.config["acoes"])

        if valido:
            print(f"comando válido, executar atuação")

            atuar(acao, dispositivo_alvo, servico.config["atuadores"])

            return Response(json.dumps({"transcricao": transcricao}), status=200)
        else:
            return Response(json.dumps({"transcricao": "Comando não reconhecido."}), status=200)
    except Exception:
        # evitar expor pilha/erro detalhado no output do servidor por previsibilidade
        print("erro ao processar fala")

        return Response(status=500)
    finally:
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)


@servico.get("/status")
def status():
    """Retorna informações de status do assistente para o front-end.
    - nome_assistente (string)
    - modelo_carregado (bool)
    - dispositivo (string)
    - atuadores (lista de nomes)
    """
    modelo = servico.config.get("modelo")
    dispositivo = servico.config.get("dispositivo")
    atuadores = servico.config.get("atuadores", [])

    atuadores_nomes = [a.get("nome") for a in atuadores]

    payload = {
        "nome_assistente": "Assistente de Infraestrutura",
        "modelo_carregado": bool(modelo),
        "dispositivo": dispositivo,
        "atuadores": atuadores_nomes
    }

    return Response(json.dumps(payload), status=200, mimetype="application/json")

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
            {"nome": "verificar", "dispositivos": ["servidor web"]},
            {"nome": "reiniciar", "dispositivos": ["banco de dados"]},
            {"nome": "backup", "dispositivos": ["aplicacao principal"]},
            {"nome": "analisar", "dispositivos": ["logs"]},
            {"nome": "consultar", "dispositivos": ["cpu", "memoria"]}
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