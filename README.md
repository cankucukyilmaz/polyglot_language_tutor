# 🌍 Polyglot AI Tutor (Live Mode)

A real-time, interruptible, voice-based AI language tutor running entirely offline in Docker. 

This project uses WebSockets to create a seamless conversational experience in English, German, and Spanish. It processes your speech locally, generates AI responses locally, and synthesizes human-like voices locally. 



### ✨ Key Features
* **True Interruption:** If the AI misunderstands you or talks too much, just start speaking. The system detects your voice instantly (sensitivity: 1 syllable) and cuts off the AI's audio stream.
* **Live Ephemeral Transcript:** Watch your conversation happen in real-time on the UI. For maximum privacy, there is no database—the transcript vanishes forever the second you refresh the page.
* **Dynamic Speed Control:** Native speakers talk fast. Users can adjust the AI's speech speed from 0.5x to 1.5x on the fly to practice listening comprehension.
* **Mobile-Ready & Secure:** Includes an integrated Ngrok tunnel within the Docker stack, instantly providing a secure `https://` endpoint to bypass strict iOS/Android microphone security policies.
* **100% Private:** No API keys for cloud AI. The "brain", "ears", and "mouth" all run entirely on your own hardware.

### 🧠 Tech Stack
* **LLM (Brain):** `llama3.2:1b` via [Ollama](https://ollama.com/)
* **STT (Ears):** [Vosk](https://alphacephei.com/vosk/) (Offline Speech Recognition)
* **TTS (Mouth):** [Piper](https://github.com/rhasspy/piper) (Offline High-Fidelity Voice Generation)
* **Backend:** Python, FastAPI, WebSockets
* **Frontend:** Vanilla HTML/JS, Web Audio API
* **Infrastructure:** Docker Compose, Ngrok

---

## 🚀 Quick Start Guide

### Prerequisites
1. **Docker Desktop** installed and running.
2. **Python 3.10+** installed on your host machine (only needed for the setup script).
3. A free [Ngrok](https://ngrok.com/) Authtoken.

### Installation

**1. Clone the repository:**
```bash
git clone [https://github.com/cankucukyilmaz/polyglot-tutor.git](https://github.com/cankucukyilmaz/polyglot-tutor.git)
cd polyglot-tutor