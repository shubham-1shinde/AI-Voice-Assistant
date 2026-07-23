import os
import subprocess

from assistant.config import cfg
from assistant.memory import memory


def _find_project(name: str) -> str | None:
    if not name:
        return None
    name = name.lower().replace(" ", "").replace("-", "")
    if not os.path.isdir(cfg.projects_root):
        return None
    for entry in os.listdir(cfg.projects_root):
        if name in entry.lower().replace(" ", "").replace("-", ""):
            return os.path.join(cfg.projects_root, entry)
    return None


def open_vscode(*args, **kwargs) -> str:
    """Safely handles open_vscode even if LLM passes extra args or string kwargs."""
    subprocess.Popen([cfg.vscode_path, "."], shell=True)
    return "Opening VS Code."


def open_project(name: str = "", *args, **kwargs) -> str:
    """Flexibly handles project names passed positionally or via kwargs."""
    proj_name = name or kwargs.get("name") or kwargs.get("project") or kwargs.get("project_name") or ""
    path = _find_project(proj_name)
    if not path:
        return f"Project '{proj_name}' not found."
    subprocess.Popen([cfg.vscode_path, path], shell=True)
    memory.remember_entity("project", proj_name, path)
    return f"Opening project {proj_name}."


def open_folder(path: str = "", *args, **kwargs) -> str:
    """Flexibly handles 'path', 'folder_path', or project folder search."""
    target_path = (
        path 
        or kwargs.get("path") 
        or kwargs.get("folder_path") 
        or kwargs.get("folder") 
        or "."
    )
    
    # Check if target_path exists directly; if not, try locating it inside projects_root
    if not os.path.isdir(target_path):
        resolved_path = _find_project(target_path)
        if resolved_path:
            target_path = resolved_path
        else:
            return f"Folder or project '{target_path}' not found."

    subprocess.Popen([cfg.vscode_path, target_path], shell=True)
    return f"Opening folder {target_path}."


def open_recent_workspace(*args, **kwargs) -> str:
    subprocess.Popen([cfg.vscode_path, "--reuse-window"], shell=True)
    return "Opening recent workspace."


def _run_git(cwd: str, *args: str) -> tuple[bool, str]:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    ok = result.returncode == 0
    return ok, (result.stdout or result.stderr).strip()


def _resolve_project_path(name: str | None) -> str | None:
    if name:
        return _find_project(name)
    return memory.last_entity("project")


def git_status(project: str | None = None, *args, **kwargs) -> str:
    proj_name = project or kwargs.get("project")
    path = _resolve_project_path(proj_name)
    if not path:
        return "No active project."
    ok, out = _run_git(path, "status", "--short")
    return "Clean." if ok and not out else out[:200]


def git_commit(message: str | None = None, project: str | None = None, *args, **kwargs) -> str:
    commit_msg = message or kwargs.get("message")
    proj_name = project or kwargs.get("project")
    path = _resolve_project_path(proj_name)
    if not path:
        return "No active project."
    if not commit_msg:
        return "NEED_COMMIT_MESSAGE"
    _run_git(path, "add", ".")
    ok, out = _run_git(path, "commit", "-m", commit_msg)
    return "Committed." if ok else f"Commit failed: {out[:100]}"


def git_push(project: str | None = None, *args, **kwargs) -> str:
    proj_name = project or kwargs.get("project")
    path = _resolve_project_path(proj_name)
    if not path:
        return "No active project."
    ok, out = _run_git(path, "push")
    return "Git push completed." if ok else f"Push failed: {out[:100]}"


def git_pull(project: str | None = None, *args, **kwargs) -> str:
    proj_name = project or kwargs.get("project")
    path = _resolve_project_path(proj_name)
    if not path:
        return "No active project."
    ok, out = _run_git(path, "pull")
    return "Pulled latest." if ok else f"Pull failed: {out[:100]}"


def git_create_branch(name: str = "", project: str | None = None, *args, **kwargs) -> str:
    branch_name = name or kwargs.get("name") or ""
    proj_name = project or kwargs.get("project")
    path = _resolve_project_path(proj_name)
    if not path:
        return "No active project."
    ok, out = _run_git(path, "checkout", "-b", branch_name)
    return f"Created branch {branch_name}." if ok else out[:100]


def git_checkout_branch(name: str = "", project: str | None = None, *args, **kwargs) -> str:
    branch_name = name or kwargs.get("name") or ""
    proj_name = project or kwargs.get("project")
    path = _resolve_project_path(proj_name)
    if not path:
        return "No active project."
    ok, out = _run_git(path, "checkout", branch_name)
    return f"Switched to {branch_name}." if ok else out[:100]


def git_merge_branch(name: str = "", project: str | None = None, *args, **kwargs) -> str:
    branch_name = name or kwargs.get("name") or ""
    proj_name = project or kwargs.get("project")
    path = _resolve_project_path(proj_name)
    if not path:
        return "No active project."
    ok, out = _run_git(path, "merge", branch_name)
    return f"Merged {branch_name}." if ok else out[:100]


def run_terminal_command(command: str = "", project: str | None = None, *args, **kwargs) -> str:
    cmd = command or kwargs.get("command") or ""
    proj_name = project or kwargs.get("project")
    path = _resolve_project_path(proj_name) or os.getcwd()
    result = subprocess.run(cmd, cwd=path, shell=True, capture_output=True, text=True)
    return (result.stdout or result.stderr or "Done.").strip()[:300]