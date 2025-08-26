import os
import subprocess
import tempfile
import base64
import uuid
import datetime
from pathlib import Path
from typing import Optional

class PiperTTSService:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.piper_dir = self.project_root / "piper"
        self.voice_dir = self.piper_dir / "voice"
        self.piper_exe = self.piper_dir / "piper.exe"
        
        # Define available voice models
        self.voice_models = {
            "english": {
                "model_path": self.piper_dir / "en_US-bryce-medium.onnx",
                "name": "en_US-bryce-medium",
                "language": "English"
            },
            "spanish": {
                "model_path": self.piper_dir / "es_MX-ald-medium.onnx",
                "name": "es_MX-ald-medium", 
                "language": "Spanish"
            }
        }
        
        self.voice_dir.mkdir(exist_ok=True)
        
        if not self.piper_exe.exists():
            print(f"Piper executable not found at {self.piper_exe}")
            print(f"Current piper directory contents: {list(self.piper_dir.iterdir()) if self.piper_dir.exists() else 'Directory does not exist'}")
            raise FileNotFoundError(f"Piper executable not found at {self.piper_exe}")
        
        # Check if at least one model exists
        available_models = []
        for lang, model_info in self.voice_models.items():
            if model_info["model_path"].exists():
                available_models.append(lang)
            else:
                print(f"Warning: Model for {lang} not found at {model_info['model_path']}")
        
        if not available_models:
            raise FileNotFoundError("No voice models found. Please ensure at least one model file exists.")
        
        print(f"Available voice models: {available_models}")
    
    def get_available_languages(self) -> list:
        """Get list of available languages with their model information"""
        available = []
        for lang, model_info in self.voice_models.items():
            if model_info["model_path"].exists():
                available.append({
                    "language": lang,
                    "name": model_info["name"],
                    "display_name": model_info["language"],
                    "model_path": str(model_info["model_path"])
                })
        return available
    
    def get_model_path(self, language: str) -> Optional[Path]:
        """Get the model path for a specific language"""
        if language.lower() in self.voice_models:
            model_info = self.voice_models[language.lower()]
            if model_info["model_path"].exists():
                return model_info["model_path"]
        return None
    
    async def text_to_speech(self, text: str, output_format: str = "wav", language: str = "english") -> Optional[dict]:
        try:
            # Get the model path for the specified language
            model_path = self.get_model_path(language)
            if not model_path:
                available_langs = [lang for lang in self.voice_models.keys() if self.voice_models[lang]["model_path"].exists()]
                raise ValueError(f"Language '{language}' not available. Available languages: {available_langs}")
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"voice_{language}_{timestamp}_{unique_id}.{output_format}"
            audio_file_path = self.voice_dir / filename
            
            cmd = [
                str(self.piper_exe),
                "--model", str(model_path),
                "--output_file", str(audio_file_path)
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.piper_dir)
            )
            
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                print(f"Piper TTS error (return code {process.returncode}): {stderr}")
                print(f"Piper stdout: {stdout}")
                print(f"Command used: {' '.join(cmd)}")
                return None
            
            if audio_file_path.exists():
                with open(audio_file_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                return {
                    "audio_base64": audio_base64,
                    "file_path": str(audio_file_path),
                    "filename": filename,
                    "file_size": len(audio_data),
                    "language": language,
                    "model_used": self.voice_models[language.lower()]["name"]
                }
            else:
                print(f"Audio file was not created at {audio_file_path}")
                return None
                
        except Exception as e:
            print(f"Error in text_to_speech: {str(e)}")
            return None
    
    def is_configured(self) -> bool:
        return self.piper_exe.exists() and any(
            model_info["model_path"].exists() 
            for model_info in self.voice_models.values()
        )
    
    def get_supported_formats(self) -> list:
        return ["wav", "mp3", "flac"]
    
    def get_voice_files(self) -> list:
        try:
            voice_files = []
            for file_path in self.voice_dir.glob("*"):
                if file_path.is_file() and file_path.suffix in [".wav", ".mp3", ".flac"]:
                    stat = file_path.stat()
                    voice_files.append({
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "path": str(file_path)
                    })
            return sorted(voice_files, key=lambda x: x["created"], reverse=True)
        except Exception as e:
            print(f"Error getting voice files: {str(e)}")
            return []

piper_tts_service = PiperTTSService()