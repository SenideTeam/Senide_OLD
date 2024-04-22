from flask import Flask
from flask import render_template,request
import requests


app= Flask(__name__)

@app.route("/")
def index():
    return render_template('/chat/index.html')


@app.route('/store', methods=['POST'])
def storage():
    __mensage=request.form['textUser']
    pass


if __name__== '__main__':
    app.run(debug=True)
