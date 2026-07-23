import datetime
import socket
import time

import psutil
import requests


def battery() -> str:
    b = psutil.sensors_battery()
    if not b:
        return "No battery detected."
    return f"Battery at {b.percent} percent{' and charging' if b.power_plugged else ''}."


def current_time() -> str:
    return f"It's {datetime.datetime.now():%I:%M %p}."


def weather(city: str = "") -> str:
    try:
        url = f"https://wttr.in/{city}?format=%C+%t" if city else "https://wttr.in/?format=%C+%t"
        r = requests.get(url, timeout=5)
        return f"Weather: {r.text.strip()}."
    except Exception:
        return "Could not fetch weather."


def cpu_usage() -> str:
    return f"CPU usage is {psutil.cpu_percent(interval=1)} percent."


def ram_usage() -> str:
    return f"RAM usage is {psutil.virtual_memory().percent} percent."


def disk_usage() -> str:
    return f"Disk usage is {psutil.disk_usage('/').percent} percent."


def internet_status() -> str:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "Internet is connected."
    except OSError:
        return "No internet connection."


def network_speed() -> str:
    s1 = psutil.net_io_counters()
    time.sleep(1)
    s2 = psutil.net_io_counters()
    down = (s2.bytes_recv - s1.bytes_recv) / 1024
    up = (s2.bytes_sent - s1.bytes_sent) / 1024
    return f"Download {down:.0f} KB/s, upload {up:.0f} KB/s."


def current_ip() -> str:
    try:
        return f"Your IP is {requests.get('https://api.ipify.org', timeout=5).text}."
    except Exception:
        return "Could not fetch IP."
