import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
from utils.state_graph import State
from utils.tools import sales_tools, tech_support_tools, order_inquiry_tools

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
    
    if state.get('messages') and state.get('next_action'):
        return {
            "messages": [HumanMessage(content=query)],
            "next_action": state['next_action']
        }
    
    system_msg = """Categorize customer queries:
- sales: Products, pricing, recommendations, placing orders
- tech_support: Technical issues, troubleshooting
- order_inquiry: Order tracking, status
- escalation: Refunds, cancellations, complaints

Extract IDs if mentioned."""
    
    structured_llm = llm.with_structured_output(RouteDecision)
    result = structured_llm.invoke([
        SystemMessage(content=system_msg),
        HumanMessage(content=query)
    ])
    
    return {
        "messages": [HumanMessage(content=query)],
        "order_id": result.order_id,
        "product_id": result.product_id,
        "customer_id": result.customer_id,
        "next_action": result.category
    }

def sales_node(state: State) -> dict:
    system_msg = """You are a sales support agent. Use available tools to help customers to recommend a product answer any of their queries..

Available Tools:
- search_products: Find products by category/keyword
- get_product_info: Get detailed product information by product_id
- get_customer_info: Verify customer exists and get their details using customer_id
- place_order: Create order for existing customers (requires customer_id, items list, shipping_address)

ORDER PLACEMENT WORKFLOW:
1. If customer wants to order a product (whether you recommended it or they requested it):
   - Ask ONLY for their customer ID if not already provided
   - Use get_customer_info to verify the customer exists
2. Once you have a valid customer_id:
   - Esstablish what product they want to order first. if they dont have anything in mind, give a suggestion as before.
   - If customer hasn't specified shipping address, ask for it
   - If they're ordering a product you recommended earlier in conversation, use that product_id
   - If they mention a product_id, use it directly
   - Call place_order with: customer_id, items list with product_id and quantity, and shipping_address
3. For NEW customers (without customer_id):
   - Respond with: "ESCALATE_TO_HUMAN" and tell them they will be contacted by a representative to assist with account creation.
Remember:
- Do NOT ask for email for placing orders - only customer_id is needed
- If you recommended a product and customer says "I want to order it" or similar, proceed directly with that product id
- Only ask for missing critical details: customer_id (if not provided) and shipping_address (if not provided)
- Default quantity to 1 if not specified
- After placing order successfully, provide order confirmation with order_id

Provide natural, conversational responses. After helping, ask if they need anything else.
If customer is unsatisfied or wants human support, respond with: "ESCALATE_TO_HUMAN" """
    
    messages = [SystemMessage(content=system_msg)] + state['messages']
    response = llm.bind_tools(sales_tools).invoke(messages)
    
    next_action = 'escalation' if response.content and 'ESCALATE_TO_HUMAN' in response.content else 'sales'
    
    return {"messages": [response], "next_action": next_action}

def tech_support_node(state: State) -> dict:
    system_msg = """You are an expert technical support specialist with deep knowledge of computer hardware and software troubleshooting.

AVAILABLE TOOLS:
- get_product_info: Get detailed specifications and information about a product using product_id
- get_technical_issues: Retrieve known issues and verified solutions for products (can filter by product_id)

Provide clear troubleshooting steps one at a time and guide the user toward resolution. Ask if the issue is resolved.
If customer is unsatisfied, wants human support, fails to resolve issue on its own, or issue requires physical repairs, respond with: "ESCALATE_TO_HUMAN" """
    
    messages = [SystemMessage(content=system_msg)] + state['messages']
    response = llm.bind_tools(tech_support_tools).invoke(messages)
    
    next_action = 'escalation' if response.content and 'ESCALATE_TO_HUMAN' in response.content else 'tech_support'
    
    return {"messages": [response], "next_action": next_action}

def order_inquiry_node(state: State) -> dict:
    system_msg = """You are an order support specialist. Use get_order_details and get_customer_orders tools.

Provide clear order updates. Ask if they need more information.
If customer is unsatisfied or wants human support, respond with: "ESCALATE_TO_HUMAN" """
    
    messages = [SystemMessage(content=system_msg)] + state['messages']
    response = llm.bind_tools(order_inquiry_tools).invoke(messages)
    
    next_action = 'escalation' if response.content and 'ESCALATE_TO_HUMAN' in response.content else 'order_inquiry'
    
    return {"messages": [response], "next_action": next_action}

def escalation_node(state: State) -> dict:
    #Can be integrated with ticketing system here
    return {
        "messages": [AIMessage(content="Escalating to human support. A representative will contact you shortly.")]
    }