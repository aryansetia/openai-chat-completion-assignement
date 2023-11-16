# OpenAI Chat Completion API with Flask

## Overview
This repository contains the source code developed as an assignment for the SDE (AI Team) role at Staple. The project focuses on integrating the OpenAI Chat Completion API with Flask. This integration streamlines the process of sending a POST request to the API, generating a response, and receiving it in return. 

## Tech Stack
The project utilizes the following technologies:

- Flask
- SQLite Database
- OpenAI
- Tiktoken

## Installation 
Ensure you have the required packages installed:

```bash
pip install -r requirements.txt
```

## Usage 
Create a `.env` file in the root directory and setup these 3 environment variables.
```
OPENAI_API_KEY=api_key
SECRET_KEY=secret_key
FLASK_CONFIG=dev
```

Once done, run the application using `python run.py` or `flask run`. App will be live on `http://127.0.0.1:5000/`. 

When making a POST request to the endpoint, the payload should adhere to the following structure: 
- user_id: A non-empty integer representing the user identifier.
- prompt: A non-empty string representing the user's prompt.

```json
{
    "user_id": 1,
    "prompt": "Who won fifa world cup 2018?"
}
```

## cURL request
```bash
curl -X POST -H "Content-Type: application/json" -d "{\"user_id\": 1, \"prompt\": \"Who won fifa world cup 2018?\"}" "http://127.0.0.1:5000/openai-completion"
```

#### Output
```json
{
  "response": "{\n  \"winner\": \"France\",\n  \"runner-up\": \"Croatia\",\n  \"score\": \"4-2\"\n}"
}
```

## Examples 
Request - 1 
```json
{
    "user_id": 2,
    "prompt": "Who is Virat Kohli?"
}
```
Response - 1 
```json
{
    "response": "{\n  \"response\": \"Virat Kohli is a cricketer and former captain of the Indian national cricket team. He is widely regarded as one of the best batsmen in the world and has achieved numerous records and accolades in his cricketing career.\"\n}"
}
```
Request - 2
```json
{
    "user_id": 2,
    "prompt": "What does he do?"
}
```
Response - 2 
```json
{
    "response": "{\n  \"response\": \"Virat Kohli is a professional cricketer who has represented the Indian national cricket team in international matches. He is known for his batting skills and has been a key player in the Indian cricket team for many years.\"\n}"
}
```
Request - 3 (Missing parameters)
```json
{
    "prompt": "Hi, how are you?"
}
```
Response - 3
```json
{
    "error": "Missing or invalid \"user_id\" field"
}
```
Request - 4 (Empty prompt field)
```json
{
    "user_id": 2,
    "prompt": ""
}
```
Response - 4
```json
{
    "error": "Invalid JSON data or missing \"prompt\" field or missing \"user_id\" field"
}
```