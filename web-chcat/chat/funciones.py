import subprocess
import os
from datetime import datetime
import speech_recognition as sr
import logging
from typing import Tuple, Optional, Dict, Any
import requests


def guardar(pregunta: str, respuesta: str, session_id: str) -> None:
    """
    Guarda la 'pregunta' y la 'respuesta' en un archivo de texto en un directorio específico.
    Utiliza el 'session_id' para agrupar las conversaciones relacionadas.
    """
    directorio_actual = os.path.dirname(__file__)
    directorio = "respuestas_asistente"
    ruta_directorio = os.path.join(directorio_actual, directorio)

    if not os.path.exists(ruta_directorio):
        os.makedirs(ruta_directorio)

    nombre_archivo = f"conversacion_{session_id}.txt"  # Usar session_id en el nombre del archivo
    ruta_archivo = os.path.join(ruta_directorio, nombre_archivo)

    with open(ruta_archivo, "a", encoding="utf-8") as file:
        file.write(f"Pregunta: {pregunta}\nRespuesta: {respuesta}\n\n")

def save_and_convert_audio(audio_file) -> Tuple[Optional[str], Optional[str]]:
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
        return None, None
    return original_path, converted_path

def transcribe_audio(converted_path: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    with sr.AudioFile(converted_path) as source:
        recognizer = sr.Recognizer()
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='es-ES') # type: ignore
            return text, None
        except sr.UnknownValueError:
            return None, {'error': 'Could not understand audio', 'details': 'No speech could be recognized', 'status': 422}
        except sr.RequestError as e:
            return None, {'error': 'Speech recognition service error', 'details': str(e), 'status': 503}

def process_recognition(text: str, dynamic_context: str, llama, session_id: str, original_path: str, converted_path: str) -> Tuple[Dict[str, Any], int]:
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
        updated_context += f"\n\nRespuesta de Llama: {assistant_response}"
        
        guardar(text, assistant_response, session_id)

        try:
            os.remove(original_path)
            os.remove(converted_path)
            logging.info("Audio files deleted successfully.")
        except Exception as e:
            logging.error(f"Error deleting audio files: {str(e)}")

        return {'response': {'text': text, 'llama_response': assistant_response}, 'updated_context': updated_context}, 200
    else:
        logging.error("LlamaAPI error: %s", response.text)
        return {'response': {'error': 'LlamaAPI error', 'details': response.text}}, response.status_code


def synthesize_text_with_elevenlabs(text: str, voice_id: str, xi_api_key: str) -> Tuple[Optional[bytes], Optional[Dict[str, Any]]]:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": xi_api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # Asumiendo que este es el modelo que quieres usar
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        if response.status_code == 200:
            audio_content = b''.join(chunk for chunk in response.iter_content(1024))
            return audio_content, None
        else:
            logging.error(f"Fallo al sintetizar voz: {response.text}")
            return None, {'error': 'Fallo al sintetizar voz', 'detalles': response.text, 'estado': response.status_code}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de red al contactar a ElevenLabs: {str(e)}")
        return None, {'error': 'Fallo al realizar solicitud a ElevenLabs', 'detalles': str(e), 'estado': 500}

