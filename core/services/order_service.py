from sqlalchemy.orm import Session
from datetime import datetime
import secrets
from core.repositories.order_repository import OrderRepository
from core.repositories.product_repository import ProductRepository
from core.repositories.customer_repository import CustomerRepository

class OrderService:
    def __init__(self, session: Session):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.product_repo = ProductRepository(session)
        self.customer_repo = CustomerRepository(session)
    
    def get_order_details(self, order_id: str) -> dict | None:
        order = self.order_repo.get_by_id(order_id)
        
        if not order:
            return None
        
        items = [
            {
                "product_id": item.product_id,
                "product_name": item.product.product_name,
                "quantity": item.quantity,
                "price": float(item.price),
                "description": item.product.description
            }
            for item in order.items
        ]
        
        return {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "order_date": order.order_date,
            "status": order.status.value,
            "total_amount": float(order.total_amount),
            "shipping_address": order.shipping_address,
            "tracking_number": order.tracking_number,
            "items": items
        }
    
    def get_customer_orders(self, customer_id: str) -> list[dict]:
        orders = self.order_repo.get_by_customer(customer_id)
        
        return [
            {
                "order_id": order.order_id,
                "order_date": order.order_date,
                "status": order.status.value,
                "total_amount": float(order.total_amount)
            }
            for order in orders
        ]
    
    def place_order(self, customer_id: str, items: list[dict], shipping_address: str) -> dict:
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return {"error": "Customer not found"}
        
        total_amount = 0
        validated_items = []
        
        for item in items:
            product = self.product_repo.get_by_id(item['product_id'])
            
            if not product:
                return {"error": f"Product {item['product_id']} not found"}
            
            if product.stock_quantity < item['quantity']:
                return {"error": f"Insufficient stock for {item['product_id']}"}
            
            item_total = float(product.price) * item['quantity']
            validated_items.append({
                "product_id": item['product_id'],
                "quantity": item['quantity'],
                "price": float(product.price)
            })
            total_amount += item_total
        
        order_id = f"ORD{secrets.token_hex(3).upper()}"
        order = self.order_repo.create({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": datetime.now(),
            "status": "pending",
            "total_amount": total_amount,
            "shipping_address": shipping_address
        })
        
        for item in validated_items:
            self.order_repo.add_item({
                "order_id": order_id,
                "product_id": item['product_id'],
                "quantity": item['quantity'],
                "price": item['price']
            })
            
            self.product_repo.update_stock(item['product_id'], -item['quantity'])
        
        self.order_repo.add_log({
            "order_id": order_id,
            "status": "pending",
            "notes": "Order placed via AI agent"
        })
        
        self.session.commit()
        
        return {
            "success": True,
            "order_id": order_id,
            "total_amount": total_amount,
            "status": "pending",
            "message": "Order placed successfully"
        }