import requests
import os
import json
from dotenv import load_dotenv

# تحميل .env
load_dotenv()


class LLMService:

    @staticmethod
    #def extract_intent(message: str):

    # prompt = f"""
    #   You are a medical assistant.

           # Extract intent and return ONLY JSON.

           # {{
            #    "intent": "book_appointment | cancel | reschedule | availability | general",
            #    "specialization": "",
             #   "date": "",
            #    "time": ""
         #   }}

       # Message: "{message}"
       # """
    def extract_intent(message):

        # TEMP FIX: disable Gemini بسبب quota
        return {
            "intent": "book_appointment",
            "specialization": "dermatologist"
        }
        API_KEY = os.getenv("GEMINI_API_KEY")

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

        try:
            if "candidates" not in result:
                print("Gemini error:", result)
                return {
                    "intent": "general",
                    "specialization": None,
                    "date": None,
                    "time": None
                }

            text = result["candidates"][0]["content"]["parts"][0]["text"]

            text = text.strip()

            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            return json.loads(text)

        except Exception as e:
            print("LLM parsing error:", e)

            return {
                "intent": "general",
                "specialization": None,
                "date": None,
                "time": None
            }



if __name__ == "__main__":
    print(LLMService.extract_intent("عايز احجز دكتور جلدية بكرة"))