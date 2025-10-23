from sqlalchemy.orm import Session, joinedload
from core.models import Order, OrderItem, OrderLog

class OrderRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, order_id: str) -> Order | None:
        return (
            self.session.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.order_id == order_id)
            .first()
        )
    
    def get_by_customer(self, customer_id: str, limit: int = 20) -> list[Order]:
        return (
            self.session.query(Order)
            .filter(Order.customer_id == customer_id)
            .order_by(Order.order_date.desc())
            .limit(limit)
            .all()
        )
    
    def create(self, order_data: dict) -> Order:
        order = Order(**order_data)
        self.session.add(order)
        self.session.flush()
        return order
    
    def add_item(self, item_data: dict) -> OrderItem:
        item = OrderItem(**item_data)
        self.session.add(item)
        self.session.flush()
        return item
    
    def add_log(self, log_data: dict) -> OrderLog:
        log = OrderLog(**log_data)
        self.session.add(log)
        self.session.flush()
        return log