from langchain_core.tools import tool
from core.database import get_db_session
from core.services.customer_service import CustomerService
from core.services.product_service import ProductService
from core.services.order_service import OrderService

@tool
def get_customer_info(customer_id: str) -> dict:
    """Get customer information by customer ID.
    Args:
        customer_id: The unique customer identifier (e.g., 'CUST001')
    Returns:
        Customer information including name, email, phone, and loyalty tier
    """
    with get_db_session() as session:
        service = CustomerService(session)
        result = service.get_customer_info(customer_id)
        return result if result else {"error": "Customer not found"}

@tool
def get_product_info(product_id: str) -> dict:
    """Get detailed product information by product ID.
    Args:
        product_id: The unique product identifier (e.g., 'LP-5000')
    Returns:
        Product details including name, description, price, stock, and specifications
    """
    with get_db_session() as session:
        service = ProductService(session)
        result = service.get_product_info(product_id)
        return result if result else {"error": "Product not found"}

@tool
def search_products(category: str = None, keyword: str = None) -> list[dict]:
    """Search for products by category and/or keyword.
    Args:
        category: Product category to filter by (optional)
        keyword: Search keyword to match in product name or description (optional)
    Returns:
        List of products matching the search criteria
    """
    with get_db_session() as session:
        service = ProductService(session)
        return service.search_products(category=category, keyword=keyword)

@tool
def get_technical_issues(product_id: str = None) -> list[dict]:
    """Get known technical issues and their solutions.
    Args:
        product_id: Filter issues by specific product ID (optional)
    Returns:
        List of technical issues with descriptions and solutions
    """
    with get_db_session() as session:
        service = ProductService(session)
        return service.get_technical_issues(product_id=product_id)

@tool
def get_order_details(order_id: str) -> dict:
    """Get detailed information about a specific order.
    Args:
        order_id: The unique order identifier (e.g., 'ORD123ABC')
    Returns:
        Order details including status, items, total amount, and shipping information
    """
    with get_db_session() as session:
        service = OrderService(session)
        result = service.get_order_details(order_id)
        return result if result else {"error": "Order not found"}

@tool
def get_customer_orders(customer_id: str) -> list[dict]:
    """Get all orders for a specific customer.
    Args:
        customer_id: The unique customer identifier (e.g., 'CUST001')
    Returns:
        List of customer's orders with basic information
    """
    with get_db_session() as session:
        service = OrderService(session)
        return service.get_customer_orders(customer_id)

@tool
def place_order(customer_id: str, items: list[dict], shipping_address: str) -> dict:
    """Place a new order for a customer.
    Args:
        customer_id: Customer ID (e.g., 'CUST001')
        items: List of items with product_id and quantity, e.g., [{"product_id": "LP-5000", "quantity": 1}]
        shipping_address: Full shipping address as a string
    Returns:
        Order confirmation with order_id and total amount, or error message
    """
    with get_db_session() as session:
        service = OrderService(session)
        return service.place_order(customer_id, items, shipping_address)

sales_tools = [search_products, get_product_info, get_customer_info, place_order]
tech_support_tools = [get_product_info, get_technical_issues]
order_inquiry_tools = [get_order_details, get_customer_orders]
tools = sales_tools + tech_support_tools + order_inquiry_tools