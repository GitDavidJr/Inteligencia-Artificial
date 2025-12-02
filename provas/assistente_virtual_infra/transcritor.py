from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torchaudio
import torch
import os
import difflib

MODELO = "lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2"

AUDIOS = [
    {
        "comando": "ligar a lâmpada",
        "wav": "/misc/ifba/workspaces/inteligencia artificial/assistente virtual/audios/ligar lampada.wav"
    },
    {
        "comando": "desligar a lâmpada",
        "wav": "/misc/ifba/workspaces/inteligencia artificial/assistente virtual/audios/desligar lampada.wav"
    }
]

def iniciar_modelo(nome_modelo, dispositivo="cpu"):
    iniciado, processador, modelo = False, None, None

    try:
        processador = Wav2Vec2Processor.from_pretrained(nome_modelo)
        modelo = Wav2Vec2ForCTC.from_pretrained(nome_modelo).to(dispositivo)

        iniciado = True
    except Exception as e:
        print(f"erro iniciando o modelo: {str(e)}")

    return iniciado, processador, modelo

TAXA_AMOSTRAGEM = 16_000

def carregar_fala(caminho_audio):
    # valida path e tenta localizar ficheiro semelhante se não existir
    if not os.path.exists(caminho_audio):
        pasta, nome = os.path.split(caminho_audio)
        if not pasta:
            pasta = os.getcwd()

        if os.path.isdir(pasta):
            candidatos = os.listdir(pasta)
            # busca uma correspondência próxima entre nomes (ignora case, espaços, hifens, underlines)
            def normalize(n):
                return n.replace(" ", "").replace("-", "").replace("_", "").lower()

            alvo = normalize(nome)
            melhores = [(c, difflib.SequenceMatcher(a=alvo, b=normalize(c)).ratio()) for c in candidatos]
            melhores = sorted(melhores, key=lambda x: x[1], reverse=True)
            if melhores and melhores[0][1] >= 0.8:
                caminho_audio = os.path.join(pasta, melhores[0][0])
            else:
                raise FileNotFoundError(f"Arquivo de áudio não encontrado: {caminho_audio}")

    audio, amostragem = torchaudio.load(caminho_audio)
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)

    if amostragem != TAXA_AMOSTRAGEM:
        adaptador_amostragem = torchaudio.transforms.Resample(amostragem, TAXA_AMOSTRAGEM)
        audio = adaptador_amostragem(audio)

    return audio.squeeze()

def transcrever_fala(dispositivo, fala, modelo, processador):
    entrada = processador(fala, return_tensors="pt", sampling_rate=TAXA_AMOSTRAGEM).input_values.to(dispositivo)
    saida = modelo(entrada).logits

    predicao = torch.argmax(saida, dim=-1)
    transcricao = processador.batch_decode(predicao)[0]

    return transcricao.lower()

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

    iniciado, processador, modelo = iniciar_modelo(MODELO, dispositivo)
    if iniciado:
        for audio in AUDIOS:
            print(f"testando transcrição do comando: {audio['comando']}")

            fala = carregar_fala(audio["wav"])
            transcricao = transcrever_fala(dispositivo, fala, modelo, processador)

            print(f"transcrição: {transcricao}")