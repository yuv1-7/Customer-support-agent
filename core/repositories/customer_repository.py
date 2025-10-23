from sqlalchemy.orm import Session
from core.models import Customer

class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, customer_id: str) -> Customer | None:
        return self.session.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    def get_by_email(self, email: str) -> Customer | None:
        return self.session.query(Customer).filter(Customer.email == email).first()
    
    def create(self, customer_data: dict) -> Customer:
        customer = Customer(**customer_data)
        self.session.add(customer)
        self.session.flush()
        return customer