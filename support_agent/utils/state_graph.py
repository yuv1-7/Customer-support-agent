from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    customer_query: str
    order_id: str | None
    customer_id: str | None
    product_id: str | None
    next_action: str | None