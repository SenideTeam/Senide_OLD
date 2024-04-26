from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import subprocess
import os
from datetime import datetime
from flask_cors import CORS
from llamaapi import LlamaAPI
import logging

app = Flask(__name__)
CORS(app)
llama = LlamaAPI("LL-UHp8T1ChDqZdLKMDXPlgWyKaGkzQ8Y32zc55lmE6ZwF62lko1TeRmQVxFKw6LgKS")

# Configura el logging
logging.basicConfig(level=logging.INFO)

# Contexto inicial con marcadores para formato
context_initial = """
Después de este mensaje ya, quiero que interactúes en base al siguiente contexto:
Eres una IA centrada en el cuidado de personas mayores o con algún tipo de problema cognitivo, por 
lo que tienes que hablar en un tono familiar y cuidadoso. En caso de que detectes una situación en la
que consideres necesario llamar a los servicios de emergencia, solo di 'ALERTA'. 
Dentro de este contexto, tienes que meterte en el siguiente papel: El paciente se llama {0} sufre de {1},
y tú eres su {2} llamado {3}.
"""

# Variables para personalizar el contexto
nombre_paciente = "Juanito"
problema = "Demencia senil"
relacion_cuidador = "hija"
nombre_cuidador = "Maria"

# Inicializa el contexto con las variables
initial_context = context_initial.format(nombre_paciente, problema, relacion_cuidador, nombre_cuidador)

# Contexto que evoluciona con cada respuesta
dynamic_context = initial_context

@app.route('/')
def index():
    return render_template('webchat/index.html')

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    logging.info("Request received with files: %s", request.files)
    if 'audio' in request.files:
        audio_file = request.files['audio']
        directory = os.path.join(os.path.dirname(__file__), "audio")
        os.makedirs(directory, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = f"original_audio_{timestamp}.webm"
        converted_filename = f"converted_audio_{timestamp}.wav"

        original_path = os.path.join(directory, original_filename)
        converted_path = os.path.join(directory, converted_filename)

        audio_file.save(original_path)
        logging.info("Original audio file saved at: %s", original_path)

        result = subprocess.run(['ffmpeg', '-i', original_path, '-ar', '16000', '-ac', '1', converted_path], capture_output=True, text=True)
        if result.returncode != 0:
            logging.error("FFmpeg error: %s", result.stderr)
            return jsonify({'error': 'Failed to convert the audio', 'ffmpeg_error': result.stderr}), 500

        with sr.AudioFile(converted_path) as source:
            recognizer = sr.Recognizer()
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='es-ES')
                global dynamic_context  # Referencia al contexto global que evoluciona
                updated_context = f"{dynamic_context}\n\nÚltima interacción: {text}"
                api_request_json = {
                    "messages": [
                        {"role": "user", "content": text},
                        {"role": "system", "content": updated_context}
                    ]
                }
                response = llama.run(api_request_json)
                if response.status_code == 200:
                    assistant_response = response.json()['choices'][0]['message']['content']
                    dynamic_context += f"\n\nRespuesta de Llama: {assistant_response}"  # Actualiza el contexto con la respuesta de Llama
                    return jsonify({'text': text, 'llama_response': assistant_response}), 200
                else:
                    logging.error("LlamaAPI error: %s", response.text)
                    return jsonify({'error': 'LlamaAPI error', 'details': response.text}), response.status_code
            except sr.UnknownValueError:
                return jsonify({'error': 'Could not understand audio', 'details': 'No speech could be recognized'}), 422
            except sr.RequestError as e:
                return jsonify({'error': 'Speech recognition service error', 'details': str(e)}), 503
    else:
        logging.error("No valid audio file provided or file format not supported.")
        return jsonify({'error': 'No valid audio file provided or file format not supported'}), 400

if __name__ == '__main__':
    app.run(debug=True)
