import ctypes
import os
import subprocess

from assistant.config import cfg
from assistant.memory import memory


def _normalize(text: str) -> str:
    return text.lower().replace(" ", "").replace("-", "").replace("_", "")


def _get_active_vscode_project() -> str | None:
    """
    Inspects open Windows titles to find the currently active/focused VS Code workspace.
    Returns the absolute path to the project if found under cfg.projects_root.
    """
    try:
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)
        )
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        titles = []

        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buff, length + 1)
                    titles.append(buff.value)
            return True

        EnumWindows(EnumWindowsProc(foreach_window), 0)

        # Look for titles matching "... - Visual Studio Code"
        for title in titles:
            if "Visual Studio Code" in title:
                parts = title.split(" - Visual Studio Code")[0].split(" - ")
                # The folder/workspace name is typically the last part before "Visual Studio Code"
                possible_folder = parts[-1].strip()
                matched_path = _find_project(possible_folder)
                if matched_path:
                    return matched_path
    except Exception:
        pass

    return None


def _find_project(name: str) -> str | None:
    """
    Finds project directory matching target name.
    1. Checks if matched directory directly contains a .git folder.
    2. Checks if a subfolder inside matched directory contains a .git folder.
    3. Fallback to matched directory even if .git is absent.
    """
    if not name or not name.strip():
        return None

    if not os.path.isdir(cfg.projects_root):
        return None

    target = _normalize(name)

    # 1. Primary Pass: Look for target match where .git exists directly or in immediate subfolder
    for root, dirs, _ in os.walk(cfg.projects_root):
        for d in dirs:
            norm_dir = _normalize(d)
            if target in norm_dir or norm_dir in target:
                candidate_path = os.path.join(root, d)

                # Check if .git is directly inside the matched folder
                if os.path.exists(os.path.join(candidate_path, ".git")):
                    return candidate_path

                # Check if .git exists in a direct subfolder
                try:
                    for child in os.listdir(candidate_path):
                        child_path = os.path.join(candidate_path, child)
                        if os.path.isdir(child_path) and os.path.exists(os.path.join(child_path, ".git")):
                            return child_path
                except PermissionError:
                    continue

    # 2. Secondary Pass: Fallback to matched directory even if no .git is found
    for root, dirs, _ in os.walk(cfg.projects_root):
        for d in dirs:
            norm_dir = _normalize(d)
            if target in norm_dir or norm_dir in target:
                return os.path.join(root, d)

    return None


def _launch_vscode(target_path: str = None) -> None:
    """Launches VS Code with fallback to default Windows install path."""
    cmd = [cfg.vscode_path]
    if target_path:
        cmd.append(target_path)

    try:
        subprocess.Popen(cmd)
    except FileNotFoundError:
        fallback_exe = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
        if os.path.exists(fallback_exe):
            fallback_cmd = [fallback_exe]
            if target_path:
                fallback_cmd.append(target_path)
            subprocess.Popen(fallback_cmd)
        else:
            raise FileNotFoundError("Could not locate VS Code executable.")


def open_vscode(name: str = "", *args, **kwargs) -> str:
    project_name = (
        name
        or kwargs.get("name")
        or kwargs.get("project")
        or kwargs.get("project_name")
        or kwargs.get("folder")
        or kwargs.get("folder_name")
        or kwargs.get("path")
        or kwargs.get("query")
        or ""
    )

    clean_name = (
        project_name.lower()
        .replace("folder", "")
        .replace("project", "")
        .replace("on vs code", "")
        .replace("in vs code", "")
        .replace("vs code", "")
        .replace("open", "")
        .strip()
    )

    if clean_name:
        project_path = _find_project(clean_name) or _find_project(project_name)

        if project_path:
            _launch_vscode(project_path)
            memory.remember_entity("project", clean_name, project_path)
            return f"Opening project {clean_name}."

    _launch_vscode()
    return "Opening VS Code."


