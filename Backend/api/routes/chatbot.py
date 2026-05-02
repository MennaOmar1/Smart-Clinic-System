from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from services.chatbot_service import ChatbotService
from services.llm_service import LLMService
from schemas.chatbot import ChatRequest
router = APIRouter(tags=["Chatbot"])



@router.post("/")
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):

    try:
        message = payload.message
        user_id = payload.user_id

        result = ChatbotService.handle_chat(db, user_id, message)

        return result

    except Exception as e:
        print("CHATBOT ERROR:", str(e))
        return {"error": str(e)}


# LLM PART
@router.post("/intent")
async def intent(request: Request):

    data = await request.json()
    message = data.get("message")

    if not message:
        return {"error": "No message"}

    intent_data = LLMService.extract_intent(message)

    return intent_data