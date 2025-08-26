from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from src.utils.gemini_service import gemini_service
from src.utils.piper_service import piper_tts_service

class ChatRequest(BaseModel):
    message: str
    include_voice: bool = True
    voice_format: str = "wav"
    language: str = "english"  # New field for language selection

class ChatResponse(BaseModel):
    message: str
    ai_response: str
    voice_data: Optional[str] = None
    voice_format: Optional[str] = None
    voice_filename: Optional[str] = None
    voice_file_path: Optional[str] = None
    voice_file_size: Optional[int] = None
    language: Optional[str] = None  # New field to return the language used
    model_used: Optional[str] = None  # New field to return the model used
    success: bool = True
    error: Optional[str] = None

class AIChatController:
    async def chat_with_ai(self, request: ChatRequest) -> ChatResponse:
        try:
            if not gemini_service.is_configured():
                raise HTTPException(
                    status_code=500, 
                    detail="Gemini AI service is not properly configured"
                )
            
            if request.include_voice and not piper_tts_service.is_configured():
                raise HTTPException(
                    status_code=500, 
                    detail="Piper TTS service is not properly configured"
                )
            
            ai_response = await gemini_service.generate_text(request.message)
            
            if not ai_response or ai_response.startswith("Error:"):
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to generate AI response: {ai_response}"
                )
            
            voice_data = None
            voice_format = None
            voice_filename = None
            voice_file_path = None
            voice_file_size = None
            language = None
            model_used = None
            
            if request.include_voice:
                supported_formats = piper_tts_service.get_supported_formats()
                if request.voice_format not in supported_formats:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Unsupported voice format. Supported: {supported_formats}"
                    )
                
                # Validate language
                available_languages = piper_tts_service.get_available_languages()
                if not any(lang["language"] == request.language.lower() for lang in available_languages):
                    available_lang_names = [lang["language"] for lang in available_languages]
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported language '{request.language}'. Available languages: {available_lang_names}"
                    )
                
                voice_result = await piper_tts_service.text_to_speech(
                    ai_response, 
                    request.voice_format,
                    request.language
                )
                
                if voice_result:
                    voice_data = voice_result["audio_base64"]
                    voice_format = request.voice_format
                    voice_filename = voice_result["filename"]
                    voice_file_path = voice_result["file_path"]
                    voice_file_size = voice_result["file_size"]
                    language = voice_result["language"]
                    model_used = voice_result["model_used"]
                else:
                    print("Warning: Voice synthesis failed, returning text only")
            
            return ChatResponse(
                message=request.message,
                ai_response=ai_response,
                voice_data=voice_data,
                voice_format=voice_format,
                voice_filename=voice_filename,
                voice_file_path=voice_file_path,
                voice_file_size=voice_file_size,
                language=language,
                model_used=model_used,
                success=True
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in chat_with_ai: {str(e)}")
            return ChatResponse(
                message=request.message,
                ai_response="",
                success=False,
                error=f"Internal server error: {str(e)}"
            )
    
    async def health_check(self) -> dict:
        return {
            "gemini_configured": gemini_service.is_configured(),
            "piper_configured": piper_tts_service.is_configured(),
            "supported_voice_formats": piper_tts_service.get_supported_formats(),
            "available_languages": piper_tts_service.get_available_languages()
        }

ai_chat_controller = AIChatController()