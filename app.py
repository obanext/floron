from flask import Flask, request, jsonify, render_template
import openai
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

openai.api_key = os.environ.get('OPENAI_API_KEY')
assistant_id = 'asst_b947fFhr1cjryVyi9KnRmMaP'  # Eén assistant ID

def log_chat_to_google_sheets(user_input, assistant_response, thread_id):
    try:
        url = 'https://script.google.com/macros/s/AKfycbxqMBJMmdgSu-VPvJM9LtKKFpId6KLRLgddrhnNk_yC3RkF0vJMTn4hNhRw4v3a6vGY/exec'
        payload = {
            'thread_id': thread_id,
            'user_input': user_input,
            'assistant_response': assistant_response
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"Failed to log chat: {response.text}")
    except Exception as e:
        print(f"Error logging chat to Google Sheets: {e}")

class CustomEventHandler(openai.AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.response_text = ""

    def on_text_created(self, text) -> None:
        self.response_text = ""

    def on_text_delta(self, delta, snapshot):
        self.response_text += delta.value

def call_assistant(assistant_id, user_input, thread_id=None):
    try:
        if thread_id is None:
            thread = openai.beta.threads.create()
            thread_id = thread.id
        else:
            openai.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_input
            )
        
        event_handler = CustomEventHandler()

        with openai.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()

        return event_handler.response_text, thread_id
    except Exception as e:
        return str(e), thread_id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_thread', methods=['POST'])
def start_thread():
    try:
        thread = openai.beta.threads.create()
        return jsonify({'thread_id': thread.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        data = request.json
        thread_id = data.get('thread_id')
        user_input = data.get('user_input')

        # Stuur naar de assistant
        response_text, thread_id = call_assistant(assistant_id, user_input, thread_id)

        # Log de interactie
        log_chat_to_google_sheets(user_input, response_text, thread_id)

        return jsonify({'response': response_text, 'thread_id': thread_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
