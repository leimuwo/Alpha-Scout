from typing import Annotated, Sequence, TypedDict, Union
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # messages 存储对话历史，operator.add 表示新消息会追加到列表中而不是覆盖
    messages: Annotated[Sequence[BaseMessage], operator.add]