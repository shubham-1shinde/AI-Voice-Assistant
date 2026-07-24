# import subprocess
# import urllib.parse

# import keyboard
# import pywhatkit

# from assistant.config import cfg


# def play_song(query: str) -> str:
#     try:
#         pywhatkit.playonyt(query)
#         return f"Playing {query}."
#     except Exception:
#         url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
#         subprocess.Popen([cfg.chrome_path, url])
#         return f"Searching {query} on YouTube."


# def pause() -> str:
#     keyboard.send("play/pause media")
#     return "Paused."


# def resume() -> str:
#     keyboard.send("play/pause media")
#     return "Resumed."


# def next_track() -> str:
#     keyboard.send("next track")
#     return "Next track."


# def previous_track() -> str:
#     keyboard.send("previous track")
#     return "Previous track."


# def increase_volume() -> str:
#     keyboard.send("volume up")
#     return "Volume up."


# def mute() -> str:
#     keyboard.send("volume mute")
#     return "Muted."

import os
import subprocess
import urllib.parse
import webbrowser
import keyboard

from assistant.config import cfg


def play_song(*args, **kwargs) -> str:
    """
    Plays a song on YouTube safely, handling any parameter format:
    - play_song("khat song")
    - play_song(query="khat song")
    - play_song(name="khat song")
    - play_song({"query": "khat song"})
    """
    song_title = ""

    # 1. Check positional args
    if args:
        first = args[0]
        if isinstance(first, str):
            song_title = first
        elif isinstance(first, dict):
            song_title = (
                first.get("query")
                or first.get("name")
                or first.get("song")
                or first.get("title")
                or ""
            )

    # 2. Check keyword args if positional was empty
    if not song_title and kwargs:
        song_title = (
            kwargs.get("query")
            or kwargs.get("name")
            or kwargs.get("song")
            or kwargs.get("title")
            or kwargs.get("search")
            or ""
        )

    # 3. Default fallback
    song_title = str(song_title).strip()
    if not song_title:
        song_title = "Be Intehaan"

    encoded_query = urllib.parse.quote(song_title)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"

    try:
        if hasattr(cfg, "chrome_path") and cfg.chrome_path and os.path.exists(cfg.chrome_path):
            subprocess.Popen([cfg.chrome_path, url])
        else:
            webbrowser.open(url)
        return f"Playing '{song_title}' on YouTube."
    except Exception:
        webbrowser.open(url)
        return f"Searching '{song_title}' on YouTube."


def pause(*args, **kwargs) -> str:
    try:
        keyboard.send("play/pause media")
    except Exception:
        keyboard.send("space")
    return "Paused."


def resume(*args, **kwargs) -> str:
    try:
        keyboard.send("play/pause media")
    except Exception:
        keyboard.send("space")
    return "Resumed."


def next_track(*args, **kwargs) -> str:
    try:
        keyboard.send("next track")
    except Exception:
        keyboard.send("shift+n")
    return "Next track."


def previous_track(*args, **kwargs) -> str:
    try:
        keyboard.send("previous track")
    except Exception:
        keyboard.send("shift+p")
    return "Previous track."


def increase_volume(*args, **kwargs) -> str:
    try:
        keyboard.send("volume up")
        return "Volume up."
    except Exception as exc:
        return f"Failed to adjust volume: {exc}"


def mute(*args, **kwargs) -> str:
    try:
        keyboard.send("volume mute")
        return "Muted."
    except Exception as exc:
        return f"Failed to mute: {exc}"