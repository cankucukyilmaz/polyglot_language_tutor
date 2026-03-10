import os
import json
import subprocess
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import vosk

app = FastAPI()

# Setup templates (for serving the index.html)
templates = Jinja2Templates(directory="src/templates")

# Configure the local LLM (Ollama) URL via Docker environment variables
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434")

# Language Configurations
# Update these folder/file names if your downloaded model files are named differently in your /models folder!
LANGUAGES = {
    "1": {
        "name": "English",
        "vosk_model": "model-en",
        "voice_model": "en_US-lessac-low.onnx"
    },
    "2": {
        "name": "German",
        "vosk_model": "model-de",
        "voice_model": "de_DE-thorsten-low.onnx"
    },
    "3": {
        "name": "Spanish",
        "vosk_model": "model-es",
        "voice_model": "es_ES-carlfm-x_low.onnx"
    }
}

# Pre-load Vosk models into memory so it doesn't freeze on the first word
print("Loading Vosk models into memory...")
loaded_vosk_models = {}
for lang_id, config in LANGUAGES.items():
    model_path = f"/app/models/{config['vosk_model']}"
    if os.path.exists(model_path):
        loaded_vosk_models[lang_id] = vosk.Model(model_path)
        print(f"Loaded {config['name']} Vosk model.")
    else:
        print(f"Warning: Could not find Vosk model at {model_path}")

@app.get("/", response_class=HTMLResponse)
async def get_webpage(request: Request):
    """Serves the frontend HTML interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{lang_id}")
async def websocket_endpoint(websocket: WebSocket, lang_id: str, speed: float = 1.0):
    """Handles the real-time audio stream, STT, LLM, and TTS generation."""
    await websocket.accept()

    # Get the requested language config
    config = LANGUAGES.get(lang_id)
    if not config or lang_id not in loaded_vosk_models:
        await websocket.close()
        return

    # Initialize the specific Vosk recognizer for this WebSocket session
    recognizer = vosk.KaldiRecognizer(loaded_vosk_models[lang_id], 16000)
    
    # Create a unique temporary audio filename for this specific connection
    temp_filename = f"/app/models/temp_{id(websocket)}.wav"

    try:
        while True:
            # Receive audio bytes from the user's browser
            data = await websocket.receive_bytes()

            # Process the audio with Vosk
            if recognizer.AcceptWaveform(data):
                # The user finished speaking a sentence
                result = json.loads(recognizer.Result())
                user_text = result.get("text", "")

                if user_text:
                    print(f"User ({config['name']}): {user_text}")
                    
                    # --- NEW: SEND USER TRANSCRIPT TO FRONTEND ---
                    await websocket.send_json({"role": "user", "text": user_text})

                    # Prompt for the LLM
                    system_prompt = f"You are a helpful language tutor. The user is practicing {config['name']}. Keep your replies conversational, natural, and limited to 1 or 2 short sentences."
                    
                    payload = {
                        "model": "llama3.2:1b",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_text}
                        ],
                        "stream": False
                    }

                    try:
                        # Send text to Ollama for an AI response
                        print("Tutor is thinking...")
                        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload)
                        ai_response_text = resp.json()["message"]["content"]
                        
                        # Clean up text so it doesn't break the command line later
                        clean_text = ai_response_text.replace('"', '').replace("'", "").replace('\n', ' ')
                        print(f"Tutor ({config['name']}): {clean_text}")

                        # --- NEW: SEND AI TRANSCRIPT TO FRONTEND ---
                        await websocket.send_json({"role": "ai", "text": clean_text})

                        # --- NEW: SPEED CONTROL MATH ---
                        # Piper uses length_scale for duration. 
                        # Speed 1.5x = Duration 0.66x. Speed 0.5x = Duration 2.0x.
                        piper_length_scale = round(1.0 / speed, 2)

                        # Generate audio using Piper TTS
                        voice_model_path = f"/app/models/{config['voice_model']}"
                        cmd_gen = f"echo '{clean_text}' | piper --model {voice_model_path} --length_scale {piper_length_scale} --output_file {temp_filename}"
                        
                        # Run the generation quietly
                        subprocess.run(cmd_gen, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        # Send the generated audio file back to the browser
                        if os.path.exists(temp_filename):
                            with open(temp_filename, "rb") as f:
                                await websocket.send_bytes(f.read())
                            os.remove(temp_filename) # Clean up

                    except Exception as e:
                        print(f"Error communicating with AI or TTS: {e}")

            else:
                # The user is currently speaking (partial audio)
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "")
                
                # --- INTERRUPT FIX ---
                # If Vosk hears even a single tiny word (length > 1), stop the AI's audio immediately
                if len(partial_text) > 1:
                    await websocket.send_json({"action": "stop_audio"})

    except WebSocketDisconnect:
        print(f"Client disconnected.")
    except Exception as e:
        print(f"WebSocket error: {e}")