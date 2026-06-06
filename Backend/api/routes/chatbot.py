from fastapi import APIRouter, Request, Response, Depends
from sqlalchemy.orm import Session
import uuid
import httpx
import asyncio

from core.database import get_db
from services.chatbot_service import ChatbotService
from services.llm_service import LLMService
from services.session_service import SessionService
from schemas.chatbot import ChatRequest

router = APIRouter(tags=["Chatbot"])

RAG_URL = "https://egypt-medical-api-production.up.railway.app"


# =========================
# 🔁 RAG CALL WITH RETRY
# =========================
async def call_rag(payload):
    retries = 3
    timeout = 60.0

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(retries):
            try:
                response = await client.post(RAG_URL, json=payload)
                response.raise_for_status()
                return response.json()

            except (httpx.ReadTimeout, httpx.ConnectError) as e:
                print(f"RAG ERROR (attempt {attempt+1}): {e}")

            except Exception as e:
                print(f"RAG UNKNOWN ERROR: {e}")
                break

            await asyncio.sleep(1)

    return None


# =========================
# 💬 MAIN CHAT
# =========================
@router.post("/")
async def chat(
    request: Request,
    response: Response,
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        message = payload.message.strip()
        user_id = payload.user_id or request.cookies.get("chatbot_user_id") or str(uuid.uuid4())

        # =========================
        # 🧠 SESSION INIT
        # =========================
        session = SessionService.get_or_create(user_id)

        if "history" not in session:
            session["history"] = []

        if "state" not in session:
            session["state"] = "start"

        history = session["history"]

        # =========================
        # 🧹 RESET COMMAND (IMPORTANT)
        # =========================
        if message.lower() in ["reset", "restart", "start over", "new"]:
            session["history"] = []
            session["state"] = "start"
            SessionService.update(user_id, session)

            return {
                "user_id": user_id,
                "reply": "Session restarted. You can start again.",
                "data": None
            }

        # =========================
        # 🧠 LIMIT HISTORY (IMPORTANT)
        # =========================
        history = history[-6:]   # نخليها قصيرة عشان Gemini يركز

        # =========================
        # 🧠 ADD USER MESSAGE
        # =========================
        history.append({
            "role": "user",
            "content": message
        })

        # =========================
        # 🧠 FORCE RAG IF MEDICAL
        # =========================
        decision = LLMService.process_message(message)

        if decision["action"] == "rag_api":
            session["state"] = "rag"

        # =========================
        # 🧠 RAG FLOW
        # =========================
        if session["state"] == "rag":

            rag_data = await call_rag({
                "message": message,
                "history": history
            })

            if not rag_data:
                result = {
                    "reply": "Medical service is slow, but I’ll try to help.",
                    "data": None
                }
            else:
                result = {
                    "reply": "Medical assessment:",
                    "data": rag_data["response"]   # FIX IMPORTANT
                }

        # =========================
        # 🧠 NORMAL FLOW
        # =========================
        else:
            result = ChatbotService.handle_chat(db, user_id, message)

        # =========================
        # 🧠 SAVE RESPONSE
        # =========================
        history.append({
            "role": "assistant",
            "content": result.get("data") or result.get("reply", "")
        })

        session["history"] = history
        SessionService.update(user_id, session)

        # =========================
        # 🍪 COOKIE
        # =========================
        response.set_cookie(
            key="chatbot_user_id",
            value=user_id,
            httponly=True,
            max_age=60 * 60 * 24 * 7
        )

        return {
            "user_id": user_id,
            **result
        }

    except Exception as e:
        print("CHATBOT ERROR:", str(e))
        return {"error": str(e)}
