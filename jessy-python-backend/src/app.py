from fastapi import FastAPI
from src.routes.auth import router as auth_router
from src.routes.ai_chat import router as ai_chat_router
from src.routes.stt import router as stt_router
from src.routes.voice_chat import router as voice_chat_router

app = FastAPI(
    title="Jessy AI Backend",
    description="AI-powered backend with voice chat, authentication, and AI capabilities",
    version="1.0.0"
)

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include AI chat routes
app.include_router(ai_chat_router, prefix="/ai", tags=["AI Chat"])

# Include STT routes
app.include_router(stt_router, prefix="/stt", tags=["Speech-to-Text"])

# Include Voice Chat routes
app.include_router(voice_chat_router, prefix="/voice", tags=["Voice Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Jessy AI Backend! Visit /docs for API documentation."}
