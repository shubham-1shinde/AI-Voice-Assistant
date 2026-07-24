import json
import re

from langchain_ollama import ChatOllama

from assistant.config import cfg
from assistant.tools import tool_names

SYSTEM_PROMPT = """
You are Jarvis's command router.

Return ONLY valid JSON in this format:

{{"tool":"tool_name","args":{{}},"speak":"short reply"}}

Available tools:
{tools}

Rules:

- Open VS Code only:
  {{"tool":"open_vscode","args":{{}}}}

- Open a project/folder in VS Code:
  {{"tool":"open_project","args":{{"name":"project name"}}}}

- Open any folder:
  {{"tool":"open_folder","args":{{"path":"folder name"}}}}

- Git status:
  {{"tool":"git_status","args":{{"project":"project name"}}}}

- Commit changes:
  {{"tool":"git_commit","args":{{"project":"project name","message":"commit message"}}}}

- Push changes:
  {{"tool":"git_push","args":{{"project":"project name"}}}}

- Pull latest changes:
  {{"tool":"git_pull","args":{{"project":"project name"}}}}

- Play a song/video on YouTube:
  {{"tool":"play_song","args":{{"query":"song name"}}}}

- Open a website:
  {{"tool":"open_website","args":{{"url":"website"}}}}

- Search Google:
  {{"tool":"search_google","args":{{"query":"search text"}}}}

- WhatsApp message:
  use send_whatsapp_message.

- WhatsApp call:
  use call_contact.

- Video call:
  use video_call_contact.

- If a commit message is missing, return:
  {{"tool":"git_commit","args":{{"message":""}}}}

- Understand common speech mistakes:
  - "comments changes" = "commit changes"
  - "good status" = "git status"

- Resolve "it", "them", "that project" using recent conversation.

- If no tool matches:
  {{"tool":"chat","args":{{}},"speak":"reply"}}

Respond ONLY with JSON.
"""


class Planner:
    def __init__(self):
        self.llm = ChatOllama(model=cfg.ollama_model, base_url=cfg.ollama_host, temperature=0)

    def plan(self, user_text: str, history: list[tuple[str, str]]) -> dict:
        convo = "\n".join(f"{r}: {c}" for r, c in history[-6:])
        prompt = (
            SYSTEM_PROMPT.format(tools=", ".join(tool_names()))
            + f"\n\nConversation:\n{convo}\n\nUser: {user_text}\nJSON:"
        )
        raw = self.llm.invoke(prompt).content
        return self._parse(raw)

    @staticmethod
    def _parse(raw: str) -> dict:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return {"tool": "chat", "args": {}, "speak": raw.strip()[:200]}

        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"tool": "chat", "args": {}, "speak": "I didn't understand that."}

        # 1. Ensure basic key presence
        data.setdefault("tool", "chat")
        data.setdefault("speak", "")

        # 2. Strict type validation for 'args'
        raw_args = data.get("args")
        if isinstance(raw_args, dict):
            data["args"] = raw_args
        elif isinstance(raw_args, str) and raw_args.strip():
            # If Ollama outputs a string for args, wrap it cleanly across common key names
            clean_str = raw_args.strip()
            data["args"] = {"name": clean_str, "project": clean_str, "path": clean_str, "query": clean_str}
        else:
            data["args"] = {}

        return data