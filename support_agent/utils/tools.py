import os
import mysql.connector
from langchain_core.tools import tool
from datetime import datetime
import secrets

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT"))
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@tool
def get_order_details(order_id: str) -> dict:
    """Get order details including items for a specific order ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT order_id, customer_id, order_date, status, 
                   total_amount, shipping_address, tracking_number
            FROM orders
            WHERE order_id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        if order:
            cursor.execute("""
                SELECT oi.product_id, p.product_name, oi.quantity, 
                       oi.price, p.description
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            order['items'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return order if order else {"error": "Order not found"}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_customer_info(customer_id: str) -> dict:
    """Get customer information by customer ID. Use this to verify a customer exists before placing orders."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT customer_id, name, email, phone, 
                   registration_date, loyalty_tier
            FROM customers
            WHERE customer_id = %s
        """, (customer_id,))
        customer = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return customer if customer else {"error": "Customer not found"}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_product_info(product_id: str) -> dict:
    """Get detailed product information by product ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT product_id, product_name, description, price, 
                   stock_quantity, category, specifications
            FROM products
            WHERE product_id = %s
        """, (product_id,))
        product = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return product if product else {"error": "Product not found"}
    except Exception as e:
        return {"error": str(e)}

@tool
def search_products(category: str = None, keyword: str = None) -> list[dict]:
    """Search products by category or keyword. Returns up to 10 products."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT product_id, product_name, description, price, stock_quantity FROM products WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if keyword:
            query += " AND (product_name LIKE %s OR description LIKE %s)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        query += " LIMIT 10"
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return products
    except Exception as e:
        return [{"error": str(e)}]

@tool
def get_customer_orders(customer_id: str) -> list[dict]:
    """Get all orders for a customer. Returns up to 20 most recent orders."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT order_id, order_date, status, total_amount
            FROM orders
            WHERE customer_id = %s
            ORDER BY order_date DESC
            LIMIT 20
        """, (customer_id,))
        orders = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return orders
    except Exception as e:
        return [{"error": str(e)}]

@tool
def get_technical_issues(product_id: str = None) -> list[dict]:
    """Get common technical issues and solutions. Optionally filter by product ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT issue_id, product_id, issue_title, description, solution FROM technical_issues"
        params = []
        
        if product_id:
            query += " WHERE product_id = %s"
            params.append(product_id)
        
        query += " LIMIT 10"
        
        cursor.execute(query, params if params else None)
        issues = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return issues
    except Exception as e:
        return [{"error": str(e)}]

@tool
def place_order(customer_id: str, items: list[dict], shipping_address: str) -> dict:
    """Place an order for an existing customer. Customer must already exist in the system.
    
    Args:
        customer_id: Customer ID (e.g., 'CUST001')
        items: List of dicts with 'product_id' and 'quantity' keys
        shipping_address: Full shipping address
        
    Example items: [{"product_id": "LP-5000", "quantity": 1}, {"product_id": "KB-100", "quantity": 2}]
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT customer_id FROM customers WHERE customer_id = %s", (customer_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return {"error": "Customer not found"}
        
        total_amount = 0
        validated_items = []
        
        for item in items:
            cursor.execute("""
                SELECT product_id, price, stock_quantity 
                FROM products 
                WHERE product_id = %s
            """, (item['product_id'],))
            product = cursor.fetchone()
            
            if not product:
                cursor.close()
                conn.close()
                return {"error": f"Product {item['product_id']} not found"}
            
            if product['stock_quantity'] < item['quantity']:
                cursor.close()
                conn.close()
                return {"error": f"Insufficient stock for {item['product_id']}"}
            
            validated_items.append({
                "product_id": item['product_id'],
                "quantity": item['quantity'],
                "price": float(product['price'])
            })
            total_amount += float(product['price']) * item['quantity']
        
        order_id = f"ORD{secrets.token_hex(3).upper()}"
        
        cursor.execute("""
            INSERT INTO orders (order_id, customer_id, order_date, status, total_amount, shipping_address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, customer_id, datetime.now(), 'pending', total_amount, shipping_address))
        
        for item in validated_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['product_id'], item['quantity'], item['price']))
            
            cursor.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity - %s 
                WHERE product_id = %s
            """, (item['quantity'], item['product_id']))
        
        cursor.execute("""
            INSERT INTO order_logs (order_id, status, notes)
            VALUES (%s, %s, %s)
        """, (order_id, 'pending', 'Order placed via AI agent'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "order_id": order_id,
            "total_amount": total_amount,
            "status": "pending",
            "message": "Order placed successfully"
        }
    except Exception as e:
        return {"error": str(e)}

sales_tools = [search_products, get_product_info, get_customer_info, place_order]
tech_support_tools = [get_product_info, get_technical_issues]
order_inquiry_tools = [get_order_details, get_customer_orders]
tools = sales_tools + tech_support_tools + order_inquiry_tools