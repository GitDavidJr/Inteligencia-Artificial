from inicializacao_openai import *

import json
import os

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_CONVERSAS = os.path.join(DIRETORIO_ATUAL, "conversas")

NOME_ROBO = "IFBABot"
ARQUIVOS_CONVERSAS = [
    os.path.join(PASTA_CONVERSAS, "informacoes_basicas.json"),
    os.path.join(PASTA_CONVERSAS, "sistemas_de_informacao.json"),
]

def inicializar_contexto(mensagens_respostas):
    contexto = [
        ("system", f"Você é {NOME_ROBO}, um assistente virtual especializado em fornecer informações sobre o Instituto Federal da Bahia (IFBA) e seus cursos, especialmente o curso de Sistemas de Informação. Sua função é ajudar os usuários respondendo suas perguntas com base nas informações fornecidas nas conversas de exemplo a seguir. Seja claro, conciso e útil em suas respostas."),
        ("system", f"sempre que alguma pessoa fizer uma saudação, responda com uma saudação apropriada de volta e informar que você não é Humano, e sim um robo de atendiemento chamado {NOME_ROBO}.")
        
    ]

    for mensagem, resposta in mensagens_respostas:
        contexto.append(("system", f"caso a pessoa pergunte {mensagem} ou algo parecido com alguma das mensagens, responda com: {resposta}"))

    contexto.append(("system", "Se a pergunta não estiver relacionada ao IFBA ou aos cursos oferecidos, responda educadamente que você é especializado em fornecer informações sobre o IFBA e seus cursos, e que não pode ajudar com perguntas fora desse escopo. E caso a pessoa insista em perguntar algo fora do seu escopo, responda com: 'desculpe, mas não tenho informações sobre esse assunto. Posso ajudar com perguntas relacionadas ao IFBA e seus cursos.' e caso ainda insista com algo relacionado a algum assunto do ifba, indique que o postal oficial do IFBA é https://portal.ifba.edu.br e que lá a pessoa pode encontrar mais informações."))
    
    contexto.append(("human", "{pergunta}"))
    
    return contexto

def get_mensagens_respostas():
    mensagens_respostas = []

    for caminho in ARQUIVOS_CONVERSAS:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
            conversas = conteudo["conversas"]

            arquivo.close()

        for mensagens_resposta in conversas:
            mensagens = mensagens_resposta["mensagens"]
            resposta = mensagens_resposta["resposta"]

            for mensagem in mensagens:
                mensagens_respostas.append((mensagem, resposta))

    return mensagens_respostas

if __name__ == "__main__":
    mensagens_respostas = get_mensagens_respostas()
    contexto = inicializar_contexto(mensagens_respostas)

    iniciada, IA = iniciar_IA(contexto)
    if iniciada:
        print("acesso à IA iniciado, atendendo usuários...")

        while True:
            pergunta = input("👤 ")

            sucesso, resposta = obter_resposta(IA, {"pergunta": pergunta})
            if sucesso:
                print(f"🤖 {resposta.content}")
            else:
                print(f"🤖 Estou tendo problemas para realizar o processamento de sua mensagem neste momentto. Tente novamente mais tarde.")