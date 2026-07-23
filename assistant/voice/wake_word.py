import numpy as np
import pyaudio
from openwakeword.model import Model

from assistant.config import cfg

CHUNK = 1280
RATE = 16000


class WakeWordDetector:
    def __init__(self, model_name: str = cfg.wake_word_model, threshold: float = 0.5):
        # Added inference_framework="onnx" to bypass TFLite dependencies
        self.model = Model(
            wakeword_models=[model_name],
            inference_framework="onnx"
        )
        self.threshold = threshold
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

    def wait_for_wake(self) -> None:
        while True:
            audio = np.frombuffer(self.stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
            scores = self.model.predict(audio)
            if any(s >= self.threshold for s in scores.values()):
                self.model.reset()
                return

    def close(self) -> None:
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()