from sqlalchemy.orm import Session
from core.repositories.customer_repository import CustomerRepository

class CustomerService:
    def __init__(self, session: Session):
        self.session = session
        self.customer_repo = CustomerRepository(session)
    
    def get_customer_info(self, customer_id: str) -> dict | None:
        customer = self.customer_repo.get_by_id(customer_id)
        
        if not customer:
            return None
        
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "registration_date": customer.registration_date,
            "loyalty_tier": customer.loyalty_tier.value
        }
    
    def customer_exists(self, customer_id: str) -> bool:
        return self.customer_repo.get_by_id(customer_id) is not None