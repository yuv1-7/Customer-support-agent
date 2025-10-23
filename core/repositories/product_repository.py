from sqlalchemy.orm import Session
from sqlalchemy import or_
from core.models import Product, TechnicalIssue

class ProductRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, product_id: str) -> Product | None:
        return self.session.query(Product).filter(Product.product_id == product_id).first()
    
    def search(self, category: str = None, keyword: str = None, limit: int = 10) -> list[Product]:
        query = self.session.query(Product)
        
        if category:
            query = query.filter(Product.category == category)
        
        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.filter(
                or_(
                    Product.product_name.like(search_pattern),
                    Product.description.like(search_pattern)
                )
            )
        
        return query.limit(limit).all()
    
    def update_stock(self, product_id: str, quantity_change: int):
        product = self.get_by_id(product_id)
        if product:
            product.stock_quantity += quantity_change
            self.session.flush()
    
    def get_technical_issues(self, product_id: str = None, limit: int = 10) -> list[TechnicalIssue]:
        query = self.session.query(TechnicalIssue)
        
        if product_id:
            query = query.filter(TechnicalIssue.product_id == product_id)
        
        return query.limit(limit).all()