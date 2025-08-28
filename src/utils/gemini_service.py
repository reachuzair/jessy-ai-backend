import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv
from src.constants.prompt import system_prompt

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.system_prompt = system_prompt
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def generate_text(self, prompt: str, max_tokens: Optional[int] = 1000) -> str:
        try:
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": max_tokens,
            }
            
            full_prompt = f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "Sorry, I couldn't generate a response at this time."
                
        except Exception as e:
            print(f"Error generating text with Gemini: {str(e)}")
            return f"Error: Unable to generate response - {str(e)}"
    
    def is_configured(self) -> bool:
        return bool(self.api_key)

gemini_service = GeminiService()