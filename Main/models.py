from decimal import Decimal
from sqlalchemy import Float, Numeric, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import functions as func
from flask_login import UserMixin
from datetime import datetime

from db import db

class Customer(UserMixin, db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), nullable=False, unique=True)
    phone = mapped_column(String(20), nullable=False)
    balance = mapped_column(Numeric, nullable=False, default=0.0)
    email = mapped_column(String(200), nullable=False)
    password = mapped_column(String(200), nullable=False)
    orders = relationship("Order")

class Category(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), nullable=False, unique=True)
    description = mapped_column(String(200), nullable=False, default="N/A")

    products = relationship("Product", back_populates="category")

class Product(db.Model):
    id = mapped_column(Integer, primary_key=True)
    product = mapped_column(String(200), nullable=False, unique=True)
    price = mapped_column(Numeric, nullable=False)
    available = mapped_column(Integer, nullable=False, default=True)
    category_id = mapped_column(Integer, ForeignKey('category.id'))

    category = relationship("Category", back_populates="products")

    products_order = relationship("ProductOrder", back_populates="product")

class Order(db.Model):
    id = mapped_column(Integer, primary_key=True)
    customer_id = mapped_column(Integer, ForeignKey('customer.id'), nullable=False)
    total = mapped_column(Float, nullable=True, default=0.0)
    created = mapped_column(DateTime, nullable=False, default=func.now())
    processed = mapped_column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="orders")
    products_order = relationship("ProductOrder", back_populates="order", cascade="all, delete-orphan")
    def price(self):
        if self.total == 0:
            return format(sum([(u.product.price) * u.quantity for u in self.products_order]), '.2f')
        else:
            return self.total

    def process(self, strategy="adjust"):
        if self.processed is not None:
            return False, "Order already processed"

        if self.customer.balance <= 0:
            return False, "Insufficient funds"
        
        if self.customer.balance < Decimal(self.total):
            return False, "Insufficient funds"

        for order_item in self.products_order:
            if order_item.quantity > order_item.product.available:
                if strategy == "adjust":
                    order_item.quantity = order_item.product.available
                elif strategy == "reject":
                    return False, "Insufficient funds"
                elif strategy == "ignore":
                    order_item.quantity = 0

            order_item.product.available -= order_item.quantity
            self.customer.balance -= int(order_item.product.price * order_item.quantity)
        
        self.processed = datetime.now()
        try:
            db.session.commit()
        except Exception as e:
            return False, f"Failed to process order: {str(e)}"

        return True, self.processed

class ProductOrder(db.Model):
    id = mapped_column(Integer, primary_key=True)
    order_id = mapped_column(Integer, ForeignKey('order.id'), nullable=False)
    product_id = mapped_column(Integer, ForeignKey('product.id'), nullable=False)
    quantity = mapped_column(Integer, nullable=False)

    product = relationship("Product", back_populates="products_order")
    order = relationship("Order", back_populates="products_order")