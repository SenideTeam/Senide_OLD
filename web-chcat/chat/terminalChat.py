import pyaudio
import numpy as np
import speech_recognition as sr
from llamaapi import LlamaAPI
import pyttsx3
from guardar_respuesta import guardar_conversacion

# Configuración de PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5  # Duración de la grabación después de detectar habla

# Crear objeto PyAudio
audio = pyaudio.PyAudio()

# Abrir el flujo de entrada de audio desde el micrófono
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

# Crear una instancia de LlamaAPI
llama = LlamaAPI("LL-UHp8T1ChDqZdLKMDXPlgWyKaGkzQ8Y32zc55lmE6ZwF62lko1TeRmQVxFKw6LgKS")

# Crear un objeto de pyttsx3 para la síntesis de voz
engine = pyttsx3.init()

print("Escuchando...")

frames = []  # Lista para almacenar frames de audio

# Bucle principal
while True:
    data = stream.read(CHUNK)
    audio_data = np.frombuffer(data, dtype=np.int16)
    amplitude = np.mean(np.abs(audio_data))

    # Detectar habla y grabar audio
    if amplitude > 350:
        print("Hablando...")
        frames.append(data)
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        # Detener la grabación y procesar el audio
        print("Fin de la grabación.")
        stream.stop_stream()

        # Crear un objeto recognizer y audio source
        recognizer = sr.Recognizer()
        audio_source = sr.AudioData(b''.join(frames), RATE, 2)

        # Usar Google Web Speech API para reconocer el audio
        try:
            text = recognizer.recognize_google(audio_source, language='es-ES')
            print("Texto transcrito: " + text)

            # Preparar el JSON para la API de Llama
            api_request_json = {
                "messages": [
                    {"role": "user", "content": text},
                ]
            }
            
            # Llamar a la API de Llama y obtener la respuesta
            response = llama.run(api_request_json)
            assistant_response = response.json()['choices'][0]['message']['content']
            print("Llama: " + assistant_response)
            
            # Guarda la respuesta
            guardar_conversacion(text,assistant_response)
            
            # Convertir la respuesta en audio y reproducirla
            engine.say(assistant_response)
            engine.runAndWait()

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

        # Reiniciar la grabación
        stream.start_stream()
        frames = []  # Limpiar los frames para la próxima grabación
    else:
        print("Silencio...")
