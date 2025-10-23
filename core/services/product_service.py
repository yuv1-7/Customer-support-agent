from sqlalchemy.orm import Session
from core.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, session: Session):
        self.session = session
        self.product_repo = ProductRepository(session)
    
    def get_product_info(self, product_id: str) -> dict | None:
        product = self.product_repo.get_by_id(product_id)
        
        if not product:
            return None
        
        return {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "description": product.description,
            "price": float(product.price),
            "stock_quantity": product.stock_quantity,
            "category": product.category,
            "specifications": product.specifications
        }
    
    def search_products(self, category: str = None, keyword: str = None) -> list[dict]:
        products = self.product_repo.search(category=category, keyword=keyword)
        
        return [
            {
                "product_id": p.product_id,
                "product_name": p.product_name,
                "description": p.description,
                "price": float(p.price),
                "stock_quantity": p.stock_quantity
            }
            for p in products
        ]
    
    def get_technical_issues(self, product_id: str = None) -> list[dict]:
        issues = self.product_repo.get_technical_issues(product_id=product_id)
        
        return [
            {
                "issue_id": issue.issue_id,
                "product_id": issue.product_id,
                "issue_title": issue.issue_title,
                "description": issue.description,
                "solution": issue.solution
            }
            for issue in issues
        ]
    
    def check_stock(self, product_id: str, required_quantity: int) -> bool:
        product = self.product_repo.get_by_id(product_id)
        return product and product.stock_quantity >= required_quantity