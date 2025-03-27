# chatbot/utils.py
import json
import google.generativeai as genai
import requests
from django.conf import settings

USER_HISTORIES = {}
USER_AGENT_CHATS = {}
ACTIVE_CHATS = {}

BUSINESS_JSON = {
  "business": {
    "name": "Sunny Shades",
    "description": "Your one-stop shop for premium sunglasses.",
    "contact": {
      "phone": "+1-800-555-1234",
      "support_email": "support@sunnyshades.com",
      "sales_email": "sales@sunnyshades.com"
    },
    "address": {
      "street": "123 Sunshine Ave",
      "city": "Sunnyville",
      "state": "CA",
      "zip": "90210",
      "country": "USA"
    },
    "policies": {
      "return": {
        "timeframe": "30 days",
        "conditions": "Items must be unused, in original packaging, with receipt.",
        "process": "Contact support@sunnyshades.com to initiate a return."
      },
      "refund": {
        "timeframe": "14 days after return approval",
        "conditions": "Refunds issued to original payment method.",
        "exceptions": "Custom orders are non-refundable."
      },
      "warranty": {
        "duration": "1 year",
        "coverage": "Manufacturing defects only."
      }
    },
    "products": [
      {
        "id": "SS001",
        "name": "Ray-Ban Aviator",
        "category": "sports",
        "price": 150.00,
        "description": "Classic aviator style, ideal for sports and outdoor activities.",
        "attributes": {
          "color": "Black",
          "lens_type": "Polarized",
          "material": "Metal"
        },
        "stock": 25
      },
      {
        "id": "SS002",
        "name": "Gucci Round",
        "category": "fashion",
        "price": 300.00,
        "description": "Trendy round frames for a stylish look.",
        "attributes": {
          "color": "Gold",
          "lens_type": "Tinted",
          "material": "Acetate"
        },
        "stock": 15
      },
      {
        "id": "SS003",
        "name": "Polaroid Classic",
        "category": "budget",
        "price": 50.00,
        "description": "Affordable and reliable everyday sunglasses.",
        "attributes": {
          "color": "Matte Black",
          "lens_type": "UV Protection",
          "material": "Plastic"
        },
        "stock": 50
      }
    ],
    "services": {
      "appointments": {
        "description": "In-store try-ons or consultations.",
        "availability": "Monday-Friday, 10:00 AM - 6:00 PM PST",
        "booking_process": "Provide preferred date and time; confirmation sent via email."
      },
      "support": {
        "description": "Assistance with orders, returns, or repairs.",
        "contact": "support@sunnyshades.com",
        "response_time": "Within 24 hours"
      }
    }
  }
}  # Same as in Flask version

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
