import os
import wave
import time
import tempfile
import pygame
from piper.voice import PiperVoice

from assistant.config import cfg


class TextToSpeech:
    def __init__(self, model_path: str = cfg.tts_model_path):
        self.voice = PiperVoice.load(model_path)
        pygame.mixer.init()
        self.temp_wav = os.path.join(tempfile.gettempdir(), "jarvis_tts_output.wav")

    def speak(self, text: str) -> None:
        if not text or not text.strip():
            return

        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception:
            pass

        try:
            # 1. Synthesize directly using Piper's native wav synthesis method
            with wave.open(self.temp_wav, "wb") as wav_file:
                wav_file.setnchannels(1)                             # Mono
                wav_file.setsampwidth(2)                            # 16-bit PCM
                wav_file.setframerate(self.voice.config.sample_rate) # Piper sample rate
                
                # Use synthesize_wav directly
                self.voice.synthesize_wav(text, wav_file)

            # 2. Play the synthesized WAV file
            pygame.mixer.music.load(self.temp_wav)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
                
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"TTS Playback Error: {e}")

    def interrupt(self) -> None:
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except Exception:
            pass