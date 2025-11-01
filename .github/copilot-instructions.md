## Objetivo rápido

Ajude a desenvolver e manter os componentes de reconhecimento de fala e assistente por voz deste repositório. Foque em reproducibilidade, execução local (CPU/GPU) e integração entre transcrição e atuadores em `4_comandos/` e `3_assistente_virtual/`.

```markdown
## Objetivo rápido

Fornecer instruções práticas para agentes automatizados focados nos componentes de reconhecimento de fala e assistente por voz: executar localmente (CPU/GPU), reproduzir transcrições e ligar atuadores (lampada/som).

## Estrutura essencial (onde olhar primeiro)

- `1_introducao_pln/` — utilitários de PLN (tokenização, stopwords, stemming).
- `2_reconhecimento_de_fala/` — inicializador Wav2Vec2, `transcritor.py`, WAVs de teste em `audios/`.
- `3_assistente_virtual/`, `4_comandos/`, `5_agente_web/` — variantes do assistente: captura, mapeamento de intenções e atuadores (cada pasta tem seu `inicializador_modelo.py`, `transcritor.py`, `assistente.py`).
- `assistente_virtual_infra/` e `assistente_virtual_professor/` — forks/implementações auxiliares; úteis para exemplos de atuadores e testes (`testes.py`).

## Fluxo de dados padrão

Microfone (PyAudio) → grava WAV em `*/temp/` → `transcritor.carregar_audio()` (resample para 16kHz) → `transcritor.transcrever_fala()` (modelo HF) → filtra stopwords (NLTK) → mapeia para ações via `config.json` → chama atuadores (`lampada.py`, `som.py`).

## Convenções importantes (seguir exatamente)

- Assinatura padrão: iniciar_modelo(nome_modelo, dispositivo='cpu') -> (bool, processor, model). Preserve-a ao alterar inicializadores.
- Taxa de amostragem: use TAXA_AMOSTRAGEM = 16000 e `transcritor.carregar_audio()` para pré-processamento.
- Configuração de ações: `4_comandos/config.json` e equivalentes usam uma lista `acoes` com objetos {"nome": "<verbo>", "dispositivo": ["<nomes>"]} — não mude o formato.
- Paths: muitos exemplos são Windows-style; prefira `os.path.join(...)` para novas implementações.

## Dependências e integrações críticas

- Hugging Face transformers / Wav2Vec2 (ex.: `lgris/...`) — modelos são baixados na primeira execução; se a rede for restrita, use os WAVs locais para testes.
- PyAudio — captura em tempo real (no Windows pode exigir binários). Se falhar, use os scripts de transcrição por arquivo em `2_reconhecimento_de_fala/`.
- NLTK stopwords (portuguese) — pipeline de comandos filtra tokens com `nltk.corpus.stopwords.words('portuguese')`.
- Torch device: use `testar_gpu.py` presente em cada módulo para escolher `cuda:0` ou `cpu`.

## Comandos úteis (rápido)

- Instalar dependências: `pip install -r requirements.txt` (execute na raiz do workspace).
- Validar inicialização do modelo: `python 4_comandos/inicializador_modelo.py` ou `python 2_reconhecimento_de_fala/inicializador_modelo.py`.
- Testar transcrição em arquivo: `python 4_comandos/transcritor.py` (usa WAVs em `2_reconhecimento_de_fala/audios/`).
- Rodar assistente local (microfone): `python 4_comandos/assistente.py` — o script chama `testar_gpu()` automaticamente.

## Exemplos práticos a citar ao editar código

- Para transcrever um WAV: usar `carregar_audio(path)` seguido de `transcrever_fala(dispositivo, fala, modelo, processador)` (ver `4_comandos/transcritor.py`).
- Adicionar um atuador: criar `X.py` com função pública que replica a interface de `lampada.py`/`som.py` e atualizar `config.json` com o verbo correspondente.

## Regras para agentes (o que fazer automaticamente)

- Priorizar mudanças pequenas e isoladas (um módulo por PR). Mantenha compatibilidade da assinatura `iniciar_modelo`.
- Substituir hard-coded paths por `os.path.join` quando seguro.
- Prefer testes locais com WAVs em `2_reconhecimento_de_fala/audios/` antes de acionar downloads de modelos ou hardware.

## Onde olhar para exemplos e testes

- `assistente_virtual_professor/testes.py` e `assistente_virtual_infra/testes.py` — casos de referência e scripts de validação.
- `4_comandos/assistente.py` — loop principal e integração com atuadores.

## Observação — novos diretórios adicionados

Foram adicionados recentemente os diretórios `assistente_virtual_professor/`, `assistente_virtual_infra/` e `6_Chatterbots/`.

- `assistente_virtual_professor/`: versão usada como prova/trabalho do assistente virtual (exemplos de atuadores e áudios de teste).
- `assistente_virtual_infra/`: scripts e utilitários focados em infraestrutura e integração.
- `6_Chatterbots/`: experimentos iniciais de chatbots (treinamento e conversas).

Inclua estes caminhos quando procurar por exemplos de integração, atuadores e testes locais.

---

Se quiser, posso: (1) converter paths para cross-platform em todo o projeto, (2) adicionar testes unitários mínimos para `transcritor.py`, ou (3) gerar um README de execução por pasta. Qual prefere?
```

- Preferir mudanças pequenas e isoladas: alterar apenas um `iniciar_modelo` ou `transcrever_fala` por PR.
