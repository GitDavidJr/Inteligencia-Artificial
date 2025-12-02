from assistente import *
import unittest
import torch
import os

# caminhos relativos ao diretório deste arquivo (funciona em Windows e Unix)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIGAR_LAMPADA = os.path.join(BASE_DIR, "audios", "ligar lampada.wav")
DESLIGAR_LAMPADA = os.path.join(BASE_DIR, "audios", "desligar lampada.wav")

class TestesLampada(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

        cls.iniciado, cls.processador, cls.modelo, _, cls.palavras_de_parada, cls.acoes = iniciar(cls.dispositivo)

    def testar_01_modelo_iniciado(self):
        self.assertTrue(self.iniciado)

    def testar_02_ligar_lampada(self):
        fala = carregar_fala(LIGAR_LAMPADA)
        self.assertIsNotNone(fala)

        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(comando)

        valido, acao, dispositivo_alvo = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertIsNotNone(acao)
        self.assertIsNotNone(dispositivo_alvo)

    def testar_03_desligar_lampada(self):
        fala = carregar_fala(DESLIGAR_LAMPADA)
        self.assertIsNotNone(fala)

        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(comando)

        valido, acao, dispositivo_alvo = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertIsNotNone(acao)
        self.assertIsNotNone(dispositivo_alvo)

unittest.main()