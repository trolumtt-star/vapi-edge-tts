import io
import edge_tts
from fastapi import FastAPI, Request, Response
from pydub import AudioSegment

app = FastAPI()

# Kadın sesi için: "tr-TR-EmelNeural"
# Erkek sesi için: "tr-TR-AhmetNeural"
VOICE = "tr-TR-AhmetNeural"

@app.post("/synthesize")
async def synthesize(request: Request):
    data = await request.json()
    text = data.get("message", {}).get("text", "")
    sample_rate = data.get("message", {}).get("sampleRate", 24000)

    if not text:
        return Response(content=b"", media_type="application/octet-stream")

    # Edge TTS'ten MP3 olarak sesi al
    communicate = edge_tts.Communicate(text, VOICE)
    mp3_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_bytes += chunk["data"]

    # Vapi'nin istediği ham PCM (16-bit mono) formatına çevir
    audio = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
    audio = audio.set_frame_rate(sample_rate).set_channels(1).set_sample_width(2)
    pcm_bytes = audio.raw_data

    return Response(content=pcm_bytes, media_type="application/octet-stream")
