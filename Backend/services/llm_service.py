import os
import requests
import json


class LLMService:

    @staticmethod
    def extract_intent(message: str):

        API_KEY = os.getenv("GEMINI_API_KEY")

        prompt = f"""
You are a medical assistant.

Extract intent and return ONLY JSON:

{{
    "intent": "book_appointment | cancel | reschedule | availability | general",
    "specialization": "",
    "date": "",
    "time": ""
}}

Message: "{message}"
"""

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}",
                json={
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ]
                }
            )

            result = response.json()
            print("RAW RESPONSE:", result)

            if "candidates" not in result:
                return {
                    "intent": "general",
                    "specialization": "dermatologist"
                }

            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            return json.loads(text)

        except Exception as e:
            print("LLM ERROR:", e)
            return {
                "intent": "general",
                "specialization": "dermatologist"
            }