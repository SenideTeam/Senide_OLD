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

def allowed_file(filename):
    """ Check if the file is in allowed format """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'webm'}

@app.route('/')
def index():
    return render_template('webchat/index.html')

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    logging.info("Request received with files: %s", request.files)
    if 'audio' in request.files and allowed_file(request.files['audio'].filename):
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
                api_request_json = {
                    "messages": [
                        {"role": "user", "content": text},
                    ]
                }
                response = llama.run(api_request_json)
                if response.status_code == 200:
                    assistant_response = response.json()['choices'][0]['message']['content']
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
