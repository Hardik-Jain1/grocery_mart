from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, PasswordField, SubmitField, DateField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange
from .models import *


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4)], render_kw={"placeholder": "Username"})
    
    role = HiddenField(default="user")

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')
        

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4)], render_kw={"placeholder": "Username"})

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


class AddSectionForm(FlaskForm):
    name = StringField('Section Name', validators=[DataRequired()])
    submit = SubmitField('Save')


class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    manufacture_date = DateField('Manufacture Date')
    expiry_date = DateField('Expiry Date') 
    section = StringField('Section')
    unit = StringField('Unit')
    submit = SubmitField('Save')
    quantity_available = IntegerField('Quantity Available', validators=[DataRequired()])