from nltk import word_tokenize, corpus
from nltk.corpus import floresta
from nltk.stem import RSLPStemmer

LINGUAGEM = "portuguese"

def iniciar():
    classificacoes, palavras_de_parada = None, None

    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    classificacoes = {}
    for palavra, classificacao in floresta.tagged_words():
        classificacoes[palavra] = classificacao
    
    return classificacoes, palavras_de_parada

def tokenizar(texto):
    tokens = word_tokenize(texto, language=LINGUAGEM)
    
    return tokens

def eliminar_palavras_de_parada(tokens, palavras_de_parada):
    tokens_filtrados = []

    for token in tokens:
        if token not in palavras_de_parada:
            tokens_filtrados.append(token)

    return tokens_filtrados

def estemizar(tokens):
    stemizador = RSLPStemmer()
    tokens_estemizados = {}

    for token in tokens:
        tokens_estemizados[token] = stemizador.stem(token)

    return tokens_estemizados

def classificar_tokens(tokens, classificacoes):
    tokens_classificados = {}

    for token in tokens:
        if token in classificacoes.keys():
            classificacao = classificacoes[token]
            tokens_classificados[token] = classificacao
        else:
            tokens_classificados[token] = "sem classificação"

    return tokens_classificados

if __name__ == "__main__":
    texto = "a verdadeira generosidade para com o futuro consiste em dar tudo ao presente e para o beta sobra nada, só o osso." # albert camus

    classificacoes, palavras_de_parada = iniciar()
    
    tokens = tokenizar(texto)
    print(tokens)

    tokens = eliminar_palavras_de_parada(tokens, palavras_de_parada)
    print(tokens)

    tokens_classificados = classificar_tokens(tokens, classificacoes)
    print(tokens_classificados)

    tokens_estemizados = estemizar(tokens)
    print(tokens_estemizados)