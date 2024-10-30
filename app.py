from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import openai
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client and assistant/thread details
openai_api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key=openai_api_key)
assistant_id = "asst_LpgGqNaMQGdwz5Cjrk7q52Nn"
thread_id = "thread_1fVhNglC0T9n3rKj2wdcRfZ5"

@app.route("/")
def home():
    # Render the HTML file in the templates folder
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    user_input = request.json.get("content")
    response = send_message(user_input)
    return jsonify({"response": response})

# Function to handle sending messages to the assistant
def send_message(content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user as Jane Doe. The user has a premium account."
    )
    if run.status == 'completed':
        message_resp = client.beta.threads.messages.list(thread_id=thread_id)
        messages = message_resp.data if hasattr(message_resp, 'data') else []
        assistant_responses = [
            content_block.text.value
            for message in messages
            if hasattr(message, 'role') and message.role == 'assistant'
            for content_block in message.content
            if hasattr(content_block, 'text') and hasattr(content_block.text, 'value')
        ]
        return assistant_responses[0] if assistant_responses else "No response."
    return "Error: The request did not complete."

if __name__ == "__main__":
    app.run(debug=True)
