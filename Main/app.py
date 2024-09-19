from flask import Flask
from auth import login_manager
from pathlib import Path
from db import db
from routes import product, order, endpoint

app = Flask(__name__)

app.config["SECRET_KEY"] = "abc"
login_manager.init_app(app)

app.register_blueprint(product, url_prefix='/api/product')
app.register_blueprint(order, url_prefix='/api/order')
app.register_blueprint(endpoint, url_prefix='/')


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main_database.db"
app.instance_path = Path("data").resolve()

db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, port=8080)