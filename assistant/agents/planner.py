import json
import re

from langchain_ollama import ChatOllama

from assistant.config import cfg
from assistant.tools import tool_names

SYSTEM_PROMPT = """You are Jarvis's command router. Given the user's request and recent \
conversation, output ONLY a JSON object: {{"tool": "<tool_name>", "args": {{...}}, "speak": "<short reply>"}}.
Pick tool from this list: {tools}

Rules for args:
- For opening projects/folders in VS Code or app commands, put the target name in "name", "project", or "path" keys inside args.
- If opening a project in VS Code (e.g. "open GST assistant in vs code"), pick tool "open_vscode" or "open_project" with "args": {{"name": "<project_name>"}}.
- If a required argument like a commit message is missing, put "" for it.
- If the request is just conversation with no matching tool, use "tool": "chat" and put the natural reply in "speak".
- Resolve pronouns like "it"/"them" using conversation history.
- Respond under 12 words in "speak". No markdown, JSON only."""


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