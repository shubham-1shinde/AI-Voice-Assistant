import subprocess
import time
import datetime

import pyautogui
import pywhatkit

from assistant.config import cfg
from assistant.memory import memory

WHATSAPP_EXE = "whatsapp"


def open_whatsapp() -> str:
    subprocess.Popen(f"start {WHATSAPP_EXE}:", shell=True)
    time.sleep(3)
    return "Opening WhatsApp."


def send_message(contact: str, message: str) -> str:
    try:
        pywhatkit.sendwhatmsg_instantly(
            phone_no=memory.get_entity("contact", contact) or contact,
            message=message,
            wait_time=cfg.whatsapp_wait_secs,
            tab_close=True,
        )
        memory.remember_entity("contact", contact, contact)
        return f"WhatsApp message sent to {contact}."
    except Exception as exc:
        return f"Failed to send message: {exc}"


def call_contact(contact: str) -> str:
    open_whatsapp()
    time.sleep(2)
    pyautogui.hotkey("ctrl", "f")
    pyautogui.typewrite(contact, interval=0.05)
    time.sleep(1)
    pyautogui.press("enter")
    return f"Calling {contact}."


def video_call_contact(contact: str) -> str:
    open_whatsapp()
    time.sleep(2)
    pyautogui.hotkey("ctrl", "f")
    pyautogui.typewrite(contact, interval=0.05)
    time.sleep(1)
    pyautogui.press("enter")
    return f"Video calling {contact}."


def search_chats(query: str) -> str:
    open_whatsapp()
    time.sleep(2)
    pyautogui.hotkey("ctrl", "f")
    pyautogui.typewrite(query, interval=0.05)
    return f"Searching chats for {query}."


def open_group(name: str) -> str:
    return search_chats(name)
