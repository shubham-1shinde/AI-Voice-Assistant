import os
import subprocess
import ctypes
import datetime

import psutil
import pyautogui
import pygetwindow as gw

APP_MAP = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "explorer": "explorer.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
}


def open_app(name: str) -> str:
    exe = APP_MAP.get(name.lower(), name)
    subprocess.Popen(exe, shell=True)
    return f"Opening {name}."


def close_app(name: str) -> str:
    exe = APP_MAP.get(name.lower(), name)
    for proc in psutil.process_iter(["name"]):
        if exe.lower() in (proc.info["name"] or "").lower():
            proc.terminate()
    return f"Closed {name}."


def open_folder(path: str) -> str:
    if not os.path.isdir(path):
        return f"Folder {path} not found."
    os.startfile(path)
    return "Opening folder."


def lock_pc() -> str:
    ctypes.windll.user32.LockWorkStation()
    return "Locking PC."


def shutdown_pc(delay: int = 5) -> str:
    subprocess.run(["shutdown", "/s", "/t", str(delay)])
    return "Shutting down."


def restart_pc(delay: int = 5) -> str:
    subprocess.run(["shutdown", "/r", "/t", str(delay)])
    return "Restarting."


def sleep_pc() -> str:
    ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
    return "Sleeping."


def set_volume(level: int) -> str:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(max(0, min(level, 100)) / 100, None)
    return f"Volume set to {level}."


def set_brightness(level: int) -> str:
    import screen_brightness_control as sbc

    sbc.set_brightness(max(0, min(level, 100)))
    return f"Brightness set to {level}."


def take_screenshot(save_dir: str = "screenshots") -> str:
    os.makedirs(save_dir, exist_ok=True)
    fname = os.path.join(save_dir, f"shot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png")
    pyautogui.screenshot().save(fname)
    return "Screenshot taken."


def get_clipboard() -> str:
    import pyperclip

    return pyperclip.paste()


def set_clipboard(text: str) -> str:
    import pyperclip

    pyperclip.copy(text)
    return "Copied to clipboard."


def search_files(name: str, root: str = "C:\\") -> str:
    matches = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if name.lower() in f.lower():
                matches.append(os.path.join(dirpath, f))
                if len(matches) >= 5:
                    return "; ".join(matches)
    return "; ".join(matches) if matches else "No files found."


def focus_window(title: str) -> str:
    wins = gw.getWindowsWithTitle(title)
    if not wins:
        return f"Window {title} not found."
    wins[0].activate()
    return f"Switched to {title}."
