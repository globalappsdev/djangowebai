# chatbot/utils.py
import json
import google.generativeai as genai
import requests
from django.conf import settings

USER_HISTORIES = {}
USER_AGENT_CHATS = {}
ACTIVE_CHATS = {}

BUSINESS_JSON = {...}  # Same as in Flask version

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    return response.status_code == 200

def sendtoAi(prompt, history=None):
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    history = history or []
    business_json_str = json.dumps(BUSINESS_JSON)
    history_str = json.dumps(history) if history else "[]"
    
    full_prompt = (
        f"Business Context: {business_json_str}\n"
        f"Conversation History: {history_str}\n"
        f"User Query: \"{prompt}\"\n"
        "Instructions: Respond to the user's query using the provided business context and history."
    )
    
    response = model.generate_content(full_prompt)
    return response.text