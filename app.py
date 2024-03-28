from flask import Flask, render_template, request
from src.chat_app import ChatApp
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    return chat_app.get_chat_response(msg)

if __name__ == '__main__':
    file_path = 'data/stock-data.json'
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    chat_app = ChatApp(json_data)
    app.run()
