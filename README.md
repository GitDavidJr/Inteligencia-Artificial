# 🧠 Inteligência Artificial - Faculdade

Este repositório contém os projetos e estudos desenvolvidos durante a disciplina de Inteligência Artificial da faculdade. O foco principal é o aprendizado de técnicas de IA utilizando Python, com ênfase em Processamento de Linguagem Natural (PLN) e Reconhecimento de Fala.

## 📚 Conteúdo do Repositório

### 1️⃣ Introdução ao PLN (`1_introducao_pln/`)

Estudos iniciais sobre Processamento de Linguagem Natural em português:

- **`pln.py`**: Implementação básica de tokenização, remoção de stopwords e stemming
- **`download.py`**: Script para download dos recursos necessários do NLTK
- Utiliza o corpus Floresta e stopwords em português

### 2️⃣ Reconhecimento de Fala (`2_reconhecimento_de_fala/`)

Implementação de sistema de reconhecimento de fala em português brasileiro:

- **`transcritor.py`**: Transcrição de áudio usando modelo Wav2Vec2 (carrega WAVs, faz pré-processamento, e retorna transcrições em texto).
- **`inicializador_modelo.py`**: Inicialização e configuração do modelo Wav2Vec2; exporta `iniciar_modelo(nome_modelo, dispositivo)` e `MODELOS`.
- **`testar_gpu.py`**: Verifica disponibilidade de GPU e retorna o dispositivo a ser usado (`cuda:0` ou `cpu`).
- **`audios/`**: Amostras de áudio para teste (comandos de voz como ligar/desligar lâmpada).

Esta pasta contém os componentes básicos para carregar um modelo de ASR (Automatic Speech Recognition) e transcrever áudios de teste.

### 3️⃣ Assistente Virtual (`3_assistente_virtual/`)

Nesta pasta você integrou o conteúdo de `2_reconhecimento_de_fala` e montou o começo de um assistente por voz (captura e transcrição em tempo real). Estrutura e propósito dos arquivos:

- **`assistente.py`**: Script principal que realiza:
  - Captura de áudio do microfone (usa `pyaudio`);
  - Salva gravações temporárias em `temp/`;
  - Carrega o modelo e transcreve o áudio em tempo real (usa funções copiadas de `transcritor.py` / `inicializador_modelo.py`);
  - Ponto de partida para ligar a transcrição a um sistema de execução de comandos (a parte de mapear transcrição para ações ainda precisa ser conectada).
- **`inicializador_modelo.py`**: Versão local no diretório do assistente (mesma funcionalidade da pasta 2) para inicializar o processador e o modelo.
- **`transcritor.py`**: Funções para carregar arquivos WAV, normalizar/resample e transcrever utilizando o modelo carregado.
- **`testar_gpu.py`**: Detecta se existe GPU e retorna uma string tipo `cuda:0` ou `cpu` (útil para decidir onde carregar o modelo).
- **`temp/`**: Diretório criado para armazenar arquivos de áudio temporários gravados durante a execução.

Observação: o fluxo atual já realiza captura e transcrição em tempo real; falta apenas implementar o mapeamento das transcrições para execução de comandos (ex.: ligar/desligar lâmpada). Você já tem as bases — falta a camada de intenção/ação.

### 4️⃣ Aula 4 — Comandos e execução (diferenças em relação à Aula 3)

Não repete o conteúdo da Aula 3 — abaixo estão apenas as mudanças/adições desta aula:

- Identificação de comandos: o pipeline agora processa transcrições com `processar_transcricao()` (tokenização + remoção de stopwords) e valida pares verbo+dispositivo via `config.json` (`validar_comando()`).
- Execução de comandos: introduzidos atuadores em `4_comandos/` (`lampada.py`, `som.py`) e a função `atuar(acao, dispositivo, atuadores)` que invoca a ação correta quando um comando é válido.
- Uso de threads: a execução dos atuadores é feita em background com `threading.Thread` para não bloquear o loop principal (ver `assistente.py` — `Thread(target=..., args=(...)).start()`).
- Arquivos afetados principais: `4_comandos/assistente.py`, `4_comandos/config.json`, `4_comandos/lampada.py`, `4_comandos/som.py`, `4_comandos/transcritor.py` (resample/transcrição) e `4_comandos/inicializador_modelo.py`.

Nota: grande parte da lógica de captura e transcrição permanece igual à Aula 3; a Aula 4 foca em como transformar a transcrição em ações seguras e não-bloqueantes.

### Assistentes auxiliares e versões do trabalho

Além da versão principal em `3_assistente_virtual/`, este repositório contém duas variações/implementações auxiliares do assistente, usadas como provas/trabalhos e para demonstração de atuadores:

