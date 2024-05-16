from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
from llamaapi import LlamaAPI
import logging
import funciones
from typing import Tuple, Union  # Asegúrate de incluir Union aquí

app = Flask(__name__)
CORS(app)
llama = LlamaAPI("LL-UHp8T1ChDqZdLKMDXPlgWyKaGkzQ8Y32zc55lmE6ZwF62lko1TeRmQVxFKw6LgKS")
logging.basicConfig(level=logging.INFO)

# Variables de contexto
nombre_paciente = "Juanito"
problema = "Demencia senil"
relacion_cuidador = "hija"
nombre_cuidador = "Maria"
initial_context = f"""
Después de este mensaje ya, quiero que interactúes en base al siguiente contexto:
Eres una IA centrada en el cuidado de personas mayores o con algún tipo de problema cognitivo, por 
lo que tienes que hablar en un tono familiar. En caso de que detectes una situación en la
que consideres necesario llamar a los servicios de emergencia, solo di 'ALERTA'. 
Dentro de este contexto, tienes que meterte en el siguiente papel: El paciente se llama {nombre_paciente} sufre de {problema},
y tú eres su {relacion_cuidador} llamado {nombre_cuidador}.
"""
dynamic_context = initial_context

# Claves API y ID de voz directamente en el código (no recomendado para producción)
XI_API_KEY = "2862eb12cfab205544b5096b0ccd560d"
DEFAULT_VOICE_ID = "ybbAXNxCgFpnKP8ym62L" # VoiceID default

@app.route('/')
def index():
    return render_template('webchat/index.html')

@app.route('/upload_audio', methods=['GET','POST'])
def upload_audio() -> Union[Response, Tuple[Response, int]]:
    global dynamic_context 
    logging.info("Request received with files: %s", request.files)
    
    if 'audio' not in request.files:
        logging.error("No valid audio file provided or file format not supported.")
        return jsonify({'error': 'No valid audio file provided or file format not supported'}), 400

    audio_file = request.files['audio']
    original_path, converted_path = funciones.save_and_convert_audio(audio_file)
    if original_path is None or converted_path is None:
        logging.error("Failed to convert the audio.")
        return jsonify({'error': 'Failed to convert the audio'}), 500

    text, error_details = funciones.transcribe_audio(converted_path)
    if text is None:
        logging.error(f"Transcription failed: {error_details}")
        return jsonify(error_details), 500

    result, status = funciones.process_recognition(text, dynamic_context, llama, "your_session_id_here", original_path, converted_path)
    if status != 200:
        logging.error(f"Processing recognition failed: {result}")
        return jsonify(result['response']), result.get('status_code', 500)

    dynamic_context = result['updated_context']

    # Leer el get con el id del usuario
    uid = request.args.get('uid', default='', type=str)
    VOICE_ID = DEFAULT_VOICE_ID
    if uid == "1":  # Gerson
        VOICE_ID = ""
    elif uid == "2":  # Aritz
        VOICE_ID = "u2IPBngGM3irIDqHwwt9"
    elif uid == "3":  # Gorka
        VOICE_ID = "4r2FcmxcEjuesUkkRSgw"
    elif uid == "4":  # Telle
        VOICE_ID = "griU9LMQClYI5aeSjdKp"

    synthesized_audio, error = funciones.synthesize_text_with_elevenlabs(result['response']['llama_response'], VOICE_ID, XI_API_KEY)
    if synthesized_audio:
        return Response(synthesized_audio, mimetype='audio/mp3')
    else:
        logging.error(f"Failed to synthesize speech: {error}")
        return jsonify(error), 500

if __name__ == '__main__':
    app.run(debug=True)
