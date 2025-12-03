from chatterbot import ChatBot

NOME_ROBO = "InfraBot"
CONFIANCA_MINIMA = 0.50

def configurar_robo():
    robo = ChatBot(NOME_ROBO, read_only = True)

    return robo

def executar_robo(robo):
    while True:
        mensagem = input("👤 ")
        resposta = robo.get_response(mensagem.lower())
        if resposta.confidence >= CONFIANCA_MINIMA:
            print(f"🤖 {resposta.text} [confiança = {resposta.confidence}]")
        else:
            print(f"🤖 Ainda não sei responder esta pergunta. Pergunte outra coisa [confiança = {resposta.confidence}]")

if __name__ == "__main__":
    robo = configurar_robo()

    if robo:
        executar_robo(robo)