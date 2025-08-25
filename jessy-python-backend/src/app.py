from fastapi import FastAPI
from src.routes.auth import router as auth_router

app = FastAPI()

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}
