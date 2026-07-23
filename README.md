# Jarvis

Offline-first voice assistant for Windows 11.

## Setup

1. `python -m venv venv && venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. Install [Ollama](https://ollama.com) and run `ollama pull llama3.1`
4. Download a Piper voice model into `models/piper/` (e.g. `en_US-amy-medium.onnx` + `.json`)
5. Copy `.env.example` to `.env` and edit paths
6. `python main.py`

## Say

"Wake up Jarvis" → then speak your command.

## Structure

```
assistant/
  voice/    wake word, STT, TTS
  agents/   LLM planner + LangGraph orchestration
  tools/    browser, vscode/git, windows, whatsapp, media, system
  memory/   SQLite conversation + entity memory
  config/   settings from .env
main.py
```

## Notes

- WhatsApp features require WhatsApp Desktop installed and logged in.
- Git tools operate on the last opened project unless a project name is given.
- Volume control needs `pycaw`; brightness needs a laptop panel that supports DDC/WMI.
