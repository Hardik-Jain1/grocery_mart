from flask import current_app as app
from flask import render_template, redirect, url_for, request, flash
from .database import db
from flask_bcrypt import  bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from .forms import *
from .login_manager import login_manager
 
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Users.query.filter_by(user_name=form.username.data, role="admin").first()
        if admin:
            if bcrypt.checkpw(form.password.data.encode('utf-8'), admin.password):
                login_user(admin)
                return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html', form=form)

@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    sections = Sections.query.all()
    form = AddSectionForm()
    return render_template('admin_dashboard.html', sections=sections, form=form)

# @app.route()

@app.route('/add_section', methods=['GET', 'POST'])
@login_required
def add_section():
    form = AddSectionForm()
    if request.method=="POST":
        section = Sections.query.filter_by(section_name = form.name.data).all()
        if section:
            flash('Section already exit','success')
            return redirect(url_for('add_section'))
        else:    
            section = Sections(section_name=form.name.data)
            if form.no_of_products.data:
                section.number_of_products = form.no_of_products.data
            db.session.add(section)
            db.session.commit()
            flash('New section added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('add_section.html', form=form)

@app.route('/section/<int:section_id>/add_product', methods=['GET', 'POST'])
@login_required
def add_product(section_id):
    form = AddProductForm()
    # form.section.choices = [(section.id, section.name) for section in Sections.query.all()]
    section = Sections.query.filter_by(section_id=section_id).one()
    if form.validate_on_submit():
        product = Products(
            product_name=form.name.data,
            rate_per_unit=form.price.data,
            manufacture_date=form.manufacture_date.data,
            expiry_date=form.expiry_date.data,
            unit=form.unit.data,
            section_id=section_id
        )
        db.session.add(product)
        db.session.commit()
        flash('New product added successfully!', 'success')
        return redirect(url_for('manage_products', section_id=section_id))
    return render_template('add_product.html', form=form, section_id=section_id)

@app.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
@login_required
def edit_section(section_id):
    section = Sections.query.get_or_404(section_id)
    form = AddSectionForm()
    if request.method=="POST":
        section.section_name = form.name.data
        db.session.commit()
        flash('Section updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    form.name.data = section.section_name
    return render_template('edit_section.html', form=form, section=section)

@app.route('/delete_section/<int:section_id>', methods=['GET','POST'])
@login_required
def delete_section(section_id):
    section = Sections.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route("/manage_products/<int:section_id>")
@login_required
def manage_products(section_id):
    products = Products.query.filter_by(section_id=section_id).all()
    section = Sections.query.filter_by(section_id=section_id).one()
    return render_template('manage_products.html', products=products, section=section)

@app.route("/manage_product_details/<int:product_id>")
@login_required
def manage_product_details(product_id):
    product = Products.query.filter_by(product_id=product_id).one()
    return render_template('manage_product_details.html', product=product)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Products.query.get_or_404(product_id)
    form = AddProductForm()
    # form.section.choices = [(section.id, section.name) for section in Sections.query.all()]
    if form.validate_on_submit():
        product.product_name = form.name.data
        product.rate_per_unit = form.price.data
        product.manufacture_date = form.manufacture_date.data
        product.expiry_date = form.expiry_date.data
        product.unit = form.unit.data
        product.section_id = Sections.query.filter_by(section_name=form.section.data).one().section_id
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('manage_product_details', product_id=product_id))
    form.name.data = product.product_name
    form.price.data = product.rate_per_unit
    form.unit.data = product.unit
    form.manufacture_date.data = product.manufacture_date
    form.expiry_date.data = product.expiry_date
    form.section.data = product.section.section_name
    return render_template('edit_product.html', form=form, product=product)

@app.route('/delete_product/<int:product_id>', methods=['GET','POST'])
def delete_product(product_id):
    product = Products.query.get_or_404(product_id)
    section_id = product.section_id
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('manage_products', section_id=section_id))

@app.route("/admin_search_section", methods=["GET", "POST"])
@login_required
def admin_search_section():
    form=SearchForm()
    if request.method == "POST":
        category = request.form.get("category")
        if category:
            sections = Sections.query.filter_by(section_name=category).all()
    else:
        sections = Sections.query.all()
    return render_template('admin_search_section.html', sections=sections, form=form)

@app.route("/admin_search_product", methods=["GET", "POST"])
@login_required
def admin_search_product():
    form=SearchForm()
    if request.method == "POST":
        query_params = {}

        product_name = request.form.get("name")
        if product_name:
            query_params['product_name'] = product_name

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

        products_query = Products.query.filter_by(**query_params)
        products = products_query.all()
    else:
        products = Products.query.all()

    return render_template('admin_search_product.html', products=products, form=form)



















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

@app.route("/user_dashboard")
@login_required
def user_dashboard():
    sections = Sections.query.all()
    return render_template('user_dashboard.html', sections=sections)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/section/<int:section_id>")
@login_required
def products_of_section(section_id):
    products = Products.query.filter_by(section_id=section_id).all()
    section_name = Sections.query.filter_by(section_id=section_id).one().section_name
    return render_template('products_of_section.html', products=products, section_name=section_name)

@app.route("/section/<int:section_id>/<int:product_id>")
@login_required
def product_details(section_id, product_id):
    product = Products.query.filter_by(section_id=section_id, product_id=product_id).one()
    return render_template('product_details.html', product=product)

@app.route("/section/<int:section_id>/<int:product_id>/buy")
@login_required
def buy(section_id, product_id):
    product = Products.query.filter_by(section_id=section_id, product_id=product_id).one()
    return render_template('buy.html', product=product)

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
@login_required
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
@login_required
def search_product():
    form=SearchForm()
    if request.method == "POST":
        query_params = {}

        product_name = request.form.get("name")
        if product_name:
            query_params['product_name'] = product_name

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

        products_query = Products.query.filter_by(**query_params)
        products = products_query.all()
    else:
        products = Products.query.all()

    return render_template('search_product.html', products=products, form=form)

@app.route("/view_cart/<int:cart_id>/delete")
@login_required
def delete_cart_item(cart_id):
  cart_item = CartItem.query.filter_by(cart_id=cart_id).one()
  db.session.delete(cart_item)
  db.session.commit()
  return redirect(url_for('view_cart'))