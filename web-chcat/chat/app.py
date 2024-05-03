from typing import Tuple, Union
from flask import Response,Flask, render_template, request, jsonify
from flask_cors import CORS
from llamaapi import LlamaAPI
import logging
import funciones



app = Flask(__name__)
CORS(app)
llama = LlamaAPI("LL-UHp8T1ChDqZdLKMDXPlgWyKaGkzQ8Y32zc55lmE6ZwF62lko1TeRmQVxFKw6LgKS")
logging.basicConfig(level=logging.INFO)

# Context variables
nombre_paciente = "Juanito"
problema = "Demencia senil"
relacion_cuidador = "hija"
nombre_cuidador = "Maria"
initial_context = """
Después de este mensaje ya, quiero que interactúes en base al siguiente contexto:
Eres una IA centrada en el cuidado de personas mayores o con algún tipo de problema cognitivo, por 
lo que tienes que hablar en un tono familiar . En caso de que detectes una situación en la
que consideres necesario llamar a los servicios de emergencia, solo di 'ALERTA'. 
Dentro de este contexto, tienes que meterte en el siguiente papel: El paciente se llama {0} sufre de {1},
y tú eres su {2} llamado {3}.
""".format(nombre_paciente, problema, relacion_cuidador, nombre_cuidador)
dynamic_context = initial_context

@app.route('/')
def index():
    return render_template('webchat/index.html')


@app.route('/upload_audio', methods=['POST'])
def upload_audio() -> Union[Response, Tuple[Response, int]]:
    global dynamic_context  # Asegúrate de referenciar la variable global
    logging.info("Request received with files: %s and form data: %s", request.files, request.form)
    
    if 'audio' not in request.files:
        logging.error("No valid audio file provided or file format not supported.")
        return jsonify({'error': 'No valid audio file provided or file format not supported'}), 400

    audio_file = request.files['audio']
    page_load_count = request.form.get('pageLoadCount', 'default_session')  # Extraer el contador de carga de página del formulario

    original_path, converted_path = funciones.save_and_convert_audio(audio_file)
    if original_path is None or converted_path is None:
        return jsonify({'error': 'Failed to convert the audio'}), 500

    text, error_details = funciones.transcribe_audio(converted_path)
    if text is None:
        return jsonify(error_details), error_details.get('status', 500) if error_details else jsonify({'error': 'Error processing audio'}), 500

    result, status = funciones.process_recognition(text, dynamic_context, llama, page_load_count)
    if status == 200:
        dynamic_context = result['updated_context']  # Actualizar el contexto dinámico global
        return jsonify(result['response']), 200
    else:
        return jsonify(result['response']), result.get('status_code', 500)




if __name__ == '__main__':
    app.run(debug=True)
