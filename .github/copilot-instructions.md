## Objetivo rápido

Ajude a desenvolver e manter os componentes de reconhecimento de fala e assistente por voz deste repositório. Foque em reproducibilidade, execução local (CPU/GPU) e integração entre transcrição e atuadores em `4_comandos/` e `3_assistente_virtual/`.

## Visão geral da arquitetura

- Pasta `1_introducao_pln/`: utilitários de PLN (tokenização, stopwords, stemming).
- Pasta `2_reconhecimento_de_fala/`: inicialização do modelo Wav2Vec2, transcrição de arquivos WAV e utilitários de configuração de dispositivo (GPU/CPU).
- Pasta `3_assistente_virtual/`: protótipo de assistente que captura áudio em tempo-real e usa os utilitários de `2_reconhecimento_de_fala`.
- Pasta `4_comandos/`: camada de execução de comandos (mapeia transcrições para ações) — contém `config.json` com verbo+dispositivo, atuadores (ex.: `lampada.py`, `som.py`) e o loop principal em `assistente.py`.

Fluxo de dados principal:

- Captura de áudio (microfone via `pyaudio`) → grava WAV em `4_comandos/temp/` → `transcritor.carregar_audio` normaliza e resample → `transcritor.transcrever_fala` usa o modelo Wav2Vec2 → tokens são filtrados por stopwords (`nltk.corpus.stopwords`) → mapeados a ações via `4_comandos/config.json` → executados por atuadores (`lampada.py`, `som.py`).

## Convenções e padrões do projeto

- Modelos HF: funções `iniciar_modelo(nome_modelo, dispositivo)` retornam (iniciado, processador, modelo). Arquivos de inicialização repetem esse padrão (`2_reconhecimento_de_fala/inicializador_modelo.py`, `4_comandos/inicializador_modelo.py`, `3_assistente_virtual/inicializador_modelo.py`).
- Taxa de amostragem esperada: 16000 Hz. Use `TAXA_AMOSTRAGEM = 16000` quando for manipular áudio (ver `transcritor.py`).
- Paths: muitos caminhos são relativos e escritos para Windows (ex.: `reconhecimento_de_fala\audios\ligar_lampada.wav`). Ao editar, prefira usar `os.path.join` para portabilidade.
- Stopwords: o pipeline de comandos usa `nltk.corpus.stopwords.words('portuguese')` para filtrar tokens; preserve esse comportamento ao ampliar o parser de intenções.

## Comandos e fluxos de desenvolvimento comuns

- Instalar dependências:

  - pip install -r requirements.txt

- Iniciar/validar modelo (linha de comando):

  - python 4_comandos/inicializador_modelo.py
  - python 2_reconhecimento_de_fala/inicializador_modelo.py

- Testar transcrição com arquivos de áudio:

  - python 4_comandos/transcritor.py
  - Os exemplos de teste carregam WAVs em `2_reconhecimento_de_fala/audios/`.

- Executar o assistente local (captura por microfone):
  - python 4_comandos/assistente.py
  - O script decide dispositivo chamando `testar_gpu()` (retorna `cuda:0` ou `cpu`).

## Padrões úteis para PRs e mudanças

- Ao alterar a inicialização do modelo, mantenha a assinatura `iniciar_modelo(nome_modelo, dispositivo='cpu') -> (bool, processor, model)` para compatibilidade.
- Sempre respeite a taxa de amostragem 16kHz; se adicionar pre-processing, reutilize `transcritor.carregar_audio`.
- Ao modificar `config.json`, preserve o formato: uma lista em `acoes` com objetos `{"nome": <verbo>, "dispositivo": [<nomes>]}`.

## Integrações e pontos de atenção

- Dependência externa crítica: Hugging Face transformers e modelos Wav2Vec2 (p. ex. `lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2`). Verifique permissões/credenciais de download se a rede bloquear.
- PyAudio: captura em tempo real; em Windows pode exigir instalação de binários/ruidos. Se tests falharem, rodar em modo de arquivo (usar WAVs em `2_reconhecimento_de_fala/audios/`).
- Torch device: use `testar_gpu.py` para decidir entre `cuda:0` e `cpu` — scripts dependem disso para chamar `.to(dispositivo)` no modelo.

## Exemplos rápidos (referências de arquivo)

- Como transcrever um WAV (usa `4_comandos/transcritor.py`): carregue com `carregar_audio(path)` e chame `transcrever_fala(dispositivo, fala, modelo, processador)`.
- Como estender comandos: editar `4_comandos/config.json` e adicionar um atuador em `4_comandos/lampada.py` ou `4_comandos/som.py`, preservando a lista retornada por `iniciar_atuadores()` em `assistente.py`.

## O que um agente deve fazer automaticamente

- Preferir mudanças pequenas e isoladas: alterar apenas um `iniciar_modelo` ou `transcrever_fala` por PR.
- Substituir caminhos hard-coded por `os.path.join` onde for seguro.
- Adicionar testes unitários simples que usam os WAVs em `2_reconhecimento_de_fala/audios/` para validar regressões de transcrição.

## Perguntas abertas / áreas para você revisar

- Confirme se existem mais atuadores hardware/IoT além de `lampada` e `som` que precisam de documentação.
- Indique se prefere que eu converta paths Windows para uso cross-platform em todo o projeto.

---

Se quiser, aplico ajustes (ex.: conversão de paths, testes unitários para transcritor, ou adicionar exemplos de execução no README). Peça qual ação prefere em seguida.
