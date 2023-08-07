import os
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField, SubmitField, DateField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange
from flask_bcrypt import  bcrypt
from datetime import datetime
from flask_restful import Api

from application.config import LocalDevelopmentConfig
from application.database import db

app, api = None, None

def create_app():
    app = Flask(__name__, template_folder="templates")

    print("Staring Local Development")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()

    api=Api(app)
    
    return app, api

app, api = create_app()
# db.create_all()


from application.controllers import *

from application.api import *
api.add_resource(SectionAPI, "/api/sections")
api.add_resource(Section_idAPI, "/api/sections/<int:section_id>")
api.add_resource(ProductAPI, "/api/products")
api.add_resource(Product_idAPI, "/api/products/<int:product_id>")
api.add_resource(CartItemAPI, "/api/cartitems")
api.add_resource(CartItem_idAPI, "/api/cartitems/<int:user_id>", "/api/cartitems/<int:user_id>/<int:item_id>")

if __name__ == "__main__":
    app.run(debug=True)