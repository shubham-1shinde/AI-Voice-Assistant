import os
import subprocess
import webbrowser
import urllib.parse

from assistant.config import cfg
from assistant.memory import memory

SITE_MAP = {
    "github": "https://github.com",
    "chatgpt": "https://chat.openai.com",
    "gmail": "https://mail.google.com",
    "youtube": "https://youtube.com",
}


def _get_chrome_path() -> str | None:
    """Finds Chrome binary path or falls back to system path / cfg."""
    if hasattr(cfg, "chrome_path") and cfg.chrome_path and os.path.exists(cfg.chrome_path):
        return cfg.chrome_path
    
    # Common Windows Chrome paths
    default_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    for path in default_paths:
        if os.path.exists(path):
            return path
    return None


def _launch_browser(url: str | None = None, *urls: str) -> None:
    """Helper to launch Chrome or fall back to system default browser."""
    chrome_bin = _get_chrome_path()
    target_urls = [u for u in ([url] + list(urls)) if u]

    if chrome_bin:
        cmd = [chrome_bin] + target_urls if target_urls else [chrome_bin]
        subprocess.Popen(cmd)
    else:
        if target_urls:
            for u in target_urls:
                webbrowser.open(u)
        else:
            subprocess.Popen("start chrome", shell=True)


def open_chrome(*args, **kwargs) -> str:
    """Safely opens Chrome regardless of extra args passed by agent."""
    url = kwargs.get("url") or kwargs.get("name_or_url")
    if url and isinstance(url, str) and url.startswith("http"):
        _launch_browser(url)
    else:
        _launch_browser()
    return "Opening Chrome."


def open_website(name_or_url: str = "", *args, **kwargs) -> str:
    target = name_or_url or kwargs.get("url") or kwargs.get("name_or_url") or kwargs.get("name") or ""
    if not target:
        _launch_browser()
        return "Opening Chrome."

    url = target.strip().lower()
    if url in SITE_MAP:
        url = SITE_MAP[url]
    elif not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}.com"

    _launch_browser(url)
    memory.remember_entity("website", target, url)
    return f"Opening {target}."


def open_multiple_tabs(names: list[str] | str = None, *args, **kwargs) -> str:
    if isinstance(names, str):
        names = [names]
    elif not names:
        names = kwargs.get("names") or []

    urls = [
        SITE_MAP.get(n.lower(), f"https://{n}.com" if not n.startswith("http") else n)
        for n in names
    ]
    if urls:
        _launch_browser(*urls)
    return f"Opened {len(urls)} tabs."


def search_google(query: str = "", *args, **kwargs) -> str:
    q = query or kwargs.get("query") or kwargs.get("search_query") or ""
    url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
    _launch_browser(url)
    memory.remember_entity("search", q, url)
    return f"Searching Google for {q}."


def search_youtube(query: str = "", *args, **kwargs) -> str:
    q = query or kwargs.get("query") or kwargs.get("search_query") or ""
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
    _launch_browser(url)
    return f"Searching YouTube for {q}."


def close_active_tab(*args, **kwargs) -> str:
    import keyboard

    keyboard.send("ctrl+w")
    return "Closed tab."


def refresh_tab(*args, **kwargs) -> str:
    import keyboard

    keyboard.send("f5")
    return "Refreshed."


def switch_tab(direction: str = "next", *args, **kwargs) -> str:
    import keyboard

    dir_val = direction or kwargs.get("direction") or "next"
    keyboard.send("ctrl+tab" if dir_val == "next" else "ctrl+shift+tab")
    return "Switched tab."