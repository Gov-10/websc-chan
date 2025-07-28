from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        response = model.generate_content(message)
        reply = response.text.strip()
        await self.send(text_data=json.dumps(
            {
                'message' : f"Chatbot: {reply}"
            }
        ))
    async def disconnect(self, close_code):
        pass
