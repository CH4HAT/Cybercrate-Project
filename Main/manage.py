from db import db
from app import app
from models import Customer, Product, Order, ProductOrder, Category
from csv import DictReader
from sqlalchemy.sql import func
import random

def populate_customer_database():
    with app.app_context():
        with open('./data/customers.csv', 'r') as file:
            reader = DictReader(file)
            customers_data = list(reader)

            for data in customers_data:
                customer = Customer(name=data['name'], phone=data['phone'], balance=random.uniform(100.00, 2000.00), email=data['email'], password=data['password'])
                db.session.add(customer)

            db.session.commit()

def populate_product_database():
    with app.app_context():
        with open('./data/products.csv', 'r') as file:
            reader = DictReader(file)
            products_data = list(reader)

            for data in products_data:
                category_name = data['category']
                category = Category.query.filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name, description="N/A")
                    db.session.add(category)
                    db.session.commit()

                product = Product(
                    product=data['name'],
                    price=data['price'],
                    available=random.randint(50, 100),
                    category=category
                )
                db.session.add(product)

            db.session.commit()
def generate_random_order():
    rand_customer = db.session.query(Customer).order_by(func.random()).first()
    order = Order(customer=rand_customer)
    db.session.add(order)
    
    for i in range(2):
        rand_product = db.session.query(Product).order_by(func.random()).first()
        quantity = random.randint(10, 20)
        new_order = ProductOrder(order=order, product=rand_product, quantity=quantity)
        db.session.add(new_order)
    
    db.session.commit()

def create_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        populate_customer_database()
        populate_product_database()

        for _ in range(40):
            generate_random_order()

if __name__ == "__main__":
    create_database()
