import os
import urllib.request
import zipfile
import ssl

# Bypass SSL issues on macOS
ssl._create_default_https_context = ssl._create_unverified_context

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Small, fast Vosk models for quick real-time listening
VOSK_LINKS = {
    "model-en": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
    "model-de": "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip",
    "model-es": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
}

# Piper ONNX and JSON config files for speaking
PIPER_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
PIPER_FILES = {
    "en_US-lessac-low.onnx": f"{PIPER_BASE_URL}/en/en_US/lessac/low/en_US-lessac-low.onnx?download=true",
    "en_US-lessac-low.onnx.json": f"{PIPER_BASE_URL}/en/en_US/lessac/low/en_US-lessac-low.onnx.json?download=true",
    "de_DE-thorsten-low.onnx": f"{PIPER_BASE_URL}/de/de_DE/thorsten/low/de_DE-thorsten-low.onnx?download=true",
    "de_DE-thorsten-low.onnx.json": f"{PIPER_BASE_URL}/de/de_DE/thorsten/low/de_DE-thorsten-low.onnx.json?download=true",
    
    # --- THE FIX: Updated to 'x_low' ---
    "es_ES-carlfm-x_low.onnx": f"{PIPER_BASE_URL}/es/es_ES/carlfm/x_low/es_ES-carlfm-x_low.onnx?download=true",
    "es_ES-carlfm-x_low.onnx.json": f"{PIPER_BASE_URL}/es/es_ES/carlfm/x_low/es_ES-carlfm-x_low.onnx.json?download=true"
}

def download_file(url, dest):
    print(f"Downloading {os.path.basename(dest)}...")
    urllib.request.urlretrieve(url, dest)

print("--- DOWNLOADING VOSK MODELS ---")
for folder_name, url in VOSK_LINKS.items():
    target_folder = os.path.join(MODELS_DIR, folder_name)
    if not os.path.exists(target_folder):
        zip_path = os.path.join(MODELS_DIR, f"{folder_name}.zip")
        download_file(url, zip_path)
        print(f"Extracting {folder_name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(MODELS_DIR)
        
        extracted_folder = os.path.join(MODELS_DIR, url.split('/')[-1].replace('.zip', ''))
        if os.path.exists(extracted_folder):
            os.rename(extracted_folder, target_folder)
        os.remove(zip_path)
    else:
        print(f"Skipping {folder_name} (already exists)")

print("\n--- DOWNLOADING PIPER VOICES ---")
for file_name, url in PIPER_FILES.items():
    target_file = os.path.join(MODELS_DIR, file_name)
    if not os.path.exists(target_file):
        download_file(url, target_file)
    else:
        print(f"Skipping {file_name} (already exists)")

print("\nAll models downloaded successfully! You can now run Docker.")