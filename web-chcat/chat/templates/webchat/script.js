let mediaRecorder;
let audioChunks = [];
let audioContext;
let audioInput;
let realTimeAnalyser;
let isRecording = false;
let lastTimeAboveThreshold = Date.now();
const silenceThreshold = 0.1; // Umbral de silencio
const silenceTime = 1500; // Tiempo en ms para considerar que el silencio significa fin de habla
let isSpeaking = false; // Estado de la reproducción de voz

document.getElementById('recordButton').addEventListener('click', () => {
    const recordButton = document.getElementById('recordButton');
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        if (!audioContext) {
            audioContext = new AudioContext();
            audioInput = audioContext.createMediaStreamSource(stream);
            realTimeAnalyser = audioContext.createAnalyser();
            realTimeAnalyser.fftSize = 512;
            audioInput.connect(realTimeAnalyser);
            console.log('Configuración completa del contexto de audio y analizador');
        }

        checkAudio();

        if (!mediaRecorder) {
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
            } else {
                console.error('Formato audio/webm;codecs=opus no soportado');
                return;
            }
            mediaRecorder.ondataavailable = e => {
                if (e.data.size > 0 && isRecording) {
                    console.log('Datos de grabación:', e.data.size);
                    audioChunks.push(e.data);
                }
            };
            mediaRecorder.onstop = () => {
                console.log('Grabación detenida');
                processAudioChunks();
            };
        }
        
        recordButton.textContent = "Monitoreando...";
        recordButton.disabled = true;
        console.log('Monitoreo iniciado');
    }).catch(error => console.error("Error al acceder a los dispositivos multimedia.", error));
});

function checkAudio() {
    if (isSpeaking) return; // No iniciar la grabación si se está hablando
    const bufferLength = realTimeAnalyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    realTimeAnalyser.getByteTimeDomainData(dataArray);
    
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
        const x = (dataArray[i] - 128) / 128.0;
        sum += x * x;
    }
    const rms = Math.sqrt(sum / bufferLength);
    
    if (rms > silenceThreshold && !isSpeaking) {
        lastTimeAboveThreshold = Date.now();
        if (!isRecording) {
            isRecording = true;
            audioChunks = [];
            mediaRecorder.start(1000);  // Iniciar grabación con timeslice
            console.log('Umbral superado, comenzando la grabación');
        }
    } else if (isRecording && (Date.now() - lastTimeAboveThreshold > silenceTime)) {
        isRecording = false;
        mediaRecorder.stop();
        console.log('Silencio detectado, grabación detenida');
    }
    
    requestAnimationFrame(checkAudio);
}

function processAudioChunks() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    console.log('Procesando trozos de audio, tamaño del blob:', audioBlob.size);
    if (audioBlob.size > 0) {
        sendAudioToServer(audioBlob);
    } else {
        console.error('No hay datos para enviar.');
    }
}

function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'filename.webm');
    console.log('Enviando audio al servidor');

    fetch('/upload_audio', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del servidor recibida:", data);
        if (data.llama_response) {
            speak(data.llama_response);
        }
    })
    .catch(error => console.error('Error al subir el audio:', error));
}

function speak(text) {
    if (!window.speechSynthesis) {
        console.log('Text-to-speech not supported.');
        return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onstart = () => { isSpeaking = true; };
    utterance.onend = () => { isSpeaking = false; checkAudio(); }; // Reanudar la comprobación del audio al finalizar la voz
    utterance.voice = speechSynthesis.getVoices().find(voice => voice.lang === 'es-ES' || voice.lang.startsWith('es'));
    speechSynthesis.speak(utterance);
}
