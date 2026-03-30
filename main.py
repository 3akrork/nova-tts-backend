import os
import uuid
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from TTS.api import TTS
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
BUCKET_NAME  = os.environ.get("SUPABASE_BUCKET", "tts-audio")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

print("Loading Coqui TTS model...")
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
print("Model ready.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
async def text_to_speech(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.wav")
    try:
        tts.tts_to_file(text=req.text, file_path=tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")
    storage_path = f"audio/{uuid.uuid4()}.wav"
    try:
        with open(tmp_path, "rb") as f:
            supabase.storage.from_(BUCKET_NAME).upload(path=storage_path, file=f, file_options={"content-type": "audio/wav"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")
    finally:
        os.remove(tmp_path)
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{storage_path}"
    return {"url": public_url}

@app.get("/health")
def health():
    return {"status": "ok"}
