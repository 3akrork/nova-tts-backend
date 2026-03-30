import os
import io
import base64
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS

app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
)


class TTSRequest(BaseModel):
        text: str


@app.post("/tts")
async def text_to_speech(req: TTSRequest):
        if not req.text.strip():
                    raise HTTPException(status_code=400, detail="text cannot be empty")
                try:
                            tts = gTTS(text=req.text, lang="en")
                            buf = io.BytesIO()
                            tts.write_to_fp(buf)
                            buf.seek(0)
                            audio_b64 = base64.b64encode(buf.read()).decode("utf-8")
except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")
    return {"audio": audio_b64, "format": "mp3"}


@app.get("/health")
def health():
        return {"status": "ok"}
