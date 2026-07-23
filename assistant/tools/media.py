import subprocess
import urllib.parse

import pywhatkit
import keyboard

from assistant.config import cfg


def play_song(query: str) -> str:
    try:
        pywhatkit.playonyt(query)
        return f"Playing {query}."
    except Exception:
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        subprocess.Popen([cfg.chrome_path, url])
        return f"Searching {query} on YouTube."


def pause() -> str:
    keyboard.send("play/pause media")
    return "Paused."


def resume() -> str:
    keyboard.send("play/pause media")
    return "Resumed."


def next_track() -> str:
    keyboard.send("next track")
    return "Next track."


def previous_track() -> str:
    keyboard.send("previous track")
    return "Previous track."


def increase_volume() -> str:
    keyboard.send("volume up")
    return "Volume up."


def mute() -> str:
    keyboard.send("volume mute")
    return "Muted."
