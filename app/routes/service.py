from fastapi import APIRouter, HTTPException, Request
from app.services.agent_service import process_user_query
from app.models.user import chat_collection
from bson import ObjectId
router = APIRouter(prefix="/gemini", tags=["Gemini"])

@router.post("/ask")
async def ask_gemini(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")

    user_email = request.state.user.get("sub")
    response = await process_user_query(prompt, user_email=user_email)
    return {"response": response}


@router.get("/history")
async def get_chat_history(request: Request):
    user_email = request.state.user.get("sub")
    chats_cursor = chat_collection.find({"user_email": user_email})
    chats = []
    async for chat in chats_cursor:
        chat["_id"] = str(chat["_id"])  # convert ObjectId to str
        chats.append(chat)
    return {"chats": chats}