def open_project(name: str = "", *args, **kwargs) -> str:
    project_name = (
        name
        or kwargs.get("name")
        or kwargs.get("project")
        or kwargs.get("project_name")
        or kwargs.get("folder")
        or kwargs.get("folder_name")
        or kwargs.get("path")
        or ""
    )

    if not project_name:
        return "Please tell me which project to open."

    project_path = _find_project(project_name)

    if not project_path:
        return f"Project '{project_name}' not found."

    _launch_vscode(project_path)
    memory.remember_entity("project", project_name, project_path)

    return f"Opening project {project_name}."


def open_folder(path: str = "", *args, **kwargs) -> str:
    folder = (
        path
        or kwargs.get("path")
        or kwargs.get("folder")
        or kwargs.get("folder_name")
        or kwargs.get("name")
        or ""
    )

    if not folder:
        return "Please tell me which folder to open."

    if os.path.isdir(folder):
        _launch_vscode(folder)
        memory.remember_entity("project", os.path.basename(folder), folder)
        return f"Opening folder {folder}."

    project = _find_project(folder)

    if project:
        _launch_vscode(project)
        memory.remember_entity("project", folder, project)
        return f"Opening project {folder}."

    return f"Folder '{folder}' not found."


def open_recent_workspace(*args, **kwargs):
    _launch_vscode("--reuse-window")
    return "Opening recent workspace."


def _run_git(cwd: str, *args: str):
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    return result.returncode == 0, (result.stdout or result.stderr).strip()


def _resolve_project_path(name=None):
    """
    1. Explicit name supplied -> look up that project.
    2. Active VS Code Window -> auto-detect project open in VS Code window title.
    3. Last active project saved in memory.
    4. Current working directory fallback.
    """
    if name:
        path = _find_project(name)
        if path:
            return path

    # Check active open VS Code window title
    active_vscode_path = _get_active_vscode_project()
    if active_vscode_path:
        # Update memory to stay synced
        memory.remember_entity("project", os.path.basename(active_vscode_path), active_vscode_path)
        return active_vscode_path

    # Fallback to last remembered entity
    last_active = memory.last_entity("project")
    if last_active and os.path.isdir(str(last_active)):
        return str(last_active)

    return os.getcwd()


def git_status(project=None, *args, **kwargs):
    path = _resolve_project_path(project)

    if not path or not os.path.exists(os.path.join(path, ".git")):
        return f"No Git repository found in {path}."

    ok, out = _run_git(path, "status", "--short")
    return "Working tree clean." if ok and not out else out


def git_commit(message=None, project=None, *args, **kwargs):
    path = _resolve_project_path(project)

    if not path or not os.path.exists(os.path.join(path, ".git")):
        return "No active Git repository."

    extracted_msg = (
        message
        or kwargs.get("message")
        or kwargs.get("msg")
        or kwargs.get("m")
        or kwargs.get("commit_message")
        or kwargs.get("text")
        or (args[0] if args and isinstance(args[0], str) else None)
    )

    clean_msg = None
    if extracted_msg and isinstance(extracted_msg, str):
        clean_msg = (
            extracted_msg.lower()
            .replace("commit changes with message", "")
            .replace("commit with message", "")
            .replace("commit message", "")
            .replace("commit changes", "")
            .replace("commit", "")
            .strip()
        )

    if not clean_msg:
        return "What should be the commit message?"

    _run_git(path, "add", ".")

    ok, out = _run_git(path, "commit", "-m", clean_msg)
    return f"Changes committed with message: '{clean_msg}'" if ok else out


def git_push(project=None, *args, **kwargs):
    path = _resolve_project_path(project)

    if not path or not os.path.exists(os.path.join(path, ".git")):
        return f"No Git repository found in project folder: {path}"

    _, remote_url = _run_git(path, "config", "--get", "remote.origin.url")

    ok, out = _run_git(path, "push")

    if ok:
        repo_name = remote_url.split("/")[-1].replace(".git", "") if remote_url else "remote"
        return f"Successfully pushed changes to {repo_name}."

    if "has no upstream branch" in out or "autoSetupRemote" in out:
        _, branch_name = _run_git(path, "rev-parse", "--abbrev-ref", "HEAD")
        if branch_name:
            ok_upstream, out_upstream = _run_git(path, "push", "--set-upstream", "origin", branch_name)
            if ok_upstream:
                return f"Pushed branch '{branch_name}' to repository."
            return out_upstream

    return out


