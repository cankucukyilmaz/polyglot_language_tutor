import os
import re
import json
import asyncio
import subprocess
import tempfile
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from vosk import Model, KaldiRecognizer
import ollama

LANGUAGES = {
    "1": {
        "name": "English",
        "vosk_model": "models/model-en",
        "voice_model": "models/en_US-lessac-low.onnx",
        "system_prompt": "You are a patient, friendly English tutor. Answer in 1 or 2 short sentences. Gently correct the user if they make a grammar mistake."
    },
    "2": {
        "name": "German",
        "vosk_model": "models/model-de",
        "voice_model": "models/de_DE-thorsten-low.onnx",
        "system_prompt": "Du bist ein geduldiger, freundlicher Deutschlehrer. Antworte in 1 oder 2 kurzen Sätzen auf Deutsch. Korrigiere den Benutzer sanft, wenn er einen Fehler macht."
    },
    "3": {
        "name": "Spanish",
        "vosk_model": "models/model-es",
        "voice_model": "models/es_ES-carlfm-x_low.onnx",
        "system_prompt": "Eres un tutor de español paciente y amable. Responde en 1 o 2 oraciones cortas. Corrige suavemente al usuario si comete un error."
    }
}

print("Loading AI Speech Models into memory... This may take a minute.")
loaded_vosk_models = {}
for key, config in LANGUAGES.items():
    if os.path.exists(config["vosk_model"]):
        loaded_vosk_models[key] = Model(config["vosk_model"])
    else:
        print(f"Warning: Vosk model for {config['name']} not found at {config['vosk_model']}")

app = FastAPI(title="Polyglot AI Tutor")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def get_webpage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{lang_id}")
async def websocket_endpoint(websocket: WebSocket, lang_id: str):
    await websocket.accept()
    
    if lang_id not in LANGUAGES or lang_id not in loaded_vosk_models:
        await websocket.send_json({"error": "Language model not available."})
        await websocket.close()
        return

    config = LANGUAGES[lang_id]
    recognizer = KaldiRecognizer(loaded_vosk_models[lang_id], 16000)
    print(f"\nUser connected. Live session started in: {config['name']}")
    
    bot_is_speaking = False

    try:
        while True:
            data = await websocket.receive_bytes()
            
            # Interruption Check
            if bot_is_speaking:
                partial_result = json.loads(recognizer.PartialResult())
                partial_text = partial_result.get("partial", "").strip()
                if len(partial_text) > 3: 
                    print(f"\n[User interrupted {config['name']} Tutor!]")
                    await websocket.send_json({"action": "stop_audio"})
                    bot_is_speaking = False
                continue 

            # Normal Listening
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                user_text = result.get("text", "").strip()
                
                if user_text:
                    print(f"\nYou: {user_text}")
                    bot_is_speaking = True
                    
                    print(f"{config['name']} Tutor is thinking...")
                    
                    # Call Ollama asynchronously
                    response = await asyncio.to_thread(
                        ollama.chat,
                        model='llama3.2:1b',
                        messages=[
                            {'role': 'system', 'content': config["system_prompt"]},
                            {'role': 'user', 'content': user_text}
                        ]
                    )
                    
                    bot_text = response['message']['content']
                    print(f"Tutor: {bot_text}")
                    
                    clean_text = re.sub(r'[^a-zA-Z0-9äöüÄÖÜßñáéíóú\s\.,!\?]', '', bot_text)
                    
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                        temp_filename = temp_audio.name
                    
                    cmd_gen = f"echo '{clean_text}' | piper --model {config['voice_model']} --length_scale 1.1 --output_file {temp_filename}"
                    await asyncio.to_thread(subprocess.run, cmd_gen, shell=True)
                    
                    with open(temp_filename, "rb") as f:
                        audio_data = f.read()
                        if bot_is_speaking: 
                            await websocket.send_bytes(audio_data)
                    
                    os.remove(temp_filename)
                    bot_is_speaking = False

    except WebSocketDisconnect:
        print("\nUser disconnected.")
    except Exception as e:
        print(f"\nConnection error: {e}")