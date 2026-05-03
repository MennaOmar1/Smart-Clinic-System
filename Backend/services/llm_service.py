import os
import requests
import json
<<<<<<< HEAD
=======
import re
from dotenv import load_dotenv

# تحميل .env
load_dotenv()
>>>>>>> 9b23da4 ( changes)


class LLMService:

    @staticmethod
<<<<<<< HEAD
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
=======
    def detect_language(text: str) -> str:
        """Detect if text is primarily Arabic or English"""
        # Arabic Unicode range
        arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
        english_chars = re.findall(r'[a-zA-Z]', text)
        
        if len(arabic_chars) > len(english_chars):
            return "ar"
        return "en"

    @staticmethod
    def extract_intent(message: str):
        lang = LLMService.detect_language(message)
        
        if lang == "ar":
            prompt = f"""
            أنت مساعد طبي لنظام حجز العيادة.
            استخرج النية من رسالة المستخدم وأرجع JSON صحيح فقط.
            
            إذا لم يحدد المستخدم التخصص، استنتج التخصص الأنسب من أعراضه.
            
            أرجع بالضبط هذا هيكل JSON:
            {{
                "intent": "book_appointment|cancel|reschedule|availability|general",
                "specialization": "dermatologist|cardiologist|neurologist|other",
                "suggested_reason": "السبب المقترح إذا كان المستخدم لا يعرف التخصص",
                "date": "YYYY-MM-DD أو today أو tomorrow أو نص فارغ",
                "time": "HH:MM أو نص فارغ"
            }}
            
            أرجع JSON فقط، بدون نصوص أخرى.

            رسالة المستخدم: "{message}"
            """
        else:
            prompt = f"""
            You are a medical assistant for a clinic booking system.
            Extract intent from the user message and return ONLY valid JSON.
            
            If the user hasn't specified a specialization, suggest the most suitable one based on their symptoms.
            
            Return exactly this JSON structure:
            {{
                "intent": "book_appointment|cancel|reschedule|availability|general",
                "specialization": "dermatologist|cardiologist|neurologist|other",
                "suggested_reason": "Reason for the suggested specialization if user didn't know",
                "date": "YYYY-MM-DD or today or tomorrow or empty string",
                "time": "HH:MM or empty string"
            }}
            
            Return ONLY the JSON, no other text.

            User message: "{message}"
            """
        
        API_KEY = os.getenv("GEMINI_API_KEY")
        
        if not API_KEY:
            print("❌ ERROR: GEMINI_API_KEY not set in environment variables")
            return {
                "intent": "general",
                "specialization": None,
                "date": None,
                "time": None
            }
>>>>>>> 9b23da4 ( changes)

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}",
                json={
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ]
<<<<<<< HEAD
                }
            )

            result = response.json()
            print("RAW RESPONSE:", result)

            if "candidates" not in result:
=======
                },
                timeout=10
            )
            
            response.raise_for_status()

            result = response.json()

            print("✓ Gemini API Response received")

            if "candidates" not in result:
                print("⚠ Gemini error - no candidates:", result)
>>>>>>> 9b23da4 ( changes)
                return {
                    "intent": "general",
                    "specialization": "dermatologist"
                }

<<<<<<< HEAD
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
=======
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip()
>>>>>>> 9b23da4 ( changes)

            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

<<<<<<< HEAD
            return json.loads(text)

        except Exception as e:
            print("LLM ERROR:", e)
            return {
                "intent": "general",
                "specialization": "dermatologist"
            }
=======
            parsed = json.loads(text)
            print(f"✓ Intent extracted: {parsed.get('intent')}")
            # Ensure all expected fields exist
            parsed.setdefault("suggested_reason", "")
            return parsed

        except requests.exceptions.RequestException as e:
            print(f"❌ LLM API Error: {e}")
            return {
                "intent": "general",
                "specialization": None,
                "suggested_reason": "",
                "date": None,
                "time": None
            }
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}. Response text: {text}")
            return {
                "intent": "general",
                "specialization": None,
                "suggested_reason": "",
                "date": None,
                "time": None
            }
        except Exception as e:
            print(f"❌ Unexpected error in LLM: {e}")
            return {
                "intent": "general",
                "specialization": None,
                "suggested_reason": "",
                "date": None,
                "time": None
            }

    @staticmethod
    def get_medical_recommendation(symptoms: str):
        """Generate medical recommendations based on symptoms using LLM"""

        prompt = f"""
        You are a medical assistant AI. Based on the user's symptoms, provide general health information.
        IMPORTANT: You are NOT providing a diagnosis or medical advice. Only general educational information.
        
        Return ONLY valid JSON with this structure:
        {{
            "general_info": "General educational information about the symptoms",
            "when_to_see_doctor": "When they should seek professional medical attention",
            "recommended_specialists": ["specialist1", "specialist2"],
            "self_care": ["suggestion1", "suggestion2", "suggestion3"],
            "warning_signs": ["sign1 that requires immediate attention", "sign2"]
        }}
        
        Return ONLY the JSON, no other text.
        
        User symptoms: "{symptoms}"
        """

        API_KEY = os.getenv("GEMINI_API_KEY")

        if not API_KEY:
            print("❌ ERROR: GEMINI_API_KEY not set")
            return {
                "error": "API not configured",
                "general_info": "Please contact a healthcare professional",
                "recommended_specialists": [],
                "self_care": [],
                "warning_signs": []
            }

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}",
                json={
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ]
                },
                timeout=10
            )

            response.raise_for_status()
            result = response.json()

            if "candidates" not in result:
                print("⚠ Gemini error - no candidates")
                return {"error": "No response from LLM"}

            text = result["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip()

            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            parsed = json.loads(text)
            print(f"✓ Medical recommendation generated")
            return parsed

        except requests.exceptions.RequestException as e:
            print(f"❌ LLM API Error: {e}")
            return {"error": f"API error: {str(e)}"}
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return {"error": f"Parse error: {str(e)}"}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {"error": f"Error: {str(e)}"}
>>>>>>> 9b23da4 ( changes)
