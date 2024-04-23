import os
from flask import Flask, render_template, request
from openai import OpenAI
from llamaapi import LlamaAPI # type: ignore
import speech_recognition as sr
import time



llama = LlamaAPI("LL-UHp8T1ChDqZdLKMDXPlgWyKaGkzQ8Y32zc55lmE6ZwF62lko1TeRmQVxFKw6LgKS")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('webchat/index.html')

@app.route('/store', methods=['POST']) 
def storage():
    recognizer = sr.Recognizer()
    
    
    
    user_input = request.form['txtMensaje']
    
    api_request_json = {
        "messages": [
            {"role": "user", "content": user_input},
        ]
    }
    
    
    response = llama.run(api_request_json)
    
    
    assistant_response = response.json()['choices'][0]['message']['content']
    print("Llama: " + assistant_response)
    return render_template('webchat/index.html')

if __name__ == '__main__':
    app.run(debug=True)
