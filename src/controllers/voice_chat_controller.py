'''
Responsible for the whole speech to speech process

'''

from pydantic import BaseModel
from typing import Optional
from src.utils import stt_service
from src.utils.gemini_service import gemini_service
from src.utils.piper_service import piper_tts_service

class VoiceChatRequest(BaseModel):
    include_voice_response: bool = True
    voice_format: str = "wav"

class VoiceChatResponse(BaseModel):
    transcribed_text: str
    ai_response: str
    voice_data: Optional[str] = None
    voice_format: Optional[str] = None
    voice_filename: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

async def process_voice_chat(audio_data: bytes, request: VoiceChatRequest) -> VoiceChatResponse:
    try:
        # Step 1: Transcribe audio
        transcribed_text = await stt_service.transcribe_audio(audio_data)
        if not transcribed_text:
            return VoiceChatResponse(
                transcribed_text="",
                ai_response="",
                success=False,
                error="Failed to transcribe audio"
            )
        
        # Step 2: Generate AI response
        ai_response = await gemini_service.generate_text(transcribed_text)
        if not ai_response or ai_response.startswith("Error:"):
            return VoiceChatResponse(
                transcribed_text=transcribed_text,
                ai_response="",
                success=False,
                error="Failed to generate AI response"
            )
        
        # Step 3: Generate voice response (optional)
        voice_data = None
        voice_format = None
        voice_filename = None
        
        if request.include_voice_response:
            voice_result = await piper_tts_service.text_to_speech(
                ai_response, 
                request.voice_format
            )
            if voice_result:
                voice_data = voice_result["audio_base64"]
                voice_format = request.voice_format
                voice_filename = voice_result["filename"]
        
        return VoiceChatResponse(
            transcribed_text=transcribed_text,
            ai_response=ai_response,
            voice_data=voice_data,
            voice_format=voice_format,
            voice_filename=voice_filename,
            success=True
        )
        
    except Exception as e:
        return VoiceChatResponse(
            transcribed_text="",
            ai_response="",
            success=False,
            error=str(e)
        )