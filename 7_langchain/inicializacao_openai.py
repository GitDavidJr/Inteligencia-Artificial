from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

API_KEY = "openai.key"
MODELO = "gpt-5-nano"

def iniciar_IA(contexto = None):
    iniciado, IA = False, None

    try: 
        with open(API_KEY, "r") as arquivo_chave:
            chave = arquivo_chave.read().strip()
            os.environ["OPENAI_API_KEY"] =  chave
            
            arquivo_chave.close()

        llm = ChatOpenAI(model = MODELO, max_tokens = None, timeout = 10, max_retries = 2)
        IA = ChatPromptTemplate.from_messages(contexto) | llm if contexto is not None else llm

        iniciado = True
    except Exception as erro:
        print(f"ocorreu um erro iniciando suporte da OpenAI: {erro}")

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
        print("Acesso à OpenAI iniciado!")

        sucesso, resposta = obter_resposta(IA, [
            ("system", "você é um assistente bom em traduzir do portugês para o inglês. Traduza a sentença do usuário para o inglês."),
            ("human", "Olá, tudo bem?")
        ])

        if sucesso:
            print("Resposta: ", resposta.content)
