import time
import random
import os

def iniciar_infra():
    """Inicializa recursos do atuador de infraestrutura (simulados).
    Sempre retorna True — em integrações reais aqui iria autenticação/cliente SSH/APIs.
    """
    return True


def atuar_sobre_infra(acao, dispositivo):
    texto_alvo = dispositivo.lower() if isinstance(dispositivo, str) else str(dispositivo)

    if acao == "verificar":
        _simular_verificar_status(texto_alvo)
    elif acao == "reiniciar":
        _simular_reiniciar_servico(texto_alvo)
    elif acao == "backup":
        _simular_backup_aplicacao(texto_alvo)
    elif acao == "analisar":
        _simular_analisar_logs(texto_alvo)
    elif acao == "consultar":
        _simular_consultar_recursos(texto_alvo)
    else:
        print(f"Ação '{acao}' não suportada pelo atuador de infra")


def _simular_verificar_status(alvo):
    print(f"[infra] checando status de: {alvo} ...")
    time.sleep(1)
    status = random.choice(["online", "offline"])
    print(f"[infra] resultado: {alvo} está {status}")


def _simular_reiniciar_servico(alvo):
    print(f"[infra] enviando comando de reinício para: {alvo}")
    for i in range(3):
        print(f"[infra] reiniciando... etapa {i+1}/3")
        time.sleep(0.8)
    print(f"[infra] {alvo} reiniciado (simulado)")


def _simular_backup_aplicacao(alvo):
    print(f"[infra] iniciando rotina de backup para: {alvo}")
    total = 5
    for i in range(total):
        time.sleep(0.6)
        progresso = int((i + 1) / total * 100)
        print(f"[infra] backup em progresso: {progresso}%")
    print(f"[infra] backup concluído para {alvo}")


def _simular_analisar_logs(alvo):
    print(f"[infra] analisando logs das últimas 24h para: {alvo}")

    # tenta ler um arquivo de log padrão se existir no diretório 'audios' ou raiz
    possiveis = [
        os.path.join(os.path.dirname(__file__), "audios", "system.log"),
        os.path.join(os.path.dirname(__file__), "system.log")
    ]

    encontrado = None
    for p in possiveis:
        if os.path.exists(p):
            encontrado = p
            break

    erros = []
    if encontrado:
        with open(encontrado, "r", encoding="utf-8", errors="ignore") as f:
            linhas = f.readlines()[-1000:]
            for linha in linhas:
                if any(x in linha.lower() for x in ["error", "exception", "critical", "fatal"]):
                    erros.append(linha.strip())

    # se não encontrou arquivo, gera resultados simulados
    if not encontrado:
        possiveis_erros = [
            "Failed to connect to database: timeout",
            "NullPointerException in com.app.Main at line 123",
            "CRITICAL: disk /dev/sda1 near capacity",
            "Fatal: kernel OOM killer invoked"
        ]
        erros = random.sample(possiveis_erros, k=random.randint(0, len(possiveis_erros)))

    if erros:
        print(f"[infra] erros críticos encontrados ({len(erros)}):")
        for e in erros[:10]:
            print(f"  - {e}")
    else:
        print("[infra] nenhum erro crítico detectado nas últimas 24h (simulado)")


def _simular_consultar_recursos(alvo):
    """Simula consulta de recursos (CPU/memória) retornando valores randômicos.
    Gera números distintos a cada chamada para evitar respostas repetitivas.
    """
    cpu = round(random.uniform(1, 95), 1)
    memoria = round(random.uniform(5, 92), 1)
    # adicional: gerar porcentagem de swap/disco ou IO se o 'alvo' sugerir
    extra = None
    if "cpu" in alvo or "cpg" in alvo:
        extra = f"CPU: {cpu}%"
    elif "mem" in alvo or "memoria" in alvo or "memória" in alvo:
        extra = f"Memória: {memoria}%"
    else:
        extra = f"CPU: {cpu}% | Memória: {memoria}%"

    print(f"[infra] uso simulado — {extra}")
