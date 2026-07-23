import io
import wave

import numpy as np
import pyaudio
from faster_whisper import WhisperModel

from assistant.config import cfg

RATE = 16000
CHUNK = 1024
SILENCE_RMS_THRESHOLD = 300


class SpeechToText:
    def __init__(self):
        self.model = WhisperModel(cfg.stt_model, device=cfg.stt_device, compute_type="int8")
        self.pa = pyaudio.PyAudio()

    def listen_and_transcribe(self) -> str:
        frames = self._record_until_silence()
        audio = np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32) / 32768.0
        segments, _ = self.model.transcribe(audio, language="en")
        return " ".join(seg.text.strip() for seg in segments).strip()

    def _record_until_silence(self) -> list[bytes]:
        stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames: list[bytes] = []
        silence_chunks = 0
        max_silence_chunks = int(cfg.silence_timeout * RATE / CHUNK)
        max_total_chunks = int(cfg.listen_timeout * 4 * RATE / CHUNK)
        spoke = False
        for _ in range(max_total_chunks):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            rms = np.sqrt(np.mean(np.frombuffer(data, dtype=np.int16).astype(np.float32) ** 2))
            if rms > SILENCE_RMS_THRESHOLD:
                spoke = True
                silence_chunks = 0
            elif spoke:
                silence_chunks += 1
                if silence_chunks >= max_silence_chunks:
                    break
        stream.stop_stream()
        stream.close()
        return frames
