import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    print("✓ Redis connected successfully")
except Exception as e:
    print(f"⚠ Redis connection failed: {e}")
    print("Chatbot session management will not work properly")
    # Create a mock redis object that raises warnings
    class MockRedis:
        def get(self, key):
            return None
        def set(self, key, value, *args, **kwargs):
            print(f"⚠ MockRedis: Cannot store session (Redis unavailable)")
        def delete(self, key):
            pass
    r = MockRedis()