def git_pull(project=None, *args, **kwargs):
    path = _resolve_project_path(project)

    if not path or not os.path.exists(os.path.join(path, ".git")):
        return "No active Git repository."

    ok, out = _run_git(path, "pull")
    return "Pulled latest changes." if ok else out


def git_create_branch(branch_name=None, project=None, *args, **kwargs):
    branch = branch_name or kwargs.get("branch") or kwargs.get("name")
    if not branch:
        return "Please specify a branch name."

    path = _resolve_project_path(project)
    if not path:
        return "No active project."

    ok, out = _run_git(path, "checkout", "-b", branch)
    return f"Created and switched to branch {branch}." if ok else out


def git_checkout_branch(branch_name=None, project=None, *args, **kwargs):
    branch = branch_name or kwargs.get("branch") or kwargs.get("name")
    if not branch:
        return "Please specify a branch name."

    path = _resolve_project_path(project)
    if not path:
        return "No active project."

    ok, out = _run_git(path, "checkout", branch)
    return f"Switched to branch {branch}." if ok else out


def git_merge_branch(branch_name=None, project=None, *args, **kwargs):
    branch = branch_name or kwargs.get("branch") or kwargs.get("name")
    if not branch:
        return "Please specify a branch to merge."

    path = _resolve_project_path(project)
    if not path:
        return "No active project."

    ok, out = _run_git(path, "merge", branch)
    return f"Merged branch {branch}." if ok else out


def run_terminal_command(command="", project=None, *args, **kwargs):
    path = _resolve_project_path(project) or os.getcwd()

    result = subprocess.run(
        command,
        cwd=path,
        shell=True,
        capture_output=True,
        text=True,
    )

    return (result.stdout or result.stderr or "Done.")[:300]

def git_init_and_push_new_repo(repo_name=None, private=False, *args, **kwargs):
    """
    Automates whole workflow for a new local project:
    1. Resolves active project path
    2. Initializes Git local repository & cleans old remotes if present
    3. Stages and commits all files
    4. Sets main branch
    5. Creates remote GitHub repository matching folder name
    6. Links remote origin and pushes code
    """
    path = _resolve_project_path()

    if not path or not os.path.exists(path):
        return "No valid project folder detected."

    # Use project folder name as default repository name
    folder_name = os.path.basename(path.rstrip(os.sep))
    
    # Clean repo name (GitHub safe: lowercase, dashes only)
    clean_repo_name = (
        folder_name.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .strip()
    )

    # 1. Initialize local Git
    _run_git(path, "init")

    # Remove stale origin remote if it already exists to prevent "Unable to add remote origin" error
    _run_git(path, "remote", "remove", "origin")

    # 2. Stage & Commit
    _run_git(path, "add", ".")
    _run_git(path, "commit", "-m", "initial commit")

    # 3. Ensure branch name is main
    _run_git(path, "branch", "-M", "main")

    # 4. Create GitHub repository using GitHub CLI
    visibility = "--private" if private or kwargs.get("private") else "--public"
    cmd = f"gh repo create {clean_repo_name} {visibility} --source=. --remote=origin --push"

    result = subprocess.run(
        cmd,
        cwd=path,
        shell=True,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return f"Successfully created GitHub repo '{clean_repo_name}' and pushed initial code!"

    error_msg = (result.stderr or result.stdout).strip()

    # Fallback: If repo already exists on GitHub, link and force push
    if "already exists" in error_msg.lower():
        # Get username from gh
        _, username = _run_git(path, "gh", "api", "user", "-q", ".login")
        user = username if username else "shubham-1shinde"
        remote_url = f"https://github.com/{user}/{clean_repo_name}.git"
        
        _run_git(path, "remote", "add", "origin", remote_url)
        ok, push_out = _run_git(path, "push", "-u", "origin", "main", "-f")
        if ok:
            return f"Linked and pushed code to existing repository '{clean_repo_name}'."
        return f"Failed to push to existing repo: {push_out[:100]}"

    return f"Failed to automate GitHub creation: {error_msg[:150]}"