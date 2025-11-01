from assistente import *
import unittest
import torch
import os

# caminhos relativos ao diretório deste arquivo (funciona em Windows e Unix)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERIFICAR_SERVIDOR = os.path.join(BASE_DIR, "audios", "verificar-servidor.wav")
REINICIAR_BANCO = os.path.join(BASE_DIR, "audios", "reiniciar-banco.wav")
BACKUP_APP = os.path.join(BASE_DIR, "audios", "backup-app.wav")
CONSULTAR_MEMORIA = os.path.join(BASE_DIR, "audios", "consultar-memoria.wav")
ANALISAR_LOGS = os.path.join(BASE_DIR, "audios", "analisar-logs.wav")


class TestesLampada(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

        cls.iniciado, cls.processador, cls.modelo, _, cls.palavras_de_parada, cls.acoes = iniciar(cls.dispositivo)

    def testar_01_modelo_iniciado(self):
        self.assertTrue(self.iniciado)

    def testar_02_verificar_servidor(self):
        fala = carregar_fala(VERIFICAR_SERVIDOR)
        self.assertIsNotNone(fala)

        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(comando)

        valido, acao, dispositivo_alvo = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertIsNotNone(acao)
        self.assertIsNotNone(dispositivo_alvo)

    def testar_03_reiniciar_banco(self):
        fala = carregar_fala(REINICIAR_BANCO)
        self.assertIsNotNone(fala)

        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(comando)

        valido, acao, dispositivo_alvo = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertIsNotNone(acao)
        self.assertIsNotNone(dispositivo_alvo)

    def testar_04_backup_app(self):
        fala = carregar_fala(BACKUP_APP)
        self.assertIsNotNone(fala)

        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(comando)

        valido, acao, dispositivo_alvo = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertIsNotNone(acao)
        self.assertIsNotNone(dispositivo_alvo)

    def testar_05_analisar_logs(self):
        fala = carregar_fala(ANALISAR_LOGS)
        self.assertIsNotNone(fala)

        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(comando)

        valido, acao, dispositivo_alvo = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertIsNotNone(acao)
        self.assertIsNotNone(dispositivo_alvo)

    def testar_06_consultar_memoria(self):
        fala = carregar_fala(CONSULTAR_MEMORIA)
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