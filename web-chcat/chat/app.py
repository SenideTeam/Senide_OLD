from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import subprocess
import os
from datetime import datetime
from flask_cors import CORS
from llamaapi import LlamaAPI

app = Flask(__name__)
CORS(app)
llama = LlamaAPI("LL-UHp8T1ChDqZdLKMDXPlgWyKaGkzQ8Y32zc55lmE6ZwF62lko1TeRmQVxFKw6LgKS")

@app.route('/')
def index():
    return render_template('webchat/index.html')

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    print("Request received with files:", request.files)
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
        print("Original audio file saved at:", original_path)

        result = subprocess.run(['ffmpeg', '-i', original_path, '-ar', '16000', '-ac', '1', converted_path], capture_output=True, text=True)

        if result.returncode != 0 or not os.path.exists(converted_path):
            return jsonify({'error': 'Failed to convert the audio'}), 500

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
                assistant_response = response.json()['choices'][0]['message']['content']
                return jsonify({'text': text, 'llama_response': assistant_response}), 200
            except sr.UnknownValueError:
                return jsonify({'error': 'Could not understand audio'}), 422
            except sr.RequestError as e:
                return jsonify({'error': str(e)}), 503
    else:
        return jsonify({'error': 'No audio file provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
