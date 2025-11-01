from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import json

CONVERSAS = [
    "conversas/saudacoes.json"
]

NOME_ROBO = "IFBABot"

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
    # cada item em `conversas` é a lista de objetos carregada a partir do JSON
    for conversa in conversas:
        # iterar sobre cada objeto de mensagem/resposta dentro da conversa
        for mensagens_resposta in conversa:
            # usar get() para segurança caso alguma chave esteja ausente
            mensagens = mensagens_resposta.get("mensagens", [])
            resposta = mensagens_resposta.get("resposta")
            if not resposta:
                # nada para treinar se não houver resposta definida
                continue
            for mensagem in mensagens:
                print(f"Treinando com a mensagem: '{mensagem}', resposta: {resposta}")
                # ListTrainer espera uma sequência que represente a troca (entrada, saída)
                treinador.train([mensagem.lower(), resposta])
            
if __name__ == "__main__":
    treinador = configurar_treinador()
    conversas = carregar_conversas()

    if treinador and conversas:
        treinar(treinador, conversas)