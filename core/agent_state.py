from typing import List, Dict, Any, TypedDict

class AgentState(TypedDict):
    """
    State for the Alpha Scout Agent.
    messages: A list of message dictionaries in OpenAI format:
              {"role": "user" | "assistant" | "system" | "tool", "content": str, "tool_calls": Optional[List], "tool_call_id": Optional[str]}
    """
    messages: List[Dict[str, Any]]