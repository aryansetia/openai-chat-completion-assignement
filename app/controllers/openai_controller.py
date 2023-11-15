from flask import Blueprint, request, jsonify, current_app, session
from app.models.log_entry import LogEntry 
from app import limiter, openai_api_key, create_app
from openai import OpenAI
import tiktoken
from threading import Thread


# Define the maximum number of tokens, model name etc. to use for the completion
MAX_ALLOWED_TOKENS = 4096
MODEL_NAME = "gpt-3.5-turbo-1106"
BOT_RESPONSE_BUFFER = 500

# Get the encoding for the model    
enc = tiktoken.encoding_for_model(MODEL_NAME)

# Create a blueprint for the API
openai_api = Blueprint('openai_api', __name__)

# Initialize the OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize the session with a system message
def initialize_system_context(): 
    system_context = [
        {"role": "system", "content": "You are a helpful assistant designed to output JSON."}
    ]
    return system_context

# 
def get_token_count(text):
    return len(enc.encode(text))

def calculate_messages_tokens(messages):
    total_tokens = 0
    for message in messages:
        total_tokens += get_token_count(message['content'])
    return total_tokens

def save_log_entry_to_database(app, user_id, prompt, response):
    with app.app_context():
        try:
            # Save the log entry to the database
            log_entry = LogEntry(user_id=user_id, prompt=prompt, response=response)
            log_entry.save()

        except Exception as e:
            # Log the error to the Flask app's logger
            current_app.logger.error(f"Error saving log entry to the database: {str(e)}")


# Gets called before each request to initialize the session
@openai_api.before_request
def before_request():
    # Check if 'messages' is not in session or 'init_done' flag is False, then initialize it
    if 'messages' not in session or not session.get('init_done', False):
        session['messages'] = initialize_system_context()

        user_id = request.get_json().get('user_id')
        previous_conversation = []

        # Get the last 10 log entries for the user if user is not in session but a previous user
        if user_id: 
            log_entries = LogEntry.query.filter_by(user_id=user_id).order_by(LogEntry.timestamp.desc()).limit(10).all()
            for entry in log_entries:   
                user_message = {"role": "user", "content": entry.prompt}
                assisant_message = {"role": "assistant", "content": entry.response}
                previous_conversation.extend([user_message, assisant_message])

            # Append the previous conversation to the session
            session['messages'] += previous_conversation


    session['init_done'] = True  # Set the flag to True after initialization

# Gets called after each request to update the session
@openai_api.after_request
def after_request(response):
    session.modified = True
    return response


@openai_api.route('/openai-completion', methods=['POST'])
@limiter.limit("10/hour")
def openai_completion():
    # Get the JSON data from the request
    data = request.get_json()

    # Check if the JSON data is valid and contains the 'prompt' field
    if not data or 'prompt' not in data or len(data['prompt']) <= 0:
        return jsonify({'error': 'Invalid JSON data or missing "prompt" field or missing "user_id" field'}), 400
    
    if 'user_id' not in data or not isinstance(data['user_id'], int):
        return jsonify({'error': 'Missing or invalid "user_id" field'}), 400
    
    # Get the user ID and prompt from the JSON data
    user_id = data.get('user_id') 
    prompt = data.get('prompt')

    # Append user message to message_history
    session['messages'].append({"role": "user", "content": prompt})

    max_response_tokens = MAX_ALLOWED_TOKENS - calculate_messages_tokens(session['messages']) - BOT_RESPONSE_BUFFER

    # Remove the oldest message from the session if the max_response_tokens is negative
    while max_response_tokens < 0 and len(session['messages']) > 1:

        # Pop the oldest message
        oldest_message_tokens = get_token_count(session['messages'].pop(1)['content'])
        max_response_tokens += oldest_message_tokens

    # Remove the oldest message from the session
    if len(session['messages']) > 20:
        session['messages'] = session['messages'][:1] + session['messages'][3:]

    try:
        # Call the OpenAI API to generate a response
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            response_format={"type": "json_object"},
            messages=session['messages']
        )

        response = completion.choices[0].message.content

        # Append assistant message to message_history
        session['messages'].append({"role": "assistant", "content": response})

        # Save the log entry to the database in a separate thread
        save_thread = Thread(target=save_log_entry_to_database, args=(current_app._get_current_object(), user_id, prompt, response))
        save_thread.start()

        return jsonify({'response': response}), 200

    except Exception as e:
        # Log the error to the log file
        current_app.logger.error(f"OpenAI API error: {str(e)}")
        return jsonify({'error': 'Internal server error. Please try again later.'}), 500
