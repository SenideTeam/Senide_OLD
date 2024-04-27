from flask import Flask, render_template, request, jsonify
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
def upload_audio():
    global dynamic_context  # Make sure to reference the global variable
    logging.info("Request received with files: %s", request.files)
    if 'audio' not in request.files:
        logging.error("No valid audio file provided or file format not supported.")
        return jsonify({'error': 'No valid audio file provided or file format not supported'}), 400

    audio_file = request.files['audio']
    # Modifica esta línea para usar el prefijo del módulo
    original_path, converted_path = funciones.save_and_convert_audio(audio_file)

    if original_path is None or converted_path is None:
        return jsonify({'error': 'Failed to convert the audio'}), 500

    # Modifica esta línea para usar el prefijo del módulo
    text, error_details = funciones.transcribe_audio(converted_path)
    if text is None:
        return jsonify(error_details), error_details['status']

    # Modifica esta línea para usar el prefijo del módulo
    result, status = funciones.process_recognition(text, dynamic_context, llama)
    if status == 200:
        dynamic_context = result['updated_context']  # Update the global dynamic context
        return jsonify(result['response']), status
    else:
        return jsonify(result['response']), result['status_code']



if __name__ == '__main__':
    app.run(debug=True)
