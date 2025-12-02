from robo import *
from flask import Flask, Response
import json

robo = configurar_robo()
servico = Flask(NOME_ROBO)

INFO = {
    "versao": "0.0.1",
    "descricao": "Um robô de atendimento especialista sobre a instituição de ensino, IFBA",
    "autor": "luis paulo"
}

@servico.get("/")
def get_info():
    return Response(json.dumps(INFO).encode("utf-8"), status = 200)

@servico.get("/resposta/<string:mensagem>")
def get_resposta(mensagem):
    resposta = robo.get_response(mensagem.lower())
    resposta = {
        "resposta": resposta.text,
        "confianca": resposta.confidence
    }

    return Response(json.dumps(resposta).encode("utf-8"), status=200)

if __name__ == "__main__":
    servico.run(host="0.0.0.0", port=7000, debug=True)