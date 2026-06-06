import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from elevenlabs.client import ElevenLabs
from io import BytesIO

app = FastAPI(title="AI Voice Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ ဒီနေရာမှာ "YOUR_API_KEY" အစား သင့်ရဲ့ ElevenLabs API Key ကို ထည့်ပေးရပါမယ်
API_KEY = "sk_74218654fbf463f9d96c7edb8d28c7052cae10c09637a176"
client = ElevenLabs(api_key=API_KEY)

class TextRequest(BaseModel):
    text: str
    voice_id: str = "Rachel"

@app.post("/generate-voice/")
async def generate_voice(request: TextRequest):
    try:
        audio_generator = client.generate(
            text=request.text,
            voice=request.voice_id,
            model="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(audio_generator)
        return StreamingResponse(
            BytesIO(audio_bytes), 
            media_type="audio/mpeg"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Server is running!"}
