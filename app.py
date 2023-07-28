import os
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField, SubmitField, DateField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange
from flask_bcrypt import  bcrypt
from datetime import datetime

from application.config import LocalDevelopmentConfig
from application.database import db

#
app = None

def create_app():
    app = Flask(__name__, template_folder="templates")

    print("Staring Local Development")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    
    return app

app = create_app()
#

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


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
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'))
    section = db.relationship('Sections', backref=db.backref('products', lazy=True))

class CartItem(db.Model):
    __tablename__ = "cartitems"
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    item = db.relationship('Products', backref=db.backref('products', lazy=True))

# db.create_all()
    
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(max=200)], render_kw={"placeholder": "Username"})
    
    role = StringField(validators=[
                    InputRequired(), Length(max=200)], render_kw={"placeholder": "Role"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=200)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = Users.query.filter_by(
            user_name=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
        

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    category = StringField("Category", validators=[])
    name = StringField("Name", validators=[])
    price = FloatField("Price", validators=[NumberRange(min=0, message="Price must be greater than or equal to 0.")])
    manufacture_date = DateField("Manufacture Date")
    expiry_date = DateField("Expiry Date")
    submit = SubmitField("Search")


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/user_register", methods=['GET', 'POST'])
def user_register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        new_user = Users(user_name=form.username.data, role=form.role.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_login'))

    return render_template('user_register.html', form=form)

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(user_name=form.username.data).first()
        if user:
            if bcrypt.checkpw(form.password.data.encode('utf-8'), user.password):
                login_user(user)
                return redirect(url_for('user_dashboard'))
    return render_template('user_login.html', form=form)

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Users.query.filter_by(user_name=form.username.data, role="user").first()
        if admin:
            if bcrypt.checkpw(form.password.data.encode('utf-8'), admin.password):
                login_user(admin)
                return render_template("admin_dashboard.html")
    return render_template('admin_login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/user_dashboard")
@login_required
def user_dashboard():
    sections = Sections.query.all()
    return render_template('user_dashboard.html', sections=sections)

@app.route("/section/<int:section_id>")
@login_required
def products_of_section(section_id):
    products = Products.query.filter_by(section_id=section_id).all()
    return render_template('products_of_section.html', products=products)

@app.route("/add_to_cart/<int:section_id>/<int:item_id>", methods=["POST"])
@login_required
def add_to_cart(section_id,item_id):
    quantity = int(request.form['quantity'])
    cart_item = CartItem(user_id=current_user.user_id, item_id=item_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()
    if request.form.get('source')=='products_of_section':
        return redirect(url_for('products_of_section', section_id=section_id))
    else:
        form = SearchForm()
        products = Products.query.all()
        return redirect(url_for('search_products', products=products, form=form))

@app.route("/view_cart")
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.user_id).all()
    total = 0
    for cart_item in cart_items:
        total += cart_item.item.rate_per_unit*cart_item.quantity
    return render_template('view_cart.html', cart_items=cart_items, total=total)

@app.route("/search_section", methods=["GET", "POST"])
def search_section():
    form=SearchForm()
    if request.method == "POST":
        category = request.form.get("category")
        if category:
            sections = Sections.query.filter_by(section_name=category).all()
    else:
        sections = Sections.query.all()
    return render_template('search_section.html', sections=sections, form=form)

@app.route("/search_product", methods=["GET", "POST"])
def search_products():
    form=SearchForm()
    if request.method == "POST":
        query_params = {}

        category = request.form.get("category")
        if category:
            section = Sections.query.filter_by(section_name=category).one()
            query_params['section_id'] = section.section_id

        price = request.form.get("price")
        if price:
            query_params['rate_per_unit'] = float(price)

        manufacture_date = request.form.get("manufacture_date")
        if manufacture_date:
            query_params['manufacture_date'] = manufacture_date

        expiry_date = request.form.get("expiry_date")
        if expiry_date:
            query_params['expiry_date'] = expiry_date

        product_name = request.form.get("name")
        if product_name:
            query_params['product_name'] = product_name

        products_query = Products.query.filter_by(**query_params)
        products = products_query.all()
    else:
        products = Products.query.all()

    return render_template('search_products.html', products=products, form=form)

@app.route("/view_cart/<int:cart_id>/delete")
def delete_cart_item(cart_id):
  cart_item = CartItem.query.filter_by(cart_id=cart_id).one()
  db.session.delete(cart_item)
  db.session.commit()
  return redirect(url_for('view_cart'))

if __name__ == "__main__":
    app.run(debug=True)