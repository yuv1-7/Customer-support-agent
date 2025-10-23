from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from agent.state import State
from agent.nodes import (
    orchestrator,
    sales_node,
    tech_support_node,
    order_inquiry_node,
    escalation_node
)
from agent.tools import tools

def route_query(state: State) -> str:
    return state['next_action']

def should_continue(state: State) -> str:
    if state.get('next_action') == 'escalation':
        return 'escalation'
    
    last_msg = state['messages'][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return 'tools'
    return END

builder = StateGraph(State)

builder.add_node('orchestrator', orchestrator)
builder.add_node('sales', sales_node)
builder.add_node('tech_support', tech_support_node)
builder.add_node('order_inquiry', order_inquiry_node)
builder.add_node('escalation', escalation_node)
builder.add_node('tools', ToolNode(tools))

builder.add_edge(START, 'orchestrator')
builder.add_conditional_edges('orchestrator', route_query)
builder.add_conditional_edges('sales', should_continue)
builder.add_conditional_edges('tech_support', should_continue)
builder.add_conditional_edges('order_inquiry', should_continue)
builder.add_conditional_edges('tools', route_query)
builder.add_edge('escalation', END)

graph = builder.compile()