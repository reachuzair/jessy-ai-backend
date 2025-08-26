import os
import aiohttp
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSEMBLYAI_API_KEY")


def is_configured() -> bool:
    if(API_KEY):
        print("AssemblyAI API key loaded successfully.")
    else:
        print("AssemblyAI API key not found. Please set ASSEMBLYAI_API_KEY in your environment variables.")
    return bool(API_KEY)


async def upload_audio(audio_data: bytes) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.assemblyai.com/v2/upload",
            headers={"authorization": API_KEY},
            data=audio_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("upload_url")
            return None

async def submit_transcription(upload_url: str) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={"authorization": API_KEY},
            json={"audio_url": upload_url}
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("id")
            return None

async def poll_result(transcript_id: str) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers={"authorization": API_KEY}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    status = result.get("status")
                    
                    if status == "completed":
                        return result.get("text")
                    elif status == "error":
                        print(f"Transcription error: {result.get('error')}")
                        return None
                    
                    await asyncio.sleep(1)
                else:
                    return None

async def transcribe_audio(audio_data: bytes) -> Optional[str]:
    try:
        upload_url = await upload_audio(audio_data)
        if not upload_url:
            return None
        
        transcript_id = await submit_transcription(upload_url)
        if not transcript_id:
            return None
        
        return await poll_result(transcript_id)
        
    except Exception as e:
        print(f"AssemblyAI error: {e}")
        return None
