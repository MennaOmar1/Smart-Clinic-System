from dotenv import load_dotenv
from core.oauth import oauth
load_dotenv()
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from api.routes import auth, google_auth, admin, appointments, protected, doctor, auth_refresh

app = FastAPI()

# Session middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key="supersecretkey123456"
)


# Attach to app state
app.state.oauth = oauth


# Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(google_auth.router, prefix="/auth", tags=["Google Auth"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(protected.router, tags=["Protected"])
app.include_router(doctor.router, prefix="/doctor", tags=["Doctor"])
app.include_router(auth_refresh.router, tags=["Auth"])

@app.get("/")
def home():
    return {"message": "API running"}