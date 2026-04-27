from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from services.chatbot_service import ChatbotService
from services.llm_service import LLMService

router = APIRouter(tags=["Chatbot"])


@router.post("/")
async def chat(request: Request, db: Session = Depends(get_db)):

    data = await request.json()
    message = data.get("message")
    user_id = data.get("user_id")

    if not message:
        return {"error": "No message"}

    result = ChatbotService.handle_chat(db, user_id, message)

    print("CHATBOT RESULT:", result)

    return result
    

# LLM PART
@router.post("/intent")
async def intent(request: Request):

    data = await request.json()
    message = data.get("message")

    if not message:
        return {"error": "No message"}

    intent_data = LLMService.extract_intent(message)

    return intent_data