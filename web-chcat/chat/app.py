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

@app.route('/')
def index():
    uid = request.args.get('uid', default='', type=str)
    return render_template('webchat/index.html', uid=uid)

@app.route('/upload_audio', methods=['POST'])
def upload_audio() -> Union[Response, Tuple[Response, int]]:
    global dynamic_context 
    logging.info("Request received with files: %s", request.files)
    
    if 'audio' not in request.files:
        logging.error("No valid audio file provided or file format not supported.")
        return jsonify({'error': 'No valid audio file provided or file format not supported'}), 400

    audio_file = request.files['audio']
    page_load_count = request.form.get('pageLoadCount', 'default_session')  

    original_path, converted_path = funciones.save_and_convert_audio(audio_file)
    if original_path is None or converted_path is None:
        return jsonify({'error': 'Failed to convert the audio'}), 500

    text, error_details = funciones.transcribe_audio(converted_path)
    if text is None:
        return jsonify(error_details), 500

    result, status = funciones.process_recognition(text, dynamic_context, llama, page_load_count, original_path, converted_path)
    if status == 200:
        dynamic_context = result['updated_context']  
        return jsonify(result['response']), 200
    else:
        return jsonify(result['response']), result.get('status_code', 500)

if __name__ == '__main__':
    app.run(debug=True)
