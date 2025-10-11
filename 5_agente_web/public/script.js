const recordButton = document.getElementById('recordButton');
const statusDisplay = document.getElementById('status');
const transcriptionDisplay = document.getElementById('transcription');
let mediaRecorder;
let audioChunks = [];

recordButton.addEventListener('click', async () => {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        // Inicia a gravação
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            // Converte os dados de áudio em um Blob e envia para o backend
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio', audioBlob);

            statusDisplay.textContent = 'Processando...';

            // Envia o áudio para o backend Flask
            try {
                const response = await fetch('reconhecer_comando', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                transcriptionDisplay.textContent = result.transcription || "Erro ao processar a transcrição";
            } catch (error) {
                transcriptionDisplay.textContent = "Erro na comunicação com o servidor.";
                console.error("Erro:", error);
            }

            audioChunks = [];
            statusDisplay.textContent = 'Parado';
        };

        mediaRecorder.start();
        statusDisplay.textContent = 'Gravando...';
        recordButton.textContent = 'Parar Gravação';
    } else {
        // Para a gravação
        mediaRecorder.stop();
        recordButton.textContent = 'Iniciar Gravação';
    }
});
