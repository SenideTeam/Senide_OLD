import os
from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('webchat/index.html')

@app.route('/store', methods=['POST']) 
def storage():
    __mensaje = request.form['txtMensaje']
    
    #client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    client = OpenAI(api_key="sk-proj-oxeV4wnhzXFDRuqGJ8QqT3BlbkFJHlZG2iFGl0EWXVNXLDUL")

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
            ]
        )

        # Asegúrate de que 'completion' tiene una respuesta y accede a ella correctamente
        if completion.choices:
            respuesta = completion.choices[0].message.content
            print(respuesta)
        else:
            respuesta = "No response received."
    except Exception as e:
        print(f"Error al obtener la respuesta de OpenAI: {e}")
        respuesta = "Error al procesar la solicitud."

    print(__mensaje)
    return render_template('webchat/index.html', respuesta=respuesta)

if __name__ == '__main__':
    app.run(debug=True)
