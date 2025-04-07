from app.models.user import chat_collection
from app.models.user import Chat

async def send_to_gemini(prompt: str, user_email: str) -> str:
    # Dummy response for now
    response = f"Echo: {prompt}"

    chat = Chat(user_email=user_email, prompt=prompt, response=response)
    await chat_collection.insert_one(chat.dict())

    return response
