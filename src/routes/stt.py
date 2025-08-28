from fastapi import APIRouter, HTTPException, UploadFile, File
from src.utils import stt_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class STTResponse(BaseModel):
    text: str
    success: bool
    error: Optional[str] = None

@router.post("/transcribe", response_model=STTResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        if not stt_service.is_configured():
            raise HTTPException(
                status_code=500, 
                detail="AssemblyAI not configured. Add ASSEMBLYAI_API_KEY to environment"
            )
        
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        text = await stt_service.transcribe_audio(audio_data)
        
        if not text:
            raise HTTPException(status_code=500, detail="Transcription failed")
        
        return STTResponse(text=text, success=True)
        
    except HTTPException:
        raise
    except Exception as e:
        return STTResponse(text="", success=False, error=str(e))

@router.get("/health")
async def stt_health():
    return {"configured": stt_service.is_configured()}