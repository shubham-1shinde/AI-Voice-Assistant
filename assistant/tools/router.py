from typing import Callable

from . import browser, vscode, windows_ctl, whatsapp, media, system_info

TOOLS: dict[str, Callable] = {
    # browser
    "open_chrome": browser.open_chrome,
    "open_website": browser.open_website,
    "open_multiple_tabs": browser.open_multiple_tabs,
    "search_google": browser.search_google,
    "search_youtube": browser.search_youtube,
    "close_active_tab": browser.close_active_tab,
    "refresh_tab": browser.refresh_tab,
    "switch_tab": browser.switch_tab,
    # vscode / git
    "open_vscode": vscode.open_vscode,
    "open_project": vscode.open_project,
    "open_folder_vscode": vscode.open_folder,
    "open_recent_workspace": vscode.open_recent_workspace,
    "run_terminal_command": vscode.run_terminal_command,
    "git_status": vscode.git_status,
    "git_commit": vscode.git_commit,
    "git_push": vscode.git_push,
    "git_pull": vscode.git_pull,
    "git_create_branch": vscode.git_create_branch,
    "git_checkout_branch": vscode.git_checkout_branch,
    "git_merge_branch": vscode.git_merge_branch,
    # windows
    "open_app": windows_ctl.open_app,
    "close_app": windows_ctl.close_app,
    "open_folder": windows_ctl.open_folder,
    "lock_pc": windows_ctl.lock_pc,
    "shutdown_pc": windows_ctl.shutdown_pc,
    "restart_pc": windows_ctl.restart_pc,
    "sleep_pc": windows_ctl.sleep_pc,
    "set_volume": windows_ctl.set_volume,
    "set_brightness": windows_ctl.set_brightness,
    "take_screenshot": windows_ctl.take_screenshot,
    "get_clipboard": windows_ctl.get_clipboard,
    "set_clipboard": windows_ctl.set_clipboard,
    "search_files": windows_ctl.search_files,
    "focus_window": windows_ctl.focus_window,
    # whatsapp
    "open_whatsapp": whatsapp.open_whatsapp,
    "send_whatsapp_message": whatsapp.send_message,
    "call_contact": whatsapp.call_contact,
    "video_call_contact": whatsapp.video_call_contact,
    "search_whatsapp_chats": whatsapp.search_chats,
    "open_whatsapp_group": whatsapp.open_group,
    # media
    "play_song": media.play_song,
    "pause_media": media.pause,
    "resume_media": media.resume,
    "next_track": media.next_track,
    "previous_track": media.previous_track,
    "increase_volume": media.increase_volume,
    "mute_media": media.mute,
    # system
    "battery_status": system_info.battery,
    "current_time": system_info.current_time,
    "weather": system_info.weather,
    "cpu_usage": system_info.cpu_usage,
    "ram_usage": system_info.ram_usage,
    "disk_usage": system_info.disk_usage,
    "internet_status": system_info.internet_status,
    "network_speed": system_info.network_speed,
    "current_ip": system_info.current_ip,
}


def execute(tool_name: str, args: dict) -> str:
    fn = TOOLS.get(tool_name)
    if not fn:
        return f"Unknown command: {tool_name}."
    try:
        return fn(**args) if args else fn()
    except TypeError as exc:
        return f"Bad arguments for {tool_name}: {exc}"
    except Exception as exc:
        return f"Error running {tool_name}: {exc}"


def tool_names() -> list[str]:
    return list(TOOLS.keys())
