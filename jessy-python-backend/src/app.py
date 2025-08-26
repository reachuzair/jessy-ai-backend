from fastapi import FastAPI
from src.routes.auth import router as auth_router
from src.routes.ai_chat import router as ai_chat_router

app = FastAPI(
    title="Jessy AI Backend",
    description="AI-powered backend with authentication and chat capabilities",
    version="1.0.0"
)

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include AI chat routes
app.include_router(ai_chat_router, prefix="/ai", tags=["AI Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Jessy AI Backend! Visit /docs for API documentation."}
