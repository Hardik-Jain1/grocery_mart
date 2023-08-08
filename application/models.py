from .database import db
from flask_login import UserMixin

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200), nullable=False)

    def get_id(self):
        return str(self.user_id) 

class Sections(db.Model):
    __tablename__ = "sections"
    section_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_name = db.Column(db.String(200), nullable=False)
    number_of_products = db.Column(db.Integer)

class Products(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(200), nullable=False)
    manufacture_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    rate_per_unit = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(200), nullable=False, default='Rs')
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id', onupdate='CASCADE'))
    section = db.relationship('Sections', backref=db.backref('products', lazy=True))
    quantity_available = db.Column(db.Integer, db.CheckConstraint('quantity_available >= 0', name='check_min_quantity') , nullable=False)


class CartItem(db.Model):
    __tablename__ = "cartitems"
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', onupdate='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('products.product_id', onupdate='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    item = db.relationship('Products', backref=db.backref('products', lazy=True))
