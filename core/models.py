from sqlalchemy import Column, String, Text, DECIMAL, Integer, TIMESTAMP, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum

class LoyaltyTier(enum.Enum):
    Bronze = "Bronze"
    Silver = "Silver"
    Gold = "Gold"
    Platinum = "Platinum"

class OrderStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class Severity(enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    registration_date = Column(TIMESTAMP, server_default=func.current_timestamp())
    loyalty_tier = Column(Enum(LoyaltyTier), default=LoyaltyTier.Bronze)
    
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(String(50), primary_key=True)
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    category = Column(String(100))
    specifications = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    order_items = relationship("OrderItem", back_populates="product")
    technical_issues = relationship("TechnicalIssue", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    order_date = Column(TIMESTAMP, server_default=func.current_timestamp())
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    shipping_address = Column(Text)
    tracking_number = Column(String(100))
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    logs = relationship("OrderLog", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class TechnicalIssue(Base):
    __tablename__ = "technical_issues"
    
    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), ForeignKey("products.product_id"))
    issue_title = Column(String(255), nullable=False)
    description = Column(Text)
    solution = Column(Text)
    severity = Column(Enum(Severity), default=Severity.Medium)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    product = relationship("Product", back_populates="technical_issues")

class OrderLog(Base):
    __tablename__ = "order_logs"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False)
    status = Column(String(50))
    notes = Column(Text)
    timestamp = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    order = relationship("Order", back_populates="logs")