from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os
import redis
from dotenv import load_dotenv
import google.generativeai as genai
from asgiref.sync import sync_to_async


load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


r = redis.Redis(host='localhost', port=6379, db=0)
REDIS_EXPIRY = 3600  # 1 hour

@sync_to_async
def generate_content(context_key, user_message):
    old_context = r.get(context_key)
    previous = old_context.decode() if old_context else ""

    
    prompt = f"{previous}\nUser: {user_message}\nAI:"

    
    response = model.generate_content(prompt)
    reply = response.text.strip()

    # Save new context in Redis
    updated_context = f"{previous}\nUser: {user_message}\nAI: {reply}"
    r.setex(context_key, REDIS_EXPIRY, updated_context)

    return reply

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["client"][1] 
        self.redis_key = f"chat:{self.user_id}"
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        reply = await generate_content(self.redis_key, message)
        await self.send(text_data=json.dumps(
            {
                'message': f"Chatbot: {reply}"
            }
        ))

    async def disconnect(self, close_code):
        pass
