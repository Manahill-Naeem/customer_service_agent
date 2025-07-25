import chainlit as cl
from agents import function_tool
import requests
import os

@function_tool
def send_whatsapp_message(number: str, message: str) -> str:
    """
    Uses the UltraMSG API to send a custom WhatsApp message to the specified phone number.
    Returns a success message if sent successfully, or an error message if the request fails.
    """

    instance_id = os.getenv("INSTANCE_ID")
    token = os.getenv("API_TOKEN")

    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    
    payload = {
        "token": token,
        "to": number,
        "body": message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        return f"📤 Message sent successfully to {number}"
    else:
        return f"❌ Failed to send message. Error: {response.text}"
