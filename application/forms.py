from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, PasswordField, SubmitField, DateField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange
from .models import *


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(max=200)], render_kw={"placeholder": "Username"})
    
    role = HiddenField(default="user")
    # role = StringField(validators=[
    #                 InputRequired(), Length(max=200)], render_kw={"placeholder": "Role"})

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


class AddSectionForm(FlaskForm):
    name = StringField('Section Name', validators=[DataRequired()])
    submit = SubmitField('Save')
    no_of_products = IntegerField('No_of_products')


class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    manufacture_date = DateField('Manufacture Date')
    expiry_date = DateField('Expiry Date')
    section = StringField('Section', validators=[])
    unit = StringField('Unit', validators=[])
    submit = SubmitField('Save')