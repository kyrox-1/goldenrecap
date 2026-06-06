import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

# ဘယ်နေရာကမဆို လှမ်းချိတ်ရင် အလုပ်လုပ်အောင် CORS ဖွင့်ပေးခြင်း
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ကမ္ဘာ့ဘယ်လင့်ခ်ကမဆို လှမ်းချိတ်လို့ရအောင် ဖွင့်ပေးထားသည်
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ElevenLabs API Key ကို Render Environment ထဲကနေ ဆွဲယူမည် (သို့မဟုတ် သင့် Key တိုက်ရိုက်ထည့်နိုင်သည်)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "သင့်_API_Key_နေရာတွင်_အစားထိုးရန်")

class VoiceRequest(BaseModel):
    text: str
    voice_id: str

@app.get("/")
def read_root():
    return {"status": "Backend is running flawlessly!"}

@app.post("/generate-voice/")
async def generate_voice(request: VoiceRequest):
    # ElevenLabs သို့ လှမ်းပို့မည့် URL
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{request.voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": request.text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="ElevenLabs API Error")
            
            # အသံဖိုင် (Binary) ကို တိုက်ရိုက် ပြန်ပေးခြင်း
            from fastapi.responses import Response
            return Response(content=response.content, media_type="audio/mpeg")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
