from langchain_core.tools import tool
from core.database import get_db_session
from core.services.customer_service import CustomerService
from core.services.product_service import ProductService
from core.services.order_service import OrderService

@tool
def get_customer_info(customer_id: str) -> dict:
    with get_db_session() as session:
        service = CustomerService(session)
        result = service.get_customer_info(customer_id)
        return result if result else {"error": "Customer not found"}

@tool
def get_product_info(product_id: str) -> dict:
    with get_db_session() as session:
        service = ProductService(session)
        result = service.get_product_info(product_id)
        return result if result else {"error": "Product not found"}

@tool
def search_products(category: str = None, keyword: str = None) -> list[dict]:
    with get_db_session() as session:
        service = ProductService(session)
        return service.search_products(category=category, keyword=keyword)

@tool
def get_technical_issues(product_id: str = None) -> list[dict]:
    with get_db_session() as session:
        service = ProductService(session)
        return service.get_technical_issues(product_id=product_id)

@tool
def get_order_details(order_id: str) -> dict:
    with get_db_session() as session:
        service = OrderService(session)
        result = service.get_order_details(order_id)
        return result if result else {"error": "Order not found"}

@tool
def get_customer_orders(customer_id: str) -> list[dict]:
    with get_db_session() as session:
        service = OrderService(session)
        return service.get_customer_orders(customer_id)

@tool
def place_order(customer_id: str, items: list[dict], shipping_address: str) -> dict:
    """
    Args:
        customer_id: Customer ID (e.g., 'CUST001')
        items: [{"product_id": "LP-5000", "quantity": 1}]
        shipping_address: Full shipping address
    """
    with get_db_session() as session:
        service = OrderService(session)
        return service.place_order(customer_id, items, shipping_address)

sales_tools = [search_products, get_product_info, get_customer_info, place_order]
tech_support_tools = [get_product_info, get_technical_issues]
order_inquiry_tools = [get_order_details, get_customer_orders]
tools = sales_tools + tech_support_tools + order_inquiry_tools