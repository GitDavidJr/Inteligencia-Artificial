const recordButton = document.getElementById("recordButton");
const statusDisplay = document.getElementById("status");
const transcriptionDisplay = document.getElementById("transcription");
const assistantNameDisplay = document.getElementById("assistantName");
const modelStatusDisplay = document.getElementById("modelStatus"); // may be null
const actuatorsDisplay = document.getElementById("actuators"); // may be null
const miniLogDisplay = document.getElementById("miniLog");

let recorder;
let audioContext;
let stream;
let isRecording = false;

// helper para obter stream do microfone com detecção de compatibilidade
async function obterStreamMicrofone() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    return await navigator.mediaDevices.getUserMedia({ audio: true });
  }

  const getUserMedia =
    navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia;
  if (getUserMedia) {
    return new Promise((resolve, reject) =>
      getUserMedia.call(navigator, { audio: true }, resolve, reject)
    );
  }

  throw new Error(
    "API getUserMedia não disponível. Abra esta página via http(s) (ou localhost). Evite abrir como file://"
  );
}

recordButton.addEventListener("click", async () => {
  if (!isRecording) {
    try {
      stream = await obterStreamMicrofone();
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContext.createMediaStreamSource(stream);
      recorder = new Recorder(source, { numChannels: 1 });
      recorder.record();

      statusDisplay.textContent = "Gravando...";
      recordButton.textContent = "Parar Gravação";
      isRecording = true;
    } catch (err) {
      console.error("Erro ao acessar microfone:", err);
      statusDisplay.textContent = "Erro ao acessar microfone.";
    }
  } else {
    recorder.stop();
    stream.getTracks().forEach((track) => track.stop());

    statusDisplay.textContent = "Processando...";
    recordButton.textContent = "Iniciar Gravação";
    isRecording = false;

    recorder.exportWAV(async (audioBlob) => {
      const formData = new FormData();
      formData.append("fala", audioBlob, "fala.wav");

      console.log("dentro do export wave");
      try {
        const response = await fetch("reconhecer_comando", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();
        transcriptionDisplay.textContent =
          result.transcricao || "Erro ao processar a transcrição";
        // após executar comando, atualiza status/atuadores
        _atualizar_status();
        // anexa log simples com timestamp (uma linha por entrada)
        try {
          const when = new Date().toLocaleString();
          const msg = `${when} — ${
            result.transcricao || "comando sem transcrição"
          }`;
          if (miniLogDisplay) {
            // pré-pende nova linha (se já existir conteúdo não vazio, separa com uma quebra)
            const existing =
              miniLogDisplay.textContent && miniLogDisplay.textContent.trim()
                ? miniLogDisplay.textContent
                : "";
            miniLogDisplay.textContent =
              msg + (existing ? "\n" + existing : "");
          }
        } catch (e) {
          // ignore
        }
      } catch (error) {
        transcriptionDisplay.textContent =
          "Erro na comunicação com o servidor.";
        console.error("Erro:", error);
      }

      statusDisplay.textContent = "Parado";
    });
  }
});

// busca informações do assistente (status do modelo, atuadores) e atualiza o front
async function _atualizar_status() {
  try {
    const resp = await fetch("status");
    if (!resp.ok) return;
    const data = await resp.json();

    if (assistantNameDisplay)
      assistantNameDisplay.textContent = data.nome_assistente || "Assistente";
    // remove textos extras — manter UI limpa (modelStatus/actuators may be absent)
    if (modelStatusDisplay) modelStatusDisplay.textContent = "";
    if (actuatorsDisplay) actuatorsDisplay.textContent = "";
  } catch (e) {
    console.error("Não foi possível obter status:", e);
  }
}

// inicializa o status ao carregar a página
window.addEventListener("load", () => {
  _atualizar_status();
});
