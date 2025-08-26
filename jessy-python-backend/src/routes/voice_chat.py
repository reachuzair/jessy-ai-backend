from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from src.controllers.voice_chat_controller import (
    process_voice_chat, 
    VoiceChatRequest, 
    VoiceChatResponse
)
from src.utils import stt_service
from src.utils.gemini_service import gemini_service
from src.utils.piper_service import piper_tts_service

router = APIRouter()

@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    include_voice_response: bool = Query(True, description="Include AI voice response"),
    voice_format: str = Query("wav", description="Voice format: wav, mp3, flac")
):
    try:
        # Validate services
        if not stt_service.is_configured():
            raise HTTPException(status_code=500, detail="STT service not configured")
        
        if not gemini_service.is_configured():
            raise HTTPException(status_code=500, detail="Gemini AI not configured")
        
        if include_voice_response and not piper_tts_service.is_configured():
            raise HTTPException(status_code=500, detail="TTS service not configured")
        
        # Read audio data
        audio_data = await audio.read()
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Process voice chat
        request = VoiceChatRequest(
            include_voice_response=include_voice_response,
            voice_format=voice_format
        )
        
        response = await process_voice_chat(audio_data, request)
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def voice_chat_health():
    return {
        "stt_configured": stt_service.is_configured(),
        "ai_configured": gemini_service.is_configured(),
        "tts_configured": piper_tts_service.is_configured()
    }