import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
from agent.state import State
from agent.tools import sales_tools, tech_support_tools, order_inquiry_tools

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

class RouteDecision(BaseModel):
    category: str = Field(description="One of: sales, tech_support, order_inquiry, escalation")
    order_id: str | None = None
    product_id: str | None = None
    customer_id: str | None = None

def orchestrator(state: State) -> dict:
    query = state['customer_query']
    messages = state.get('messages', [])
    
    if messages and state.get('next_action') and state['next_action'] != 'escalation':
        return {}
    
    system_msg = """Categorize customer queries based on the CURRENT query and conversation context:
- sales: Products, pricing, recommendations, placing orders
- tech_support: Technical issues, troubleshooting
- order_inquiry: Order tracking, status
- escalation: Refunds, cancellations, complaints

Extract IDs if mentioned. Consider the conversation history to maintain context."""
    
    structured_llm = llm.with_structured_output(RouteDecision)
    
    context_messages = [SystemMessage(content=system_msg)]
    
    if messages:
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        context_messages.extend(recent_messages)
    
    context_messages.append(HumanMessage(content=query))
    
    result = structured_llm.invoke(context_messages)
    
    return {
        "messages": [HumanMessage(content=query)],
        "order_id": result.order_id or state.get('order_id'),
        "product_id": result.product_id or state.get('product_id'),
        "customer_id": result.customer_id or state.get('customer_id'),
        "next_action": result.category
    }

def sales_node(state: State) -> dict:
    system_msg = """You are a sales support agent. Use available tools to help customers recommend products and answer queries.
                    Review conversation history carefully to understand context.

CONTEXT: Map informal references to products discussed earlier. Don't ask for info already provided.

Available Tools:
- search_products: Find products by category/keyword
- get_product_info: Get detailed product information by product_id
- get_customer_info: Verify customer exists using customer_id
- place_order: Create order (requires customer_id, items list, shipping_address)

ORDER PLACEMENT WORKFLOW:
1. Customer wants to order:
   - Ask for customer ID if not provided
   - Use get_customer_info to verify customer exists
2. Once customer_id verified:
   - Establish what product they want
   - If no shipping address, ask for it
   - Call place_order with customer_id, items, shipping_address
3. NEW customers without customer_id:
   - Respond with "ESCALATE_TO_HUMAN"

Review the conversation history to understand context. If customer has already provided information, use it rather than asking again.

Remember:
- Only ask for customer_id and shipping_address
- Default quantity to 1 if not specified
- Provide order confirmation with order_id after success

If customer is unsatisfied or wants human support, respond exactly with: "ESCALATE_TO_HUMAN" """
    
    messages = [SystemMessage(content=system_msg)] + state['messages']
    response = llm.bind_tools(sales_tools).invoke(messages)
    
    next_action = 'escalation' if response.content and 'ESCALATE_TO_HUMAN' in response.content else 'sales'
    
    return {"messages": [response], "next_action": next_action}

def tech_support_node(state: State) -> dict:
    system_msg = """You are a technical support specialist.

AVAILABLE TOOLS:
- get_product_info: Get product specifications using product_id
- get_technical_issues: Get known issues and solutions (filter by product_id)

Review the conversation history to understand the full context of the technical issue. Reference previous troubleshooting steps to avoid repeating them.

Provide clear troubleshooting steps. Ask if issue is resolved.
If customer is unsatisfied, wants human support, or issue requires physical repairs, respond exactly with: "ESCALATE_TO_HUMAN" """
    
    messages = [SystemMessage(content=system_msg)] + state['messages']
    response = llm.bind_tools(tech_support_tools).invoke(messages)
    
    next_action = 'escalation' if response.content and 'ESCALATE_TO_HUMAN' in response.content else 'tech_support'
    
    return {"messages": [response], "next_action": next_action}

def order_inquiry_node(state: State) -> dict:
    system_msg = """You are an order support specialist. Use get_order_details and get_customer_orders tools.

Review the conversation history to understand what information has already been provided. Reference the order details already discussed.

Provide clear order updates. Ask if they need more information.
If customer is unsatisfied or wants human support, respond exactly with: "ESCALATE_TO_HUMAN" """
    
    messages = [SystemMessage(content=system_msg)] + state['messages']
    response = llm.bind_tools(order_inquiry_tools).invoke(messages)
    
    next_action = 'escalation' if response.content and 'ESCALATE_TO_HUMAN' in response.content else 'order_inquiry'
    
    return {"messages": [response], "next_action": next_action}

def escalation_node(state: State) -> dict:
    return {
        "messages": [AIMessage(content="Escalating to human support. A representative will contact you shortly.")]
    }