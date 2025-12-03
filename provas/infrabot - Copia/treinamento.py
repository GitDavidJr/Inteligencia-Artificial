from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

import json

CONVERSAS = [
    "conversas/saudacoes.json",
    "conversas/monitoramento.json",
    "conversas/comandos.json"
]

NOME_ROBO = "InfraBot"

def configurar_treinador():
    robo = ChatBot(NOME_ROBO)
    treinador = ListTrainer(robo)

    return treinador

def carregar_conversas():
    conversas = []

    for arquivo_conversas in CONVERSAS:
        with open(arquivo_conversas, "r", encoding="utf-8") as arquivo:
            conversas.append(json.load(arquivo)["conversas"])
            arquivo.close()

    return conversas

def treinar(treinador, conversas):
    for conversa in conversas:
        for mensagens_resposta in conversa:
            mensagens = mensagens_resposta["mensagens"]
            resposta = mensagens_resposta["resposta"]

            for mensagem in mensagens:
                print(f"treinando mensagem: '{mensagem}', resposta: '{resposta}'")
                treinador.train([mensagem.lower(), resposta])

if __name__ == "__main__":
    treinador = configurar_treinador()
    conversas = carregar_conversas()

    if treinador and conversas:
        treinar(treinador, conversas)