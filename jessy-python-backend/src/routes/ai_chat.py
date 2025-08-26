from fastapi import APIRouter, HTTPException, Query
from src.controllers.ai_chat_controller import (
    ai_chat_controller, 
    ChatRequest, 
    ChatResponse
)
from src.utils.piper_service import piper_tts_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        response = await ai_chat_controller.chat_with_ai(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/health")
async def get_ai_health():
    try:
        health = await ai_chat_controller.health_check()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/text-only", response_model=ChatResponse)
async def chat_text_only(
    message: str = Query(..., description="Text message to send to AI")
):
    try:
        request = ChatRequest(message=message, include_voice=False)
        response = await ai_chat_controller.chat_with_ai(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/voice-simple")
async def chat_with_voice_simple(
    message: str = Query(..., description="Text message to send to AI"),
    voice_format: str = Query("wav", description="Audio format: wav, mp3, flac")
):
    try:
        request = ChatRequest(
            message=message, 
            include_voice=True, 
            voice_format=voice_format
        )
        response = await ai_chat_controller.chat_with_ai(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice/files")
async def list_voice_files():
    try:
        voice_files = piper_tts_service.get_voice_files()
        return {
            "voice_files": voice_files,
            "total_files": len(voice_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))