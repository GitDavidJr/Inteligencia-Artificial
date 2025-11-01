from chatterbot import ChatBot

NOME_ROBO = "IFBABot"
CONFIANCA_MINIMA = 0.6

def configurar_robo():
    robo = ChatBot(NOME_ROBO)
    return robo

def executar_robo(robo):
    while True:
        entrada = input("👤: ")
        resposta = robo.get_response(entrada.lower())
        if resposta.confidence >= CONFIANCA_MINIMA:
            print(f"🤖: {resposta}")
        else:
            print("🤖: Desculpe, não entendi.")

if __name__ == "__main__":
    robo = configurar_robo()
    executar_robo(robo)