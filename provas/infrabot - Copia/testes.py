import unittest
import json
import os
from robo import *

class TesteInfraBot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n[INFO] Iniciando configuração do robô para testes...")
        cls.robo = configurar_robo()
        print("[INFO] Robô configurado com sucesso.\n")
        return super().setUpClass()

    def carregar_conversas(self, arquivo):
        caminho = os.path.join("conversas", arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)["conversas"]

    def testar_todas_conversas(self):
        arquivos = ["saudacoes.json", "monitoramento.json", "comandos.json"]
        total_testes = 0
        falhas = 0

        for arquivo in arquivos:
            print(f"--- Testando arquivo: {arquivo} ---")
            conversas = self.carregar_conversas(arquivo)
            
            for conversa in conversas:
                resposta_esperada = conversa["resposta"]
                mensagens = conversa["mensagens"]
                
                for mensagem in mensagens:
                    total_testes += 1
                    
                    # Hack: Re-inicializar o robô a cada 15 testes para evitar TimeoutError do SQLAlchemy
                    if total_testes % 15 == 0:
                        self.robo = configurar_robo()

                    print(f"Teste #{total_testes}: Enviando '{mensagem}'...")
                    
                    resposta = self.robo.get_response(mensagem)
                    
                    try:
                        self.assertGreaterEqual(resposta.confidence, CONFIANCA_MINIMA)
                        # Verificação flexível: verifica se a resposta obtida é igual à esperada
                        self.assertEqual(resposta.text, resposta_esperada)
                        print(f"   [PASS] Resposta: '{resposta.text}' (Confiança: {resposta.confidence})")
                    except AssertionError as e:
                        print(f"   [FAIL] Esperado: '{resposta_esperada}' | Obtido: '{resposta.text}' (Confiança: {resposta.confidence})")
                        falhas += 1

        print(f"\nResumo dos Testes: Total: {total_testes}, Falhas: {falhas}")
        if falhas > 0:
            self.fail(f"Houve {falhas} falhas nos testes.")

if __name__ == "__main__":
    unittest.main()
