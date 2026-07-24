import logging
import random
import os
import time
from logging.handlers import RotatingFileHandler

from assistant.config import cfg
from assistant.voice import WakeWordDetector, SpeechToText, TextToSpeech
from assistant.agents import run_task


def setup_logging() -> logging.Logger:
    os.makedirs(os.path.dirname(cfg.log_path) or ".", exist_ok=True)

    logger = logging.getLogger("jarvis")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            cfg.log_path,
            maxBytes=1_000_000,
            backupCount=3
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)

    return logger


def main() -> None:
    logger = setup_logging()

    print("\n--- Initializing Jarvis Core Components ---")

    wake = WakeWordDetector()
    stt = SpeechToText()
    tts = TextToSpeech()

    print("All modules loaded successfully.\n")

    print("Jarvis is sleeping. Say 'Hey Jarvis' to wake me.\n")

    while True:
        try:
            # Wait for wake word
            wake.wait_for_wake()

            print("\n[Wake Word Detected!]")
            logger.info("Wake word detected")

            GREETINGS = [
                f"Welcome back, {cfg.owner_name}. How can I help you?",
                f"Hello {cfg.owner_name}. What are we building today?",
                f"Good to see you, {cfg.owner_name}.",
                f"Ready when you are, {cfg.owner_name}.",
                f"Hi {cfg.owner_name}. What can I do for you today?"
            ]
            greeting = random.choice(GREETINGS)
            tts.speak(greeting)

            # Stay awake for 2 minutes
            awake_timeout = 120
            awake_until = time.time() + awake_timeout

            while time.time() < awake_until:

                print("\nListening...")
                text = stt.listen_and_transcribe()

                # Nothing heard
                if not text:
                    continue

                # Reset timer after every valid command
                awake_until = time.time() + awake_timeout

                print(f"You: {text}")
                logger.info(f"User: {text}")

                print("Thinking...")

                result = run_task(text)

                if not result:
                    result = "Done."

                print(f"Jarvis: {result}")
                logger.info(f"Jarvis: {result}")

                tts.speak(result)

            print("\nNo activity for 2 minutes.")
            tts.speak("Going back to sleep.")

            print("\nWaiting for 'Hey Jarvis'...\n")

        except KeyboardInterrupt:
            print("\nStopping Jarvis...")
            break

        except Exception as exc:
            print(f"\nError: {exc}")
            logger.exception("Main loop error")

            try:
                tts.speak("Something went wrong.")
            except Exception:
                pass

    wake.close()
    print("Jarvis stopped.")


if __name__ == "__main__":
    main()