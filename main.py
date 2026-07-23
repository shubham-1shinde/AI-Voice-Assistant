import logging
import os
from logging.handlers import RotatingFileHandler

from assistant.config import cfg
from assistant.voice import WakeWordDetector, SpeechToText, TextToSpeech
from assistant.agents import run_task


def setup_logging() -> logging.Logger:
    os.makedirs(os.path.dirname(cfg.log_path) or ".", exist_ok=True)
    logger = logging.getLogger("jarvis")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(cfg.log_path, maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def main() -> None:
    logger = setup_logging()
    
    print("\n--- Initializing Jarvis Core Components ---")
    wake = WakeWordDetector()
    stt = SpeechToText()
    tts = TextToSpeech()
    print("✅ All modules loaded successfully.\n")

    print(f"Jarvis idle. Say 'Hey Jarvis' to wake...")
    
    while True:
        try:
            wake.wait_for_wake()
            print("\n[Wake Word Detected!]")
            logger.info("Wake word detected")
            
            print("🔊 Speaking: 'Yes?'")
            tts.speak("Yes?")

            while True:
                print("🎙️ Listening for user command...")
                text = stt.listen_and_transcribe()
                
                if not text:
                    print("⚠️ No audio detected / Speech-to-Text returned empty.")
                    print("🔊 Speaking: 'I didn't catch that.'")
                    tts.speak("I didn't catch that.")
                    break

                print(f"👤 User: {text}")
                logger.info(f"User: {text}")

                print("🤖 Processing task with Agent...")
                result = run_task(text)
                
                print(f"🤖 Jarvis: {result}")
                logger.info(f"Jarvis: {result}")

                print("🔊 Speaking response...")
                tts.speak(result)

                if result and result.endswith("?"):
                    print("❓ Response ends with a question, listening for follow-up...")
                    continue
                break
                
            print("\nReturning to idle mode. Say 'Hey Jarvis' to wake...")
            
        except KeyboardInterrupt:
            print("\nExiting Jarvis cleanly...")
            break
        except Exception as exc:
            print(f"❌ Error encountered: {exc}")
            logger.exception("Error in main loop")
            tts.speak("Something went wrong. Returning to idle.")

    wake.close()
    print("Jarvis stopped.")


if __name__ == "__main__":
    main()