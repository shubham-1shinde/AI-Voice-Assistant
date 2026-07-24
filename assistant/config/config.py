import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    owner_name = os.getenv("OWNER_NAME", "User")
    owner_full_name = os.getenv("OWNER_FULL_NAME", "User")
    wake_word: str = os.getenv("WAKE_WORD", "jarvis")
    wake_word_model: str = os.getenv("WAKE_WORD_MODEL", "hey_jarvis")
    stt_model: str = os.getenv("STT_MODEL", "base")
    stt_device: str = os.getenv("STT_DEVICE", "cpu")
    tts_model_path: str = os.getenv("TTS_MODEL_PATH", "models/piper/en_US-amy-medium.onnx")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    db_path: str = os.getenv("DB_PATH", "memory/jarvis.db")
    log_path: str = os.getenv("LOG_PATH", "logs/jarvis.log")
    vscode_path: str = os.getenv("VSCODE_PATH", "code")
    projects_root: str = os.getenv("PROJECTS_ROOT", os.path.expanduser("~/Projects"))
    chrome_path: str = os.getenv("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    whatsapp_wait_secs: int = int(os.getenv("WHATSAPP_WAIT_SECS", "15"))
    listen_timeout: int = int(os.getenv("LISTEN_TIMEOUT", "8"))
    silence_timeout: int = int(os.getenv("SILENCE_TIMEOUT", "2"))


cfg = Config()
