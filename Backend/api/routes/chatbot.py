from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
import uuid
from core.database import get_db
from services.chatbot_service import ChatbotService
from services.llm_service import LLMService
from schemas.chatbot import ChatRequest
router = APIRouter(tags=["Chatbot"])



@router.post("/")
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):

    try:
<<<<<<< HEAD
        message = payload.message
        user_id = payload.user_id

        result = ChatbotService.handle_chat(db, user_id, message)

        return result

    except Exception as e:
        print("CHATBOT ERROR:", str(e))
        return {"error": str(e)}

=======
        data = await request.json()
    except Exception as e:
        return {"error": f"Invalid JSON: {str(e)}"}
    
    message = data.get("message")
    user_id = data.get("user_id") or str(uuid.uuid4())
>>>>>>> 9b23da4 ( changes)

    if not message:
        return {"error": "Message is required"}
    
    try:
        result = ChatbotService.handle_chat(db, str(user_id), str(message))
        print(f"✓ Chatbot response for user {user_id}: {result.get('reply')}")
        return {"user_id": user_id, **result}
    except Exception as e:
        print(f"✗ Chatbot error for user {user_id}: {e}")
        return {"error": f"Chatbot error: {str(e)}"}


# LLM INTENT EXTRACTION ENDPOINT
@router.post("/intent")
async def extract_intent(request: Request):
    """Extract user intent using LLM"""

    try:
        data = await request.json()
    except Exception as e:
        return {"error": f"Invalid JSON: {str(e)}"}
    
    message = data.get("message")

    if not message:
        return {"error": "Message is required"}

    try:
        intent_data = LLMService.extract_intent(str(message))
        print(f"✓ Intent extracted: {intent_data.get('intent')}")
        return intent_data
    except Exception as e:
        print(f"✗ Intent extraction error: {e}")
        return {"error": f"Failed to extract intent: {str(e)}"}


# MEDICAL RECOMMENDATIONS ENDPOINT
@router.post("/recommendation")
async def get_medical_recommendation(request: Request):
    """Get medical recommendations based on symptoms using LLM"""

    try:
        data = await request.json()
    except Exception as e:
        return {"error": f"Invalid JSON: {str(e)}"}
    
    symptoms = data.get("symptoms")

    if not symptoms:
        return {"error": "Symptoms are required"}

    try:
        recommendation = LLMService.get_medical_recommendation(str(symptoms))
        print(f"✓ Medical recommendation generated")
        return {
            "disclaimer": "⚠️ This is general educational information, not medical advice. Always consult with a healthcare professional.",
            **recommendation
        }
    except Exception as e:
        print(f"✗ Recommendation error: {e}")
        return {"error": f"Failed to generate recommendation: {str(e)}"}