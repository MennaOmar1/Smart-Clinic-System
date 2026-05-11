from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv
load_dotenv()
# Create OAuth ONCE and attach to app
oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile https://www.googleapis.com/auth/calendar.events"},
    client_auth_method="client_secret_post",
    timeout=10.0
)

# Temporarily disabled OAuth print statements
# print("CLIENT ID:", os.getenv("GOOGLE_CLIENT_ID"))
# print("CLIENT SECRET:", os.getenv("GOOGLE_CLIENT_SECRET"))


