# 🌍 Polyglot AI Tutor (Live Mode)

A real-time, interruptible, voice-based AI language tutor running entirely offline. 

This project uses WebSockets to create a seamless conversational experience in English, German, and Spanish. It features **true interruption**: if the AI misunderstands you, just start speaking again, and it will instantly cut itself off and listen—just like an advanced voice assistant.

### 🧠 How It Works
* **Brain (LLM):** Local `llama3.2:1b` via [Ollama](https://ollama.com/)
* **Ears (STT):** [Vosk](https://alphacephei.com/vosk/) for real-time, offline speech recognition.
* **Mouth (TTS):** [Piper](https://github.com/rhasspy/piper) for high-fidelity, offline voice generation.
* **Architecture:** Python/FastAPI backend with a vanilla JavaScript/Web Audio API frontend, fully containerized in Docker.

---

## 🚀 Quick Start Guide

### Prerequisites
1. **Docker Desktop** installed and running.
2. **Python 3.10+** installed on your host machine (only needed for the one-time model download script).

### Installation
**1. Clone the repository:**
```bash
git clone [https://github.com/cankucukyilmaz/polyglot_language_tutor](https://github.com/cankucukyilmaz/polyglot_language_tutor)
cd polyglot-tutor