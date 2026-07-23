from typing import TypedDict

from langgraph.graph import StateGraph, END

from assistant.agents.planner import Planner
from assistant.tools import execute
from assistant.memory import memory

planner = Planner()


class JarvisState(TypedDict):
    user_text: str
    tool: str
    args: dict
    speak: str
    result: str
    ask_followup: str | None


def plan_node(state: JarvisState) -> JarvisState:
    history = memory.recent_history()
    decision = planner.plan(state["user_text"], history)
    
    state["tool"] = decision.get("tool", "chat")
    
    # Ensure args is always a valid dictionary before passing to execute
    args = decision.get("args", {})
    if isinstance(args, dict):
        state["args"] = args
    elif isinstance(args, str) and args.strip():
        # Fallback if planner returns a string argument instead of a dict
        state["args"] = {"path": args, "query": args, "name": args, "command": args}
    else:
        state["args"] = {}

    state["speak"] = decision.get("speak", "")
    return state


def execute_node(state: JarvisState) -> JarvisState:
    if state["tool"] == "chat":
        state["result"] = state["speak"] or "Okay."
        return state

    # Ensure state["args"] is guaranteed to be a dict
    tool_args = state["args"] if isinstance(state["args"], dict) else {}
    
    result = execute(state["tool"], tool_args)
    if result == "NEED_COMMIT_MESSAGE":
        state["ask_followup"] = "What should the commit message be?"
        state["result"] = state["ask_followup"]
        return state

    memory.track_command(state["tool"])
    state["result"] = result
    return state


def build_graph():
    graph = StateGraph(JarvisState)
    graph.add_node("plan", plan_node)
    graph.add_node("execute", execute_node)
    graph.set_entry_point("plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", END)
    return graph.compile()


jarvis_graph = build_graph()


def run_task(user_text: str) -> str:
    memory.add_message("user", user_text)
    state: JarvisState = {
        "user_text": user_text,
        "tool": "",
        "args": {},
        "speak": "",
        "result": "",
        "ask_followup": None,
    }
    out = jarvis_graph.invoke(state)
    memory.add_message("assistant", out["result"])
    return out["result"]