- `assistente_virtual_professor/` — implementação usada como primeira prova/trabalho da matéria; contém exemplos de atuadores, áudios de teste e interfaces para hardware (ex.: `lampada/`).
- `assistente_virtual_infra/` — variação focada em infraestrutura e scripts de suporte (logs, backups, testes automatizados); útil como referência para integração com serviços e atuadores.

Também foi adicionado um diretório de estudos sobre chatbots. Abaixo está uma seção detalhada seguindo o mesmo padrão das seções anteriores.

### 6️⃣ Chatterbots (`6_Chatterbots/`)

Experimentos iniciais com chatbots e agentes conversacionais. Esta pasta reúne código de protótipo para treinar e executar bots simples baseados em regras e exemplos de conversas.

- Propósito:

  - Prototipar e experimentar técnicas simples de chatbot (p. ex. respostas baseadas em template, conjuntos de intenções ou fluxos de diálogo).
  - Guardar exemplos de conversa usados para testes e para treinar/ajustar modelos leves.

- Arquivos principais:

  - **`robo.py`**: Script do agente/chatbot — implementa a lógica de respostas e interface de execução (modo interativo ou por chamadas de função).
  - **`treinamento.py`**: Script para gerar/executar rotinas de treinamento (pode preparar dados a partir de `conversas/` e treinar um modelo simples ou pipeline experimental).
  - **`conversas/saudacoes.json`**: Exemplos de conversas/treinos armazenados em JSON para uso nos testes e no treinamento.
  - **`requirements.txt`**: Dependências específicas para esta pasta (separadas das dependências globais do projeto).

- Requisito adicional (spaCy):

  - Observação: alguns exemplos/rotinas de NLP experimentais podem usar spaCy. Para rodar localmente esses pipelines, instale o pacote de modelos em inglês com:

    ```powershell
    python -m spacy download en_core_web_sm
    ```

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **PyTorch** - Framework de deep learning
- **Transformers (Hugging Face)** - Modelos pré-treinados
- **NLTK** - Processamento de linguagem natural
- **torchaudio** - Processamento de áudio
- **Flask** - Framework web (para futuros desenvolvimentos)

Adicionalmente, para os experimentos de chatbots presentes em `6_Chatterbots/`:

- **ChatterBot** - Biblioteca para criação de chatbots e experimentos de diálogo (utilizada nos protótipos em `6_Chatterbots/`).
- **pytz** - Utilitários de fuso horário; dependência de suporte usada por alguns exemplos e bibliotecas.

## ⚙️ Configuração do Ambiente

### 1. Instalar PyTorch com suporte CUDA (recomendado para GPU):

```bash
pip install torch==2.6.0 torchvision torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
```

### 2. Instalar dependências do projeto:

```bash
pip install -r requirements.txt
```

### 3. Baixar recursos do NLTK (executar uma vez):

```python
python 1_introducao_pln/download.py
```

## 🚀 Como Usar

### Processamento de Linguagem Natural

```python
from 1_introducao_pln.pln import iniciar, tokenizar, eliminar_palavras_de_parada

# Inicializar recursos
classificacoes, palavras_de_parada = iniciar()

# Processar texto
texto = "Este é um exemplo de processamento de linguagem natural"
tokens = tokenizar(texto)
tokens_filtrados = eliminar_palavras_de_parada(tokens, palavras_de_parada)
```

### Reconhecimento de Fala

```python
from 2_reconhecimento_de_fala.transcritor import iniciar_modelo

# Inicializar modelo
iniciado, processador, modelo = iniciar_modelo("lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2")
```

## 📋 Dependências

```
transformers      # Modelos de IA pré-treinados
torchaudio       # Processamento de áudio
PySoundFile      # Leitura de arquivos de áudio
soundfile        # Manipulação de arquivos de som
pyaudio          # Captura de áudio em tempo real
flask            # Framework web
nltk             # Processamento de linguagem natural
```

## 🎯 Status do Projeto

- ✅ **PLN Básico**: Tokenização e remoção de stopwords implementadas
- ✅ **Reconhecimento de Fala**: Modelo Wav2Vec2 configurado
- 🔄 **Em Desenvolvimento**: Integração entre módulos
- 📚 **Estudando**: Continuamente aprendendo novos conceitos de IA

## 📝 Observações

Este é um projeto acadêmico em desenvolvimento. Os códigos representam o processo de aprendizado da disciplina e podem conter implementações básicas que serão refinadas ao longo do curso.

## 🎓 Sobre

Projeto desenvolvido como parte dos estudos em Inteligência Artificial na faculdade. O objetivo é aplicar na prática os conceitos teóricos aprendidos em sala de aula, com foco em:

- Processamento de Linguagem Natural
- Reconhecimento de Fala
- Modelos de Deep Learning
- Aplicações práticas de IA

---

_Repositório em constante atualização conforme o progresso na disciplina._
