from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

import os

API_KEY = "genai.key"
MODELO = "gemini-3-pro-preview"

def iniciar_IA(contexto = None):
    iniciado, IA = False, None

    try: 
        with open(API_KEY, "r") as arquivo_chave:
            chave = arquivo_chave.read()
            os.environ["GOOGLE_API_KEY"] =  chave

            arquivo_chave.close()

        llm = ChatGoogleGenerativeAI(model = MODELO, max_tokens = None, timeout = 3, max_retries = 2)
        IA = ChatPromptTemplate.from_messages(contexto) | llm if contexto is not None else llm

        iniciado = True
    except Exception as erro:
        print(f"ocorreu um erro iniciando suporte da Google GEMINI: {erro}")

    return iniciado, IA

def obter_resposta(IA, parametros):
    sucesso, resposta = False, None

    try:
        resposta = IA.invoke(parametros)

        sucesso = True
    except Exception as erro:
        print(f"Ocorreu um erro na obtenção da resposta: {erro}")

    return sucesso, resposta

if __name__ == "__main__":
    iniciado, IA = iniciar_IA()
    if iniciado:
        print("Acesso à GOOGLE GEMINI iniciado!")

        sucesso, resposta = obter_resposta(IA, [
            ("system", "você é um assistente bom em traduzir do portugês para o inglês. Traduza a sentença do usuário para o inglês."),
            ("human", "Olá, tudo bem?")
        ])

        if sucesso:
            print("Resposta: ", resposta.